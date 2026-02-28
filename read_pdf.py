import sys
import subprocess
try:
    import fitz
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyMuPDF"])
    import fitz

pdf_path = r"d:\AITS测试平台\AITS系统详细设计方案.pdf"
txt_path = r"d:\AITS测试平台\AITS系统详细设计方案.txt"

text = ""
with fitz.open(pdf_path) as doc:
    for page in doc:
        text += page.get_text()

with open(txt_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Extraction complete.")
