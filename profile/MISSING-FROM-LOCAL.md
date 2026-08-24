# Missing From Local (Skills in Repository but Not in Local Profile)

This document tracks skills that exist in the repository but may not be present
in the local Hermes skills directory at `C:\Users\Loggg\AppData\Local\hermes\skills\`.

## Sync Status

As of the latest sync, **all 127 skills from the repository are present in the local profile**.
The 13 skills that were previously missing (12 from `data-science/` and 1 from
`autonomous-ai-agents/`) have been synced from the repository.

### Previously Missing (Now Synced)

| # | Category | Skill Name | Notes |
|---|----------|-----------|-------|
| 1 | data-science | `build-systems-data` | Data build pipeline skill — now local |
| 2 | data-science | `cli-tool-craft` | CLI tool development craft — now local |
| 3 | data-science | `evolutionary-ml` | Evolutionary ML techniques — now local |
| 4 | data-science | `model-export-deploy` | Model export and deployment — now local |
| 5 | data-science | `orbital-mechanics-data` | Orbital mechanics data processing — now local |
| 6 | data-science | `python-craft` | Python development craft — now local |
| 7 | data-science | `python-data-science` | Python data science workflows — now local |
| 8 | data-science | `sql-for-data` | SQL for data analysis — now local |
| 9 | data-science | `static-site-seo` | Static site SEO optimization — now local |
| 10 | data-science | `streamlit-dashboards` | Streamlit dashboard creation — now local |
| 11 | data-science | `test-infra-ml` | ML infrastructure testing — now local |
| 12 | data-science | `verification-culture` | Verification culture practices — now local |
| 13 | autonomous-ai-agents | `cron-job-authoring` | Cron job authoring patterns — now local |

## Local-Only Skill

The local profile has **1 skill** that does not exist in the repository:

| # | Skill Name | Local Path | Notes |
|---|-----------|------------|-------|
| 1 | `hermes-agent` | `C:\Users\Loggg\AppData\Local\hermes\skills\autonomous-ai-agents\hermes-agent` | Pre-installed by Hermes core; the repo version is a curated copy |

## Action Items

- [x] Sync all 13 missing skills from the repository to local profile
- [x] Verify all 127 repo skills are present locally
- [x] Document sync status in this file
