import fitz
import re


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception:
        raise ValueError("Invalid PDF file. Could not parse the document.")

    text_parts = []
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text = page.get_text("text")
        if text.strip():
            text_parts.append(text)

    doc.close()

    full_text = "\n\n".join(text_parts)
    if not full_text.strip():
        raise ValueError("No text could be extracted. This might be a scanned/image-based PDF.")

    return full_text


def extract_sections(text: str) -> dict:
    section_patterns = [
        r'(?i)(education|academic)',
        r'(?i)(experience|employment|work\s*history)',
        r'(?i)(skills|technical\s*skills|competencies)',
        r'(?i)(projects|personal\s*projects)',
        r'(?i)(certifications?|courses?)',
        r'(?i)(summary|objective|about\s*me|profile)',
    ]

    sections = {}
    lines = text.split('\n')
    current_section = "header"
    current_content = []

    for line in lines:
        matched = False
        for pattern in section_patterns:
            if re.match(pattern, line.strip()):
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = re.match(pattern, line.strip()).group(1).lower()
                current_content = []
                matched = True
                break
        if not matched:
            current_content.append(line)

    if current_content:
        sections[current_section] = '\n'.join(current_content)

    return sections