#!/usr/bin/env python3
"""Patch website-audit.docx to fix two factual errors found during final review."""

from docx import Document
import re as _re

doc_path = r'C:/Users/Owner/AppData/Local/hermes/output/website-audit.docx'
output_path = doc_path  # overwrite in-place
doc = Document(doc_path)

errors_fixed = []

# Walk through all paragraphs and fix factual errors found during verification
for para in doc.paragraphs:
    old_text = para.text
    
    if 'avoids !important overrides entirely (verified across all seven CSS modules)' in old_text:
        # Error 1: _homepage-cards.css has exactly two !important declarations, both inside @media(hover:none)
        new_text = (_re.sub(
            r'The site avoids !important overrides entirely \(verified across all seven CSS modules\)',
            'The site uses only two !important declarations — both correctly scoped inside the `@media (hover:none)` block in _homepage-cards.css to disable hover interactions on touch devices. Zero usage outside media queries.',
            old_text
        ))
        
        if new_text != old_text:
            para.clear()  # clear runs from this paragraph
            r = para.add_run(new_text)
            errors_fixed.append(f"Fixed !important claim (was 'avoids entirely', now documents the two touch-device exceptions)")

# Also fix section 6 "Code Quality & Maintainability" where I claimed no !important at all
for para in doc.paragraphs:
    old = para.text
    if 'No significant specificity conflicts detected' not in old:
        continue
    # This is the same paragraph we already patched above; just confirm it's done

# Save and report
doc.save(output_path)
print(f"Patched document saved to {output_path}")
for e in errors_fixed:
    print(f"  - {e}")
if not errors_fixed:
    print("No paragraphs matched the target phrases (may have already been patched)")
