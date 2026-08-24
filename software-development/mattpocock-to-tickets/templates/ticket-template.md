# <NN>: <title>

**What to build:** end-to-end behaviour (e.g. "Add {disease-name} page: fetch from PubMed + Europe PMC, gate with Claude, render to HTML, validate in 9-page pipeline output")

**Blocked by:** tickets that gate this one (leave empty if none)

**Status:** ready-for-agent

**Acceptance criteria:**
- [ ] Data source parser returns valid JSON for this disease
- [ ] Gatekeeper scoring produces expected pass/fail count
- [ ] Disease page renders correctly in the pipeline output
- [ ] Tests pass (`pytest tests/ -v`)
