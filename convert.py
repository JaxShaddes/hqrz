import os
from PIL import Image
from pathlib import Path

def compress_images(input_folder, output_folder=None, quality=80, max_width=1920):
    """
    Compress and convert all images to JPG
    
    Args:
        input_folder: Path to your images folder
        output_folder: Where to save (None = overwrite originals)
        quality: JPG quality 1-100 (80 is good balance)
        max_width: Max width in pixels (maintains aspect ratio)
    """
    
    if output_folder is None:
        output_folder = input_folder
    
    supported_formats = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.gif'}
    
    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            file_path = Path(root) / filename
            
            if file_path.suffix.lower() not in supported_formats:
                continue
            
            try:
                with Image.open(file_path) as img:
                    # Convert to RGB (required for JPG)
                    if img.mode in ('RGBA', 'P', 'LA'):
                        # White background for transparent images
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Resize if too large
                    if img.width > max_width:
                        ratio = max_width / img.width
                        new_size = (max_width, int(img.height * ratio))
                        img = img.resize(new_size, Image.LANCZOS)
                    
                    # Create output path (maintaining folder structure)
                    relative_path = Path(root).relative_to(input_folder)
                    output_dir = Path(output_folder) / relative_path
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Save as JPG
                    output_path = output_dir / f"{file_path.stem}.jpg"
                    img.save(output_path, 'JPEG', quality=quality, optimize=True)
                    
                    # Show compression results
                    original_size = file_path.stat().st_size / 1024
                    new_size = output_path.stat().st_size / 1024
                    saved = ((original_size - new_size) / original_size) * 100
                    
                    print(f"✓ {filename}: {original_size:.1f}KB → {new_size:.1f}KB ({saved:.1f}% saved)")
                    
            except Exception as e:
                print(f"✗ Error processing {filename}: {e}")

# ===== USAGE =====
if __name__ == "__main__":
    compress_images(
        input_folder="./portfolio",           # Your images folder
        output_folder="./images_compressed", # Output folder (or None to overwrite)
        quality=80,                         # 60-80 recommended for web
        max_width=1920                      # Max width in pixels
    )