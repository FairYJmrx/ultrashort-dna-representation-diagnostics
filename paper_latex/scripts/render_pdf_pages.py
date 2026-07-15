from __future__ import annotations

import argparse
from pathlib import Path

import pypdfium2 as pdfium


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a PDF into PNG pages for visual QA.")
    parser.add_argument("pdf", type=Path, help="Input PDF path.")
    parser.add_argument("--out-dir", type=Path, default=Path("qa"), help="Output directory.")
    parser.add_argument("--prefix", default="page", help="PNG filename prefix.")
    parser.add_argument("--scale", type=float, default=2.0, help="Render scale.")
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    doc = pdfium.PdfDocument(str(args.pdf))
    for index, page in enumerate(doc, start=1):
        image = page.render(scale=args.scale).to_pil()
        out_path = args.out_dir / f"{args.prefix}_{index:02d}.png"
        image.save(out_path)
        print(out_path)
    print(f"pages {len(doc)}")


if __name__ == "__main__":
    main()
