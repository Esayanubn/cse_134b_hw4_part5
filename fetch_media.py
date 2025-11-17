#!/usr/bin/env python3
"""
Fetch media files (album covers, artist images) for the music blog.
Uses Last.fm API and other sources to download images.
"""

import json
import os
import requests
from pathlib import Path
from urllib.parse import quote
import time

# Configuration
LASTFM_API_KEY = "1be3c088d23460678bef28cff5e13eb2"  # Get free API key from https://www.last.fm/api
LASTFM_API_URL = "http://ws.audioscrobbler.com/2.0/"
MUSIC_DATA_PATH = "new_blog/src/data/music-data.json"
MEDIA_DIR = Path("new_blog/public/media")
ALBUM_COVERS_DIR = MEDIA_DIR / "albums"
ARTIST_IMAGES_DIR = MEDIA_DIR / "artists"

# Create directories
ALBUM_COVERS_DIR.mkdir(parents=True, exist_ok=True)
ARTIST_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

def slugify(text):
    """Convert text to URL-friendly slug."""
    import re
    if not text:
        return 'unknown'
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.lower().strip('-')

def get_lastfm_album_cover(artist, album):
    """Get album cover from Last.fm API."""
    if not LASTFM_API_KEY or LASTFM_API_KEY == "YOUR_LASTFM_API_KEY":
        return None
    
    try:
        params = {
            'method': 'album.getinfo',
            'api_key': LASTFM_API_KEY,
            'artist': artist,
            'album': album,
            'format': 'json'
        }
        response = requests.get(LASTFM_API_URL, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'album' in data and 'image' in data['album']:
                images = data['album']['image']
                # Get the largest image (usually the last one)
                for img in reversed(images):
                    if img.get('#text'):
                        return img['#text']
    except Exception as e:
        print(f"Error fetching Last.fm album cover for {artist} - {album}: {e}")
    return None

def get_lastfm_artist_image(artist):
    """Get artist image from Last.fm API."""
    if not LASTFM_API_KEY or LASTFM_API_KEY == "YOUR_LASTFM_API_KEY":
        return None
    
    try:
        params = {
            'method': 'artist.getinfo',
            'api_key': LASTFM_API_KEY,
            'artist': artist,
            'format': 'json'
        }
        response = requests.get(LASTFM_API_URL, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'artist' in data and 'image' in data['artist']:
                images = data['artist']['image']
                # Get the largest image (usually the last one)
                for img in reversed(images):
                    if img.get('#text'):
                        return img['#text']
    except Exception as e:
        print(f"Error fetching Last.fm artist image for {artist}: {e}")
    return None

def download_image(url, filepath):
    """Download image from URL."""
    try:
        response = requests.get(url, timeout=10, stream=True)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
    return False

def generate_placeholder_image(text, filepath, size=(400, 400)):
    """Generate a placeholder image with text."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new('RGB', size, color=(102, 126, 234))
        draw = ImageDraw.Draw(img)
        
        # Try to use a nice font, fallback to default
        try:
            font_size = 60
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            font = ImageFont.load_default()
        
        # Get text dimensions
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center the text
        position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
        draw.text(position, text, fill=(255, 255, 255), font=font)
        
        img.save(filepath, 'PNG')
        return True
    except ImportError:
        print("PIL/Pillow not installed. Install with: pip install Pillow")
        return False
    except Exception as e:
        print(f"Error generating placeholder: {e}")
        return False

def process_albums(music_data):
    """Process albums and download covers."""
    print("Processing albums...")
    album_media = {}
    
    for album in music_data.get('albums', []):
        album_slug = album.get('slug', slugify(album['name']))
        cover_path = ALBUM_COVERS_DIR / f"{album_slug}.jpg"
        
        # Skip if already exists
        if cover_path.exists():
            album_media[album['name']] = f"/media/albums/{album_slug}.jpg"
            continue
        
        # Try to get from Last.fm
        image_url = get_lastfm_album_cover(album['artist'], album['name'])
        
        if image_url and download_image(image_url, cover_path):
            album_media[album['name']] = f"/media/albums/{album_slug}.jpg"
            print(f"✓ Downloaded cover for: {album['name']}")
        else:
            # Generate placeholder
            placeholder_path = ALBUM_COVERS_DIR / f"{album_slug}.png"
            if generate_placeholder_image(album['name'][:20], placeholder_path):
                album_media[album['name']] = f"/media/albums/{album_slug}.png"
                print(f"✓ Generated placeholder for: {album['name']}")
        
        time.sleep(0.2)  # Rate limiting
    
    return album_media

def process_artists(music_data):
    """Process artists and download images."""
    print("Processing artists...")
    artist_media = {}
    
    for artist in music_data.get('artists', []):
        artist_slug = artist.get('slug', slugify(artist['name']))
        image_path = ARTIST_IMAGES_DIR / f"{artist_slug}.jpg"
        
        # Skip if already exists
        if image_path.exists():
            artist_media[artist['name']] = f"/media/artists/{artist_slug}.jpg"
            continue
        
        # Try to get from Last.fm
        image_url = get_lastfm_artist_image(artist['name'])
        
        if image_url and download_image(image_url, image_path):
            artist_media[artist['name']] = f"/media/artists/{artist_slug}.jpg"
            print(f"✓ Downloaded image for: {artist['name']}")
        else:
            # Generate placeholder with first letter
            placeholder_path = ARTIST_IMAGES_DIR / f"{artist_slug}.png"
            first_letter = artist['name'][0].upper() if artist['name'] else '?'
            if generate_placeholder_image(first_letter, placeholder_path):
                artist_media[artist['name']] = f"/media/artists/{artist_slug}.png"
                print(f"✓ Generated placeholder for: {artist['name']}")
        
        time.sleep(0.2)  # Rate limiting
    
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
    
    # Save updated data
    output_path = MUSIC_DATA_PATH.replace('.json', '_with_media.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Processed {len(album_media)} album covers")
    print(f"✓ Processed {len(artist_media)} artist images")
    print(f"✓ Updated data saved to {output_path}")
    print("\nNote: To use Last.fm API, get a free API key from https://www.last.fm/api")
    print("      and update LASTFM_API_KEY in this script.")

if __name__ == '__main__':
    main()

