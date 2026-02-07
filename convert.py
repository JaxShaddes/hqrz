import os
from pathlib import Path

from PIL import Image


SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".gif"}


def compress_images(input_folder, output_folder=None, quality=80, max_width=1920):
    """
    Compress and convert images to JPG recursively.

    Args:
        input_folder: Root folder to scan recursively.
        output_folder: Destination root. If None, overwrite inside input folder.
        quality: JPG quality 1-100 (80 is a good balance).
        max_width: Max width in pixels (height keeps aspect ratio).
    """

    input_folder = Path(input_folder)
    if not input_folder.exists():
        raise FileNotFoundError(f"Input folder not found: {input_folder.resolve()}")
    if not input_folder.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {input_folder.resolve()}")

    if output_folder is None:
        output_folder = input_folder
    else:
        output_folder = Path(output_folder)

    input_folder_resolved = input_folder.resolve()
    output_folder_resolved = output_folder.resolve()

    processed_count = 0

    for root, dirs, files in os.walk(input_folder):
        root_path = Path(root)

        # Skip the output folder tree so generated files are not reprocessed.
        if output_folder_resolved != input_folder_resolved:
            dirs[:] = [d for d in dirs if (root_path / d).resolve() != output_folder_resolved]

        for filename in files:
            file_path = root_path / filename

            if file_path.suffix.lower() not in SUPPORTED_FORMATS:
                continue

            try:
                with Image.open(file_path) as img:
                    # Convert to RGB (required for JPG)
                    if img.mode in ("RGBA", "P", "LA"):
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        if img.mode == "P":
                            img = img.convert("RGBA")
                        background.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
                        img = background
                    elif img.mode != "RGB":
                        img = img.convert("RGB")

                    # Resize if too large
                    if img.width > max_width:
                        ratio = max_width / img.width
                        new_size = (max_width, int(img.height * ratio))
                        img = img.resize(new_size, Image.LANCZOS)

                    # Keep folder structure under output root
                    relative_path = root_path.relative_to(input_folder)
                    output_dir = output_folder / relative_path
                    output_dir.mkdir(parents=True, exist_ok=True)

                    output_path = output_dir / f"{file_path.stem}.jpg"
                    img.save(output_path, "JPEG", quality=quality, optimize=True)

                    original_size_kb = file_path.stat().st_size / 1024
                    new_size_kb = output_path.stat().st_size / 1024
                    if original_size_kb > 0:
                        saved_pct = ((original_size_kb - new_size_kb) / original_size_kb) * 100
                    else:
                        saved_pct = 0

                    processed_count += 1
                    print(
                        f"[OK] {filename}: {original_size_kb:.1f}KB -> "
                        f"{new_size_kb:.1f}KB ({saved_pct:.1f}% saved)"
                    )

            except Exception as exc:
                print(f"[ERR] Error processing {file_path}: {exc}")

    if processed_count == 0:
        print(f"No supported images found in: {input_folder_resolved}")
    else:
        print(f"Done. Processed {processed_count} image(s).")


# ===== USAGE =====
if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent

    compress_images(
        input_folder=script_dir,  # Process all folders and subfolders under this script location
        output_folder=script_dir / "images_compressed",  # Set None to overwrite originals
        quality=80,
        max_width=1920,
    )
