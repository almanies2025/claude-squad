"""
Fix the missing space in "Why This AddressesRoot Cause:" → "Why This Addresses Root Cause:"
in v13 (which inherited the issue from v12, which introduced it via Fix 5).

The root cause: fix_v11.py Fix 5 split "Why This Addresses Root Cause:" into two runs:
  run[0]: "Why This Addresses"   ← missing trailing space
  run[1]: "Root Cause: "         ← correct but concatenates badly

Fix: add trailing space to run[0].
"""

from docx import Document

SRC = "/mnt/c/Users/User/Desktop/FlexCap_Case_Analysis_v13.docx"
DST = "/mnt/c/Users/User/Desktop/FlexCap_Case_Analysis_v14.docx"

doc = Document(SRC)

fixed = []
for i, para in enumerate(doc.paragraphs):
    if (
        len(para.runs) >= 2
        and para.runs[0].text == "Why This Addresses"
        and para.runs[1].text.startswith("Root Cause:")
    ):
        para.runs[0].text = "Why This Addresses "  # add trailing space
        fixed.append(f"  Para [{i}]")
        print(f"Fix: space restored in para [{i}]")

doc.save(DST)
print(f"\nSaved → {DST}")
print(f"Fixed {len(fixed)} paragraph(s).")
