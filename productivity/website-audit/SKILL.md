---
name: website-audit
description: "Audit websites/codebases into .docx reports; read-only."
version: v0.9.0
author: Hermes Agent (ported from starred-repo research)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [audit, reports, docx, read-only]
    related_skills: [docx]
---

## What This Skill Does

- User wants an improvement/fix report as a document (usually `.docx`) from analyzing their website or codebase - Analysis-only workflow required — no refactoring, feature development, or source edits permitted


# Website Audit Report Skill

Generate comprehensive .docx audit reports for websites/codebases via read-only analysis. Zero source modifications — pure documentation deliverable.

## When to Use
- User wants an improvement/fix report as a document (usually `.docx`) from analyzing their website or codebase
- Analysis-only workflow required — no refactoring, feature development, or source edits permitted
- Deliverable must be actionable with prioritized recommendations based on actual findings
- Report format requested is Word (.docx) rather than chat text/markdown

## Prerequisites
- `python-docx` installed: `pip install python-docx`
- Python 3.10+ available (Windows often needs explicit venv path)
- Output directory exists before script execution — always run `mkdir -p /path/to/output/` first
- Source files accessible for read-only analysis

## Workflow

### Phase 1: Discovery & Inventory (Read-Only Analysis)

**Step 1.1:** Identify all source files to analyze using shell commands or file search tools. Count total files, identify technology stack (frameworks vs vanilla? build tools?), note unusual patterns like underscore-prefixed CSS partials or IIFE JavaScript patterns.

**Step 1.2:** Read each source file fully using the `read_file` tool. Capture:
- File purpose and scope
- Notable implementation details (security features, accessibility patterns, error handling)
- Potential issues found during reading
- Strengths worth documenting in report

### Phase 2: Analysis & Synthesis

**Step 2.1:** Group findings into standard sections:
1. Architecture Overview (tech stack, file organization, dependencies)
2. Accessibility Audit (WCAG compliance patterns, screen reader behavior, keyboard navigation)
3. Security Analysis (CSP meta tags, form protection mechanisms, external link security)
4. SEO & Social Media (meta tags, Open Graph/Twitter cards, structured data/JSON-LD, sitemap)
5. Performance (loading strategies, asset optimization opportunities, caching potential)
6. Code Quality (naming conventions, code comments, modularity, error handling patterns)
7. Content & UX (navigation flow, interactive elements, responsive behavior observations)
8. Cross-Page Consistency (patterns across all pages, notable deviations flagged)
9. Testing & CI/CD (test coverage gaps, automation opportunities)
10. Recommendations Summary (prioritized by impact: High/Medium/Low + effort estimate)

**Step 2.2:** Add deep-dive sections for complex findings:
- Per-file/per-page comparison tables when multiple similar pages exist
- Security pattern verification (e.g., CSP directives vs actual site usage)
- Error handling gaps in JavaScript modules (fetch calls without `.catch()`, form POST failures with no user feedback, etc.)
- Form processing flows and bot mitigation strategies documented

### Phase 3: Report Generation (.docx via python-docx)

**CRITICAL PATTERN:** Do NOT use JSON spec approach. Complex markdown-like text (tables, code blocks) breaks strict JSON escaping rules on Windows terminals — especially with Unicode characters like em-dashes (`—`, U+2014). Always write direct python-docx scripts instead of trying to pass content through a JSON intermediate format.

Instead, write a self-contained Python script that builds the document directly:
```python
from docx import Document
doc = Document()

# Add headings for each section
doc.add_heading('Section Title', level=1)
doc.add_paragraph('Analysis text with findings...')

# Use tables for comparison data when needed
table = doc.add_table(rows=N, cols=M, style='Table Grid')
for cell in table.rows[0].cells:
    cell.text = 'Header'

# Bullet lists with bold items where emphasis is needed
p = doc.add_paragraph()
r = p.add_run('Bold label: ')  # Bold prefix for list items
r.bold = True
p.add_run('Normal description text follows')
```

**Step 3.2:** Key document structure elements:
- Title page with project name, date, file count analyzed
- Sections numbered sequentially (1., 2., etc.) or named by analysis category
- Summary tables comparing status across pages/files using 'Table Grid' style
- Final assessment section with overall grade and prioritized recommendations
- Appendices for technical details, dependency graphs, raw data inventories

**Step 3.3:** Run the script:
```bash
# Always verify output directory exists first — never skip this step!
mkdir -p "output_dir_path"
python path/to/generate_script.py
```
Verify exit code is 0 and file size > 10KB (indicates content was written successfully).

### Phase 4: Final Review Pass ⚠️ MANDATORY BEFORE DELIVERY

**This step catches factual errors that slip through during analysis.** Verify every major claim against fresh reads of critical source files — do NOT trust earlier notes blindly. At least one factual claim per audit cycle typically needs correction (e.g., claiming no `!important` usage when two exist inside media queries).

Example verification checks to run before finalizing:
```python
def verify_claims(doc_path):
    doc = Document(doc_path)
    full_text = '\n'.join([p.text for p in doc.paragraphs])
    
    # Cross-reference key claims against actual source files read during this session
    with open('site.js', encoding='utf-8') as f:
        js_source = f.read()
    
    if 'no .catch() handler' in full_text and '.catch()' not in js_source:
        print('Verified: Kaggle fetch lacks error handling - claim is accurate')
```

Final review checklist (verify each before delivery):
- [ ] All factual claims about code behavior verified against actual source files read during this session
- [ ] No false positives discovered (e.g., claiming no `!important` when one exists in a media query block)
- [ ] Section numbers and headings match document structure exactly
- [ ] File counts, line counts accurate for inventory table
- [ ] Recommendations are actionable and prioritized correctly by impact × effort matrix
- [ ] Final assessment grade is justified by findings documented above it

### Phase 5: Delivery & Cleanup

**Step 5.1:** Deliver the `.docx` file to user via chat (MEDIA syntax or direct attachment). Format like this in your response markdown:

```markdown
## 📄 **Website Audit Report — FINAL**
*(File size · N pages)*
```

**Step 5.2:** Clean up temporary files:
- Remove `build-audit-vX.py` scripts used for generation unless user wants them preserved
- Keep only the final `.docx` deliverable when cleanup is requested by user
- Verify working tree is clean (`git status`) if in a git repo context and no changes were made

## Pitfalls & Lessons Learned

1. **JSON spec approach always fails for complex reports.** When document contains tables, code blocks, or markdown-like text, JSON escaping breaks on Windows terminals — especially with Unicode characters like em-dashes (U+2014 `—`). Always write direct python-docx scripts instead of trying to pass content through a JSON intermediate format.

2. **Unicode em-dashes cause patch failures.** The character `—` (U+2014) causes SyntaxError when editing files containing it via terminal/patch tools on Windows. Replace all instances with ASCII `--` before any edits using:
   ```bash
   python -c "p='file.py'; t=open(p,'r',encoding='utf-8').read(); r=t.replace('\u2014','--'); open(p,'w',encoding='utf-8').write(r)"
   ```

3. **Output directory must exist before script execution.** python-docx does not auto-create parent directories — `mkdir -p /path/to/output/` is required or the write will fail silently with a confusing error message about missing path components.

4. **Final review catches false positives.** Always re-read critical source files and verify key claims rather than trusting analysis notes from earlier in the same session. At least one factual claim per audit cycle typically needs correction (e.g., "no `!important` usage" when two exist inside media queries). Document corrections made during this step for transparency with user if asked.

5. **Python path on Windows often needs explicit venv reference.** System python may not have `python-docx` installed — use:
   ```bash
   C:/Users/Owner/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe script.py
   ```
   If that fails, check with `where.exe python` or verify via terminal if standard `python3` works.

6. **Type mismatch in bullet rendering.** When passing `(text, is_bold)` tuples to paragraph builders expecting plain strings, unpack them first and set `r.bold = True` explicitly rather than relying on implicit formatting detection from markup markers like `<strong>`.