# Missing From Local (Skills in Repository but Not in Local Profile)

The following 13 skills exist in this repository but are **not present** in the local
Hermes skills directory at `C:\Users\Loggg\AppData\Local\hermes\skills\`.

They were imported from the `the-skill-maker` or `the-memory-controller` profiles,
which are no longer present on this machine (no `profiles/` directory exists under
`AppData\Local\hermes\`).

## Data Science Category (12 skills)

These were all in the `data-science/` category, which has no corresponding directory
in the local skills tree:

| # | Skill Name | Local Status | Notes |
|---|-----------|-------------|-------|
| 1 | `build-systems-data` | Not local | Data build pipeline skill |
| 2 | `cli-tool-craft` | Not local | CLI tool development craft |
| 3 | `evolutionary-ml` | Not local | Evolutionary ML techniques |
| 4 | `model-export-deploy` | Not local | Model export and deployment |
| 5 | `orbital-mechanics-data` | Not local | Orbital mechanics data processing |
| 6 | `python-craft` | Not local | Python development craft |
| 7 | `python-data-science` | Not local | Python data science workflows |
| 8 | `sql-for-data` | Not local | SQL for data analysis |
| 9 | `static-site-seo` | Not local | Static site SEO optimization |
| 10 | `streamlit-dashboards` | Not local | Streamlit dashboard creation |
| 11 | `test-infra-ml` | Not local | ML infrastructure testing |
| 12 | `verification-culture` | Not local | Verification culture practices |

## Autonomous AI Agents Category (1 skill)

| # | Skill Name | Local Status | Notes |
|---|-----------|-------------|-------|
| 13 | `cron-job-authoring` | Not local | Cron job authoring patterns; was fixed in this audit (frontmatter normalized) |

## Action Items

- [ ] Decide whether to copy these 13 skills back to local from the repository
- [ ] If the local skills directory was the original source, investigate whether
      these skills were lost during a profile migration or were never synced locally
