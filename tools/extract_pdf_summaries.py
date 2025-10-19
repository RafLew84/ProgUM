import json
from pathlib import Path
from typing import List, Dict

from pdfminer.high_level import extract_text


def summarize_text(raw: str, max_words: int = 40) -> str:
    text = raw.replace('\r', '\n')
    # Normalize blank lines
    lines = [l.strip() for l in text.split('\n')]
    # Drop very short/irrelevant lines
    lines = [l for l in lines if l and not l.lower().startswith('page ') and not l.isdigit()]
    if not lines:
        return ''
    # Heuristic: first meaningful line is title-ish; build brief summary from first lines
    joined = ' '.join(lines[:8])  # limit to first block
    words = joined.split()
    if len(words) <= max_words:
        return ' '.join(words)
    return ' '.join(words[:max_words]) + '…'


def extract_first_page_text(pdf_path: Path) -> str:
    try:
        return extract_text(str(pdf_path), page_numbers={0}) or ''
    except Exception:
        return ''


def collect(pdf_dirs: List[Path]) -> Dict[str, Dict[str, str]]:
    data: Dict[str, Dict[str, str]] = {}
    for base in pdf_dirs:
        for pdf in sorted(base.glob('Wyklad*.pdf')):
            raw = extract_first_page_text(pdf)
            summary = summarize_text(raw)
            data[str(pdf).replace('\\', '/')] = {
                'summary': summary,
                'empty': '1' if not summary else '0',
            }
    return data


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    pdf_dirs = [root / 'PUM1' / 'Wyk', root / 'PUM2' / 'Wyk']
    result = collect(pdf_dirs)
    print(json.dumps(result, ensure_ascii=False, indent=2))

