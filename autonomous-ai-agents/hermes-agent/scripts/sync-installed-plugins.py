#!/usr/bin/env python3
"""Sync the installed-plugins reference doc from the live Hermes environment.

Reads plugin metadata from the local Hermes installation and regenerates
``references/installed-plugins.md``. In ``--check`` mode, compares the
generated content against the committed file to detect drift — this is the
plugin/drift counterpart to ``gen-references-index.py --check``.

Data sources (all read at runtime from the live environment):
  * ``hermes plugins list --json --no-bundled``  → name, version, catalog,
    status, description, short revision.
  * ``$HERMES_HOME/plugins/.install-metadata.json`` → full source URL,
    full pinned revision, branch, install type.
  * ``$HERMES_HOME/config.yaml`` → ``plugins.enabled`` list (ground truth
    for enabled/disabled status).
  * ``hermes tools list`` → enabled/disabled toolsets, mapped to plugins.

Usage:
    python3 hermes-agent/scripts/sync-installed-plugins.py            # regenerate
    python3 hermes-agent/scripts/sync-installed-plugins.py --check    # verify drift

Exit codes:
    0 — doc matches live state (or gate was skipped — see below)
    1 — drift detected (doc does not match live state)
    2 — scan produced fewer plugins than the floor (treated as a scan failure)

CI / no-local-install behavior:
    When no local Hermes installation is found (no ``$HERMES_HOME`` directory
    with a ``config.yaml``), the script prints ``skipped: …`` and exits 0.
    This is a deliberately local-only gate — it only catches drift when run
    on a machine that actually has Hermes installed. In CI it is a no-op that
    keeps the pipeline green so the reference doc doesn't rot in the repo.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# ── Path resolution ─────────────────────────────────────────────────────────
SCRIPT = Path(__file__).resolve()
# scripts/ → hermes-agent/skill → hermes-agent/cat → repo-root
SKILL_DIR = SCRIPT.parents[1]
REPO = SCRIPT.parents[3]
REF_DOC = SKILL_DIR / "references" / "installed-plugins.md"

# ── Environment guard ─────────────────────────────────────────────────────
if sys.version_info < (3, 8):
    raise SystemExit(
        "[FATAL] sync-installed-plugins.py needs Python 3.8+, got "
        + sys.version.split()[0]
    )
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

MIN_PLUGINS = 1  # write-guard floor — a scan returning 0 plugins is a failed scan

# ── Static metadata (update by hand only when a new plugin is installed) ───
# These fields cannot be read from files alone and are stable between releases.
PLUGIN_TYPE = {
    "agent-analytics": "dashboard",
    "bot-forge": "tool",
    "hermes-ledgerline": "dashboard",
    "hermes-memory-ui": "dashboard",
    "icarus": "tool",
    "job-search": "tool",
    "memory-wiki": "dashboard",
    "mnemosyne-dashboard": "tool",
    "web-search-plus": "tool",
    "yantrikdb": "tool",
}

# Map from `hermes tools list` plugin toolset name → plugin name.
# Built-in toolsets that are sourced from a plugin (e.g. `memory` ← yantrikdb)
# are also listed here so the script can attribute them correctly.
TOOLSET_TO_PLUGIN = {
    "bot_forge": "bot-forge",
    "fabric": "icarus",
    "mnemosyne-dashboard": "mnemosyne-dashboard",
    "web-search-plus": "web-search-plus",
    "memory": "yantrikdb",
    "a2a": "a2a",
}

# Human-readable tool summaries (from `hermes tools` interactive output —
# captured here because the interactive mode cannot be scripted).
TOOL_GROUP_INFO = {
    "web": ("Web Search & Scraping", "web_search, web_extract"),
    "browser": ("Browser Automation", "navigate, click, type, scroll"),
    "terminal": ("Terminal & Processes", "terminal, process"),
    "file": ("File Operations", "read, write, patch, search"),
    "code_execution": ("Code Execution", "execute_code"),
    "vision": ("Vision / Image Analysis", "vision_analyze"),
    "image_gen": ("Image Generation", "image_generate"),
    "tts": ("Text-to-Speech", "text_to_speech"),
    "skills": ("Skills", "skill_view, skill_manage, skills_list"),
    "todo": ("Task Planning", "todo_list"),
    "memory": ("Memory", "yantrikdb_remember, yantrikdb_recall, yantrikdb_forget, "
                      "yantrikdb_conflicts, yantrikdb_relate, yantrikdb_tasks, "
                      "yantrikdb_resolve_conflict"),
    "session_search": ("Session Search", "session_search"),
    "connections": ("Connections", "connections"),
    "clarify": ("Clarifying Questions", "clarify"),
    "delegation": ("Task Delegation", "delegate_task"),
    "cronjob": ("Cron Jobs", "cronjob_manage (create/list/update/pause/resume/run)"),
    "computer_use": ("Computer Use", "computer_use (list_apps, capture, click, type, ...)"),
    "bot_forge": ("Bot Forge", "agent that builds complete working bots"),
    "fabric": ("Fabric", "self-memory + replacement model tools"),
    "mnemosyne-dashboard": ("Mnemosyne-Dashboard", "memory browsing & visualization"),
    "web-search-plus": ("Web-Search-Plus", "multi-provider search, URL extraction, reports"),
    "a2a": ("A2A", "Agent-to-Agent protocol"),
    "video": ("Video Analysis", "(requires video-capable model)"),
    "video_gen": ("Video Generation", "(not enabled)"),
    "x_search": ("X (Twitter) Search", "(requires xAI OAuth or XAI_API_KEY)"),
    "stt": ("Speech-to-Text", "(not enabled)"),
    "kanban": ("Kanban", "(opt-in task board)"),
    "context_engine": ("Context Engine", "(no active context engine)"),
    "homeassistant": ("Home Assistant", "(no API key)"),
    "spotify": ("Spotify", "(not configured)"),
    "yuanbao": ("Yuanbao", "(not configured)"),
    "job_search": ("Job Search", "(agent-data/job-search)"),
    "ledgerline": ("Ledgerline", "(session cost inspection)"),
}


# Static metadata for standalone desktop plugins — those in desktop-plugins/
# that have NO .hermes-package.json (i.e. not bundled with a Python plugin).
# These are invisible to `hermes plugins list` because they have no Python
# component; their metadata can only be read from disk. Update this dict when
# a new standalone desktop plugin is installed.
DESKTOP_PLUGIN_INFO = {
    "hermes-home-dashboard": (
        "bundled",
        "Built-in Hermes Desktop home dashboard: grid-layout workspace with "
        "ascii art, clock, gateway status, session list, cron jobs, system "
        "stats, and analytics.",
    ),
}


def find_hermes_dir():
    """Locate the local Hermes installation directory."""
    # $HERMES_HOME takes priority, then LOCALAPPDATA/hermes (Windows), then ~/.hermes
    hermes_home = os.environ.get("HERMES_HOME")
    if hermes_home:
        p = Path(hermes_home)
        if (p / "config.yaml").exists():
            return p
    la = os.environ.get("LOCALAPPDATA")
    if la:
        p = Path(la) / "hermes"
        if (p / "config.yaml").exists():
            return p
    home = os.environ.get("HOME") or str(Path.home())
    p = Path(home) / ".hermes"
    if (p / "config.yaml").exists():
        return p
    return None


def run_hermes_cmd(args, timeout=30):
    """Run a hermes CLI command, return (stdout_str, ok)."""
    try:
        proc = subprocess.run(["hermes"] + args,
                              capture_output=True, text=True, timeout=timeout)
        if proc.returncode != 0:
            return "", False
        return proc.stdout, True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "", False


def get_plugins_json():
    """Return parsed output of `hermes plugins list --json --no-bundled`."""
    stdout, ok = run_hermes_cmd(["plugins", "list", "--json", "--no-bundled"])
    if not ok:
        return None
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return None


def get_install_metadata(hermes_dir):
    """Read .install-metadata.json for full source URLs and revisions."""
    path = hermes_dir / "plugins" / ".install-metadata.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def get_config_enabled(hermes_dir):
    """Read config.yaml for the plugins.enabled list."""
    path = hermes_dir / "config.yaml"
    if not path.exists():
        return []
    try:
        import yaml
        cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
        return cfg.get("plugins", {}).get("enabled", [])
    except Exception:
        return []


def get_standalone_desktop_plugins(hermes_dir):
    """Scan desktop-plugins/ for standalone desktop plugins.

    A desktop plugin is *standalone* if its dir has no .hermes-package.json
    (i.e. it's not bundled with a Python plugin that already appears in the
    main catalog above). Standalone plugins are invisible to
    `hermes plugins list` because they have no Python component.

    Returns a list of dicts with keys: name, source, description, plugin_js_size.
    """
    dp_dir = hermes_dir / "desktop-plugins"
    if not dp_dir.is_dir():
        return []
    result = []
    for entry in sorted(dp_dir.iterdir()):
        if not entry.is_dir():
            continue
        # Bundled desktop plugins carry .hermes-package.json and are already
        # covered by their parent Python plugin entry in the main catalog.
        if (entry / ".hermes-package.json").exists():
            continue
        plugin_js = entry / "plugin.js"
        if not plugin_js.exists():
            continue
        name = entry.name
        info = DESKTOP_PLUGIN_INFO.get(name)
        if info:
            source, description = info
        else:
            source = "unknown"
            description = (
                f"Standalone desktop plugin (plugin.js: "
                f"{plugin_js.stat().st_size} bytes, no manifest)"
            )
        result.append({
            "name": name,
            "source": source,
            "description": description,
            "plugin_js_size": plugin_js.stat().st_size,
        })
    return result


def parse_tools_list(stdout):
    """Parse `hermes tools list` output into (enabled, disabled) lists of toolsets.

    Returns lists of (toolset_name, display_name, description) tuples.
    """
    enabled = []
    disabled = []
    section = None
    for line in stdout.splitlines():
        line = line.rstrip()
        m = re.match(
            r"\s*[✓✗]\s+(enabled|disabled)\s+(\S+)\s*(.+)", line
        )
        if m:
            status, name, rest = m.group(1), m.group(2), m.group(3)
            # rest contains emoji + display name; split off the emoji
            parts = rest.split(None, 1)
            display = parts[1] if len(parts) > 1 else name
            if status == "enabled":
                enabled.append((name, display))
            else:
                disabled.append((name, display))
    return enabled, disabled


def generate_doc(plugins, metadata, config_enabled, tools_enabled, tools_disabled,
                 desktop_plugins=None):
    """Build the reference doc content from live data (deterministic, no timestamps)."""
    # --- Build plugin rows from live data ---
    rows = []
    for p in sorted(plugins, key=lambda p: p["name"]):
        name = p["name"]
        version = p.get("version", "unknown")
        source_field = p.get("source", "")
        m = re.match(r"catalog:(\w+)@([0-9a-f]+)", source_field)
        catalog = m.group(1) if m else "unknown"
        rev_short = m.group(2)[:8] if m else ""

        meta = metadata.get(name, {})
        full_rev = meta.get("revision", "")
        source_url = meta.get("source", "")

        status = "enabled" if name in config_enabled else "disabled"
        ptype = PLUGIN_TYPE.get(name, "unknown")

        rows.append({
            "name": name,
            "version": version,
            "catalog": catalog,
            "status": status,
            "source_short": source_url.replace("https://github.com/", "")
                                   .replace("#catalog", "")
                                   .replace("https://", ""),
            "source_full": source_url.replace("#catalog", ""),
            "rev_short": rev_short,
            "rev_full": full_rev,
            "type": ptype,
            "description": p.get("description", "(no description available)"),
        })

    # --- Summary stats ---
    total = len(rows)
    enabled = sum(1 for r in rows if r["status"] == "enabled")
    disabled = total - enabled
    dashboard = sum(1 for r in rows if r["type"] == "dashboard")
    tool_plugins = sum(1 for r in rows if r["type"] == "tool")
    community = sum(1 for r in rows if r["catalog"] == "community")
    official = sum(1 for r in rows if r["catalog"] == "official")

    # --- Tool config summary ---
    total_typesets = len(tools_enabled) + len(tools_disabled)
    enabled_tools = len(tools_enabled)
    disabled_tools = len(tools_disabled)

    # --- Build the doc ---
    L = []
    L.append("# Installed Plugins — Live Environment Catalog")
    L.append("")
    L.append("> **Machine-generated** by `scripts/sync-installed-plugins.py` — do not edit by hand.")
    L.append("> Regenerate: `python3 hermes-agent/scripts/sync-installed-plugins.py`")
    L.append("> Check drift: `python3 hermes-agent/scripts/sync-installed-plugins.py --check`")
    L.append("")
    L.append("## Summary")
    L.append("")
    L.append("| Metric | Count |")
    L.append("|--------|-------|")
    L.append(f"| Total plugins installed | {total} |")
    L.append(f"| Enabled | {enabled} |")
    L.append(f"| Disabled | {disabled} |")
    L.append(f"| Dashboard/UI-only plugins | {dashboard} |")
    L.append(f"| Tool-providing plugins | {tool_plugins} |")
    L.append(f"| Community catalog plugins | {community} |")
    L.append(f"| Official catalog plugins | {official} |")
    L.append(f"| Standalone desktop plugins | {len(desktop_plugins) if desktop_plugins else 0} |")
    L.append(f"| Total toolsets | {total_typesets} |")
    L.append(f"| Toolsets enabled | {enabled_tools} |")
    L.append(f"| Toolsets disabled | {disabled_tools} |")
    L.append("")
    L.append("## Plugin Catalog")
    L.append("")
    L.append("| # | Plugin | Version | Catalog | Status | Source | Revision | Type |")
    L.append("|---|--------|---------|---------|--------|--------|----------|------|")
    for i, r in enumerate(rows, 1):
        L.append(
            f"| {i} | {r['name']} | {r['version']} | {r['catalog']} | "
            f"{r['status']} | {r['source_short']} | {r['rev_short']} | {r['type']} |"
        )
    L.append("")
    L.append("## Tool Configuration")
    L.append("")
    L.append(f"> Auto-generated from `hermes tools list` — {enabled_tools}/{total_typesets} toolsets enabled.")
    L.append("")
    L.append("### Enabled toolsets")
    L.append("")
    L.append("| Toolset | Display name | Tools | Plugin source |")
    L.append("|---------|--------------|-------|---------------|")
    for name, display in tools_enabled:
        info = TOOL_GROUP_INFO.get(name, (display, ""))
        _, tools_desc = info
        plugin_src = TOOLSET_TO_PLUGIN.get(name, "built-in")
        if plugin_src == "built-in":
            plugin_src = "built-in"
        L.append(f"| `{name}` | {display} | {tools_desc} | {plugin_src} |")
    L.append("")
    if tools_disabled:
        L.append("### Disabled toolsets")
        L.append("")
        L.append("| Toolset | Display name | Reason | Plugin source |")
        L.append("|---------|--------------|--------|---------------|")
        for name, display in tools_disabled:
            info = TOOL_GROUP_INFO.get(name, (display, ""))
            _, tools_desc = info
            plugin_src = TOOLSET_TO_PLUGIN.get(name, "")
            if not plugin_src:
                plugin_src = "built-in"
            reason = tools_desc if tools_desc else "(not configured)"
            L.append(f"| `{name}` | {display} | {reason} | {plugin_src} |")
        L.append("")
    L.append("## Per-Plugin Details")
    L.append("")
    for i, r in enumerate(rows, 1):
        L.append(f"### {i}. `{r['name']}`")
        L.append("")
        L.append(f"- **Version**: {r['version']}")
        L.append(f"- **Catalog**: {r['catalog']}")
        L.append(f"- **Status**: {r['status']}")
        L.append(f"- **Install source**: {r['source_full']}")
        if r['rev_full']:
            L.append(f"- **Revision**: `{r['rev_short']}` (`{r['rev_full']}`) — pinned")
        else:
            L.append(f"- **Revision**: `{r['rev_short']}` — pinned (full hash not in metadata)")
        ptype_display = "Dashboard/UI panel" if r['type'] == 'dashboard' else "Agent tool-providing"
        L.append(f"- **Type**: {ptype_display}")
        # Find toolsets this plugin provides
        plugin_toolsets = []
        for ts_name, ts_display in tools_enabled + tools_disabled:
            if TOOLSET_TO_PLUGIN.get(ts_name) == r['name']:
                info = TOOL_GROUP_INFO.get(ts_name, (ts_display, ""))
                _, tools_desc = info
                plugin_toolsets.append(f"`{ts_name}` ({ts_display}) — {tools_desc}")
        if plugin_toolsets:
            L.append(f"- **Tools**: {', '.join(plugin_toolsets)}")
        elif r['type'] == 'dashboard':
            L.append("- **Tools**: None (dashboard panel only)")
        else:
            L.append("- **Tools**: Not reflected in `hermes tools list` (may register via agent tool discovery)")
        L.append(f"- **Description**: {r['description']}")
        L.append("")
    if desktop_plugins:
        L.append("## Standalone Desktop Plugins")
        L.append("")
        L.append("> Plugins in `desktop-plugins/` without a `.hermes-package.json` — these are")
        L.append("> not visible to `hermes plugins list` (no Python component) and must be scanned")
        L.append("> from disk directly.")
        L.append("")
        L.append("| Plugin | Source | plugin.js size | Description |")
        L.append("|--------|--------|----------------|-------------|")
        for dp in desktop_plugins:
            size = f"{dp['plugin_js_size']} bytes"
            L.append(f"| `{dp['name']}` | {dp['source']} | {size} | {dp['description']} |")
        L.append("")
    L.append("## Sync")
    L.append("")
    L.append("This reference is machine-generated from the live Hermes environment:")
    L.append("")
    L.append(f"- `python3 hermes-agent/scripts/sync-installed-plugins.py` — regenerate from live env")
    L.append(f"- `python3 hermes-agent/scripts/sync-installed-plugins.py --check` — verify no drift")
    L.append(f"- Data sources: `hermes plugins list --json`, `.install-metadata.json`, `config.yaml`, `hermes tools list`, `desktop-plugins/` dir scan")
    L.append(f"- CI note: when no local Hermes installation is found, the gate skips gracefully (exit 0)")
    L.append("")

    return "\n".join(L) + "\n"


def main():
    check_mode = "--check" in sys.argv[1:]

    hermes_dir = find_hermes_dir()
    if hermes_dir is None:
        print("skipped: no local Hermes installation found "
              "($HERMES_HOME / $LOCALAPPDATA/hermes / ~/.hermes) — local-only gate")
        return 0

    # 1. Plugin data from `hermes plugins list --json`
    plugins = get_plugins_json()
    if plugins is None:
        print("skipped: `hermes plugins list --json` unavailable — "
              "hermes CLI not found on PATH")
        return 0
    if len(plugins) < MIN_PLUGINS:
        print(f"[FATAL] sync-installed-plugins: scan produced only "
              f"{len(plugins)} plugins (floor {MIN_PLUGINS}). "
              f"Refusing to overwrite {REF_DOC.name} — this is a failed scan.")
        return 2

    # 2. Install metadata (source URLs, full revisions)
    metadata = get_install_metadata(hermes_dir)

    # 3. Config-enabled plugins
    config_enabled = get_config_enabled(hermes_dir)

    # 4. Tool configuration from `hermes tools list`
    tools_stdout, ok = run_hermes_cmd(["tools", "list"])
    if ok and tools_stdout:
        tools_enabled, tools_disabled = parse_tools_list(tools_stdout)
    else:
        # Fall back: empty lists if `hermes tools list` is not parseable
        tools_enabled, tools_disabled = [], []
        print("WARNING: `hermes tools list` not available — "
              "tool configuration section will be empty")

    # 4b. Standalone desktop plugins (not visible via hermes CLI)
    desktop_plugins = get_standalone_desktop_plugins(hermes_dir)

    # 5. Generate doc
    content = generate_doc(plugins, metadata, config_enabled,
                           tools_enabled, tools_disabled, desktop_plugins)

    # 6. Write or check
    if check_mode:
        if REF_DOC.exists():
            current = REF_DOC.read_text(encoding="utf-8")
            if current != content:
                cur_lines, new_lines = current.splitlines(), content.splitlines()
                print(f"[DRIFT] {REF_DOC.name} is stale: "
                      f"{len(cur_lines)} lines on disk vs {len(new_lines)} generated")
                for i, (a, b) in enumerate(zip(cur_lines, new_lines)):
                    if a != b:
                        print(f"        first difference at line {i + 1}:")
                        print(f"          on disk   : {a[:120]}")
                        print(f"          generated : {b[:120]}")
                        break
                return 1
            print(f"[OK] {REF_DOC.name} is up to date "
                  f"({len(plugins)} plugins, {len(desktop_plugins)} standalone desktop)")
            return 0
        else:
            print(f"[DRIFT] {REF_DOC.name} does not exist (would be created)")
            return 1
    else:
        REF_DOC.parent.mkdir(parents=True, exist_ok=True)
        REF_DOC.write_text(content, encoding="utf-8")
        print(f"Wrote {len(plugins)} plugins to {REF_DOC} "
              f"({len(tools_enabled)} enabled toolsets, "
              f"{len(tools_disabled)} disabled, "
              f"{len(desktop_plugins)} standalone desktop plugins)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
