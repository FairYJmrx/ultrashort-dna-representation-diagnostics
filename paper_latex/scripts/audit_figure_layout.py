from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFont


def render_first_page(path: Path, scale: float) -> tuple[Image.Image, float]:
    document = pdfium.PdfDocument(str(path))
    page = document[0]
    width, height = page.get_size()
    image = page.render(scale=scale).to_pil().convert("RGB")
    return image, width / height


def fit_thumbnail(image: Image.Image, width: int, height: int) -> Image.Image:
    copy = image.copy()
    copy.thumbnail((width, height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (width, height), "white")
    canvas.paste(copy, ((width - copy.width) // 2, (height - copy.height) // 2))
    return canvas


def main() -> None:
    parser = argparse.ArgumentParser(description="Render manuscript figures into contact sheets for visual QA.")
    parser.add_argument("figure_root", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--scale", type=float, default=2.0)
    parser.add_argument("--columns", type=int, default=2)
    args = parser.parse_args()

    paths = sorted(args.figure_root.rglob("*.pdf"))
    args.out_dir.mkdir(parents=True, exist_ok=True)
    tile_width, tile_height, label_height = 1000, 620, 58
    font = ImageFont.load_default(size=20)
    rows: list[tuple[str, str, float, int, int]] = []
    tiles: list[Image.Image] = []

    for path in paths:
        rendered, aspect = render_first_page(path, args.scale)
        relative = path.relative_to(args.figure_root).as_posix()
        preview = fit_thumbnail(rendered, tile_width, tile_height)
        tile = Image.new("RGB", (tile_width, tile_height + label_height), "white")
        tile.paste(preview, (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.rectangle((0, 0, tile.width - 1, tile.height - 1), outline="#c7cdd4", width=2)
        draw.text((16, tile_height + 12), f"{relative} | aspect {aspect:.2f}", fill="#111827", font=font)
        tiles.append(tile)
        rows.append((relative, str(path), aspect, rendered.width, rendered.height))

        rendered.save(args.out_dir / f"{path.stem}.png")

    columns = max(1, args.columns)
    row_count = math.ceil(len(tiles) / columns)
    sheet = Image.new("RGB", (columns * tile_width, row_count * (tile_height + label_height)), "#eef1f4")
    for index, tile in enumerate(tiles):
        sheet.paste(tile, ((index % columns) * tile_width, (index // columns) * (tile_height + label_height)))
    sheet.save(args.out_dir / "figure_contact_sheet.png")

    with (args.out_dir / "figure_geometry.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["relative_path", "absolute_path", "aspect_ratio", "render_width_px", "render_height_px"])
        writer.writerows(rows)

    print(f"Rendered {len(paths)} figures to {args.out_dir}")


if __name__ == "__main__":
    main()
