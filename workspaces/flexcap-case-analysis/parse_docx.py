import zipfile, xml.etree.ElementTree as ET, sys

path = "/mnt/c/Users/User/Desktop/FlexCap_Case_Analysis_v14.docx"
ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

with zipfile.ZipFile(path) as z:
    with z.open("word/document.xml") as f:
        tree = ET.parse(f)
        root = tree.getroot()
        for para in root.iter(f"{ns}p"):
            texts = []
            for t in para.iter(f"{ns}t"):
                if t.text:
                    texts.append(t.text)
            line = "".join(texts)
            if line.strip():
                print(line)
