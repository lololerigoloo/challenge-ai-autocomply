import json
import re
from PyPDF2 import PdfReader

# ----------------------------------------------------------
# 1. TITRES DES SECTIONS À DÉTECTER (ajuste-les si nécessaire)
# ----------------------------------------------------------

SECTION_TITLES = [
    "Articles & Amendments",
    "By Laws",
    "Unanimous Shareholder Agreement",
    "Minutes & Resolutions",
    "Directors Register",
    "Officers Register",
    "Shareholder Register",
    "Securities Register",
    "Share Certificates",
    "Ultimate Beneficial Owner Register",
]

# Expressions régulières robustes pour matcher les titres
TITLE_PATTERNS = {
    title: re.compile(rf"\b{re.escape(title)}\b", re.IGNORECASE)
    for title in SECTION_TITLES
}

# ----------------------------------------------------------
# 2. SCAN DU PDF POUR TROUVER OÙ CHAQUE SECTION COMMENCE
# ----------------------------------------------------------

def find_section_pages(pdf_path):
    reader = PdfReader(pdf_path)
    num_pages = len(reader.pages)

    detections = []

    for i in range(num_pages):
        text = reader.pages[i].extract_text() or ""
        found = None

        for title, rgx in TITLE_PATTERNS.items():
            if rgx.search(text):
                found = title
                break

        if found:
            detections.append((i + 1, found))  # pages en 1-based

    return detections

# ----------------------------------------------------------
# 3. CONSTRUIRE LES INTERVALLES startPage / endPage
# ----------------------------------------------------------

def build_section_map(detections, total_pages):
    # detections = [(pageNumber, sectionName), ...]
    if not detections:
        return []

    sections = []

    for idx, (page, title) in enumerate(detections):
        start_page = page

        if idx < len(detections) - 1:
            # fin = page juste avant le début de la prochaine section
            end_page = detections[idx + 1][0] - 1
        else:
            # dernière section → jusqu'à la fin du PDF
            end_page = total_pages

        sections.append({
            "name": title,
            "startPage": start_page,
            "endPage": end_page
        })

    return sections

# ----------------------------------------------------------
# 4. MAIN
# ----------------------------------------------------------

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python script.py <PDF>")
        return

    pdf_path = sys.argv[1]

    # scan
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    detections = find_section_pages(pdf_path)

    if not detections:
        print("Aucune section trouvée.")
        return

    section_map = build_section_map(detections, total_pages)

    print(json.dumps({"sections": section_map}, indent=4))


# ----------------------------------------------------------
if __name__ == "__main__":
    main()
