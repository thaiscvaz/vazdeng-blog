"""
PT<->EN parity check for blog bundles (CI gate).

The 2026-06/07 desync incident left 12 PT posts without EN for weeks because
nothing enforced the pair. This check fails CI when a bundle drifts:

  - index.md exists but index.en.md is missing (or vice versa)
  - structural drift beyond tolerance: H2 section count must match exactly;
    word count within +/-40% (translations vary, structure should not)

Usage: python scripts/check_i18n_parity.py   (exit 1 on any violation)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

BLOG_DIR = Path(__file__).resolve().parents[1] / "content" / "blog"
WORD_TOLERANCE = 0.40


def stats(path: Path) -> tuple[int, int]:
    text = path.read_text(encoding="utf-8")
    body = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    h2 = len(re.findall(r"^## ", body, flags=re.MULTILINE))
    words = len(body.split())
    return h2, words


def main() -> int:
    problems: list[str] = []
    bundles = sorted(p for p in BLOG_DIR.iterdir() if p.is_dir())
    for bundle in bundles:
        pt = bundle / "index.md"
        en = bundle / "index.en.md"
        if pt.exists() != en.exists():
            missing = "index.en.md" if pt.exists() else "index.md"
            problems.append(f"{bundle.name}: {missing} MISSING (pair broken)")
            continue
        if not pt.exists():
            continue
        h2_pt, w_pt = stats(pt)
        h2_en, w_en = stats(en)
        if h2_pt != h2_en:
            problems.append(
                f"{bundle.name}: H2 sections differ (pt={h2_pt}, en={h2_en})"
            )
        if w_pt > 0 and abs(w_en - w_pt) / w_pt > WORD_TOLERANCE:
            problems.append(
                f"{bundle.name}: word count drift >40% (pt={w_pt}, en={w_en})"
            )

    if problems:
        print(f"i18n parity: {len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"i18n parity OK ({len(bundles)} bundles)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
