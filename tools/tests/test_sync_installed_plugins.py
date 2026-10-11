"""sync-installed-plugins.py: skips are exit 77, unreadable live state is exit 2.

Before round-256 a Hermes install whose CLI failed printed 'skipped' and exited 0 (verify-all
showed PASS), a failing `hermes tools list` wrote an empty tool section, and unreadable
config/metadata silently became empty lists.
"""

import json
import types

import pytest

SIP = "autonomous-ai-agents/hermes-agent/scripts/sync-installed-plugins.py"

PLUGINS = [{"name": "bot-forge", "version": "1.0.0", "description": "d", "enabled": True}]
TOOLS_OUT = "  ✓ enabled  web  🌐 Web tools\n  ✗ disabled  tts  🔊 Speech\n"


@pytest.fixture
def env(load, tmp_path, monkeypatch):
    """The module with a fake Hermes home, a temp ref doc and a scriptable `hermes` CLI."""
    sip = load(SIP)
    home = tmp_path / "hermes"
    (home / "plugins").mkdir(parents=True)
    (home / "config.yaml").write_text("plugins:\n  enabled: [bot-forge]\n", encoding="utf-8")
    monkeypatch.setattr(sip, "find_hermes_dir", lambda: home)
    monkeypatch.setattr(sip, "REF_DOC", tmp_path / "installed-plugins.md")
    cli = {
        ("plugins", "list", "--json", "--no-bundled"): (0, json.dumps(PLUGINS)),
        ("tools", "list"): (0, TOOLS_OUT),
    }

    def fake_run(argv, **kw):
        if argv[0] != "hermes":
            raise AssertionError(f"unexpected command {argv}")
        rc, out = cli[tuple(argv[1:])]
        if rc is None:
            raise FileNotFoundError("hermes")
        return types.SimpleNamespace(
            returncode=rc, stdout=out if rc == 0 else "", stderr="" if rc == 0 else out
        )

    monkeypatch.setattr(sip.subprocess, "run", fake_run)
    return types.SimpleNamespace(sip=sip, home=home, cli=cli, monkeypatch=monkeypatch)


def run_main(env, *args):
    env.monkeypatch.setattr(env.sip.sys, "argv", ["sync-installed-plugins.py", *args])
    return env.sip.main()


def test_write_then_check_is_clean(env):
    assert run_main(env) == 0
    assert run_main(env, "--check") == 0


def test_check_detects_drift(env):
    assert run_main(env) == 0
    env.sip.REF_DOC.write_text(
        env.sip.REF_DOC.read_text(encoding="utf-8") + "stale\n", encoding="utf-8"
    )
    assert run_main(env, "--check") == 1


def test_no_hermes_install_is_skip_77(env):
    env.monkeypatch.setattr(env.sip, "find_hermes_dir", lambda: None)
    assert run_main(env, "--check") == 77


def test_other_machines_doc_is_skip_77(env):
    env.sip.REF_DOC.write_text("> Generated on machine: `SomeoneElse`\n", encoding="utf-8")
    assert run_main(env, "--check") == 77


@pytest.mark.parametrize("failure", [(None, ""), (1, "boom: plugin registry locked")])
def test_cli_failure_with_hermes_installed_is_exit_2(env, failure, capsys):
    env.cli[("plugins", "list", "--json", "--no-bundled")] = failure
    assert run_main(env, "--check") == 2
    assert "[FATAL]" in capsys.readouterr().out


def test_invalid_plugins_json_is_exit_2(env):
    env.cli[("plugins", "list", "--json", "--no-bundled")] = (0, "not json")
    assert run_main(env) == 2
    assert not env.sip.REF_DOC.exists()  # nothing written


def test_tools_list_failure_is_exit_2_not_empty_section(env):
    env.cli[("tools", "list")] = (1, "tools list crashed")
    assert run_main(env) == 2
    assert not env.sip.REF_DOC.exists()


def test_tools_list_unparseable_is_exit_2(env):
    env.cli[("tools", "list")] = (0, "a new output format nobody parses\n")
    assert run_main(env) == 2


def test_corrupt_install_metadata_is_exit_2(env):
    (env.home / "plugins" / ".install-metadata.json").write_text("{broken", encoding="utf-8")
    assert run_main(env) == 2


def test_missing_install_metadata_is_fine(env):
    assert run_main(env) == 0


def test_corrupt_config_is_exit_2(env):
    (env.home / "config.yaml").write_text("plugins: [unclosed\n", encoding="utf-8")
    assert run_main(env) == 2


def test_config_plugins_wrong_type_is_exit_2(env):
    (env.home / "config.yaml").write_text("plugins: just-a-string\n", encoding="utf-8")
    assert run_main(env) == 2
