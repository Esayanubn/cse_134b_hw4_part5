#!/usr/bin/env python3
"""
Update media paths in music-data.json to use .jpg files instead of .png placeholders.
Remove placeholder .png files if .jpg exists.
"""

import json
import os
from pathlib import Path

MUSIC_DATA_PATH = "new_blog/src/data/music-data.json"
ALBUM_COVERS_DIR = Path("new_blog/public/media/albums")
ARTIST_IMAGES_DIR = Path("new_blog/public/media/artists")

def update_media_paths():
    """Update paths from .png to .jpg if .jpg exists."""
    print("Loading music data...")
    with open(MUSIC_DATA_PATH, 'r', encoding='utf-8') as f:
        music_data = json.load(f)
    
    updated_count = 0
    
    # Update albums
    print("\nUpdating album covers...")
    for album in music_data.get('albums', []):
        if 'coverImage' in album and album['coverImage']:
            # Check if .png path exists
            if album['coverImage'].endswith('.png'):
                slug = album['coverImage'].split('/')[-1].replace('.png', '')
                jpg_path = ALBUM_COVERS_DIR / f"{slug}.jpg"
                png_path = ALBUM_COVERS_DIR / f"{slug}.png"
                
                if jpg_path.exists():
                    # Update path to .jpg
                    album['coverImage'] = album['coverImage'].replace('.png', '.jpg')
                    updated_count += 1
                    print(f"✓ Updated: {album['name']} -> .jpg")
                    
                    # Remove .png placeholder
                    if png_path.exists():
                        png_path.unlink()
                        print(f"  Removed placeholder: {png_path.name}")
    
    # Update artists
    print("\nUpdating artist images...")
    for artist in music_data.get('artists', []):
        if 'image' in artist and artist['image']:
            # Check if .png path exists
            if artist['image'].endswith('.png'):
                slug = artist['image'].split('/')[-1].replace('.png', '')
                jpg_path = ARTIST_IMAGES_DIR / f"{slug}.jpg"
                png_path = ARTIST_IMAGES_DIR / f"{slug}.png"
                
                if jpg_path.exists():
                    # Update path to .jpg
                    artist['image'] = artist['image'].replace('.png', '.jpg')
                    updated_count += 1
                    print(f"✓ Updated: {artist['name']} -> .jpg")
                    
                    # Remove .png placeholder
                    if png_path.exists():
                        png_path.unlink()
                        print(f"  Removed placeholder: {png_path.name}")
    
    # Update tracks (albumCover)
    print("\nUpdating track album covers...")
    for track in music_data.get('tracks', []):
        if 'albumCover' in track and track['albumCover']:
            if track['albumCover'].endswith('.png'):
                slug = track['albumCover'].split('/')[-1].replace('.png', '')
                jpg_path = ALBUM_COVERS_DIR / f"{slug}.jpg"
                
                if jpg_path.exists():
                    track['albumCover'] = track['albumCover'].replace('.png', '.jpg')
    
    # Save updated data
    print(f"\nSaving updated data...")
    with open(MUSIC_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(music_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Updated {updated_count} media paths")
    print(f"✓ Saved to {MUSIC_DATA_PATH}")
    
    # Clean up remaining .png files that have .jpg counterparts
    print("\nCleaning up remaining placeholder files...")
    cleaned = 0
    
    for png_file in ALBUM_COVERS_DIR.glob("*.png"):
        jpg_file = png_file.with_suffix('.jpg')
        if jpg_file.exists():
            png_file.unlink()
            cleaned += 1
            print(f"  Removed: {png_file.name}")
    
    for png_file in ARTIST_IMAGES_DIR.glob("*.png"):
        jpg_file = png_file.with_suffix('.jpg')
        if jpg_file.exists():
            png_file.unlink()
            cleaned += 1
            print(f"  Removed: {png_file.name}")
    
    print(f"\n✓ Cleaned up {cleaned} placeholder files")

if __name__ == '__main__':
    update_media_paths()

