#!/usr/bin/env python3
"""
Generate placeholder images for albums and artists.
This creates simple gradient images with text that can be replaced later.
"""

import json
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import re

# Configuration
MUSIC_DATA_PATH = "new_blog/src/data/music-data.json"
MEDIA_DIR = Path("new_blog/public/media")
ALBUM_COVERS_DIR = MEDIA_DIR / "albums"
ARTIST_IMAGES_DIR = MEDIA_DIR / "artists"

# Create directories
ALBUM_COVERS_DIR.mkdir(parents=True, exist_ok=True)
ARTIST_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

def slugify(text):
    """Convert text to URL-friendly slug."""
    if not text:
        return 'unknown'
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.lower().strip('-')

def generate_gradient_image(text, filepath, size=(400, 400), colors=None):
    """Generate a gradient placeholder image with text."""
    if colors is None:
        colors = [(102, 126, 234), (118, 75, 162)]  # Purple gradient
    
    # Create gradient
    img = Image.new('RGB', size, color=colors[0])
    draw = ImageDraw.Draw(img)
    
    # Draw gradient
    for i in range(size[1]):
        ratio = i / size[1]
        r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
        g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
        b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
        draw.line([(0, i), (size[0], i)], fill=(r, g, b))
    
    # Add text
    try:
        # Try to use system fonts
        font_size = min(60, size[0] // len(text) if text else 60)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Get text dimensions and wrap if needed
    words = text.split() if text else []
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= size[0] - 40:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    
    if not lines:
        lines = [text[:20] if text else "?"]
    
    # Center the text
    total_height = sum(draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines)
    start_y = (size[1] - total_height) // 2
    
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size[0] - text_width) // 2
        y = start_y + i * (text_height + 10)
        draw.text((x, y), line, fill=(255, 255, 255), font=font, anchor="lt")
    
    img.save(filepath, 'PNG')
    return True

def process_albums(music_data):
    """Process albums and generate cover images."""
    print("Generating album covers...")
    album_media = {}
    
    for album in music_data.get('albums', []):
        album_slug = album.get('slug', slugify(album['name']))
        cover_path = ALBUM_COVERS_DIR / f"{album_slug}.png"
        
        # Skip if already exists
        if cover_path.exists():
            album_media[album['name']] = f"/media/albums/{album_slug}.png"
            continue
        
        # Generate placeholder
        album_name = album['name'][:30]  # Limit length
        if generate_gradient_image(album_name, cover_path):
            album_media[album['name']] = f"/media/albums/{album_slug}.png"
            print(f"✓ Generated cover for: {album['name']}")
    
    return album_media

def process_artists(music_data):
    """Process artists and generate images."""
    print("Generating artist images...")
    artist_media = {}
    
    for artist in music_data.get('artists', []):
        artist_slug = artist.get('slug', slugify(artist['name']))
        image_path = ARTIST_IMAGES_DIR / f"{artist_slug}.png"
        
        # Skip if already exists
        if image_path.exists():
            artist_media[artist['name']] = f"/media/artists/{artist_slug}.png"
            continue
        
        # Generate placeholder with first letter or name
        display_text = artist['name'][0].upper() if artist['name'] else '?'
        if len(artist['name']) <= 15:
            display_text = artist['name']
        else:
            display_text = artist['name'][:15]
        
        if generate_gradient_image(display_text, image_path, size=(300, 300)):
            artist_media[artist['name']] = f"/media/artists/{artist_slug}.png"
            print(f"✓ Generated image for: {artist['name']}")
    
    return artist_media

def update_music_data(music_data, album_media, artist_media):
    """Update music data with media paths."""
    # Update albums
    for album in music_data.get('albums', []):
        if album['name'] in album_media:
            album['coverImage'] = album_media[album['name']]
    
    # Update artists
    for artist in music_data.get('artists', []):
        if artist['name'] in artist_media:
            artist['image'] = artist_media[artist['name']]
    
    # Update tracks with album cover
    for track in music_data.get('tracks', []):
        album_name = track.get('album')
        if album_name and album_name in album_media:
            track['albumCover'] = album_media[album_name]
    
    return music_data

def main():
    print("Loading music data...")
    with open(MUSIC_DATA_PATH, 'r', encoding='utf-8') as f:
        music_data = json.load(f)
    
    print(f"Found {len(music_data.get('albums', []))} albums and {len(music_data.get('artists', []))} artists")
    
    # Process media
    album_media = process_albums(music_data)
    artist_media = process_artists(music_data)
    
    # Update music data
    updated_data = update_music_data(music_data, album_media, artist_media)
    
    # Save updated data (backup original)
    backup_path = MUSIC_DATA_PATH.replace('.json', '_backup.json')
    if not Path(backup_path).exists():
        import shutil
        shutil.copy(MUSIC_DATA_PATH, backup_path)
        print(f"✓ Created backup: {backup_path}")
    
    # Save updated data
    with open(MUSIC_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Generated {len(album_media)} album covers")
    print(f"✓ Generated {len(artist_media)} artist images")
    print(f"✓ Updated {MUSIC_DATA_PATH}")
    print("\nNote: You can replace these placeholder images with actual album covers")
    print("      and artist photos by placing them in the same directories with the same filenames.")

if __name__ == '__main__':
    try:
        main()
    except ImportError:
        print("Error: PIL/Pillow is required. Install with: pip install Pillow")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

