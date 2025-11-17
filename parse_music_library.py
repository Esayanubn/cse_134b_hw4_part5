#!/usr/bin/env python3
"""
Parse iTunes Library.xml and extract top 200 songs by play count.
"""

import xml.etree.ElementTree as ET
import json
import re
from collections import defaultdict
from typing import Dict, List, Optional

def parse_plist_value(element):
    """Parse a plist value element."""
    tag = element.tag
    if tag == 'string':
        return element.text or ''
    elif tag == 'integer':
        return int(element.text) if element.text else 0
    elif tag == 'true':
        return True
    elif tag == 'false':
        return False
    elif tag == 'date':
        return element.text or ''
    elif tag == 'dict':
        result = {}
        i = 0
        children = list(element)
        while i < len(children):
            key_elem = children[i]
            if key_elem.tag == 'key' and i + 1 < len(children):
                key = key_elem.text
                value_elem = children[i + 1]
                result[key] = parse_plist_value(value_elem)
                i += 2
            else:
                i += 1
        return result
    elif tag == 'array':
        return [parse_plist_value(child) for child in element]
    return None

def parse_tracks(xml_file: str) -> List[Dict]:
    """Parse tracks from iTunes Library.xml file."""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Find the dict element (plist structure)
    plist_dict = root.find('dict')
    if plist_dict is None:
        return []
    
    # Parse the plist structure
    library_dict = parse_plist_value(plist_dict)
    
    # Get tracks dictionary
    tracks_dict = library_dict.get('Tracks', {})
    
    tracks = []
    for track_id, track_data in tracks_dict.items():
        if not isinstance(track_data, dict):
            continue
            
        # Extract track information
        track = {
            'id': str(track_data.get('Track ID', track_id)),
            'name': track_data.get('Name', 'Unknown'),
            'artist': track_data.get('Artist', 'Unknown Artist'),
            'albumArtist': track_data.get('Album Artist', track_data.get('Artist', 'Unknown Artist')),
            'album': track_data.get('Album', 'Unknown Album'),
            'genre': track_data.get('Genre', 'Unknown'),
            'year': track_data.get('Year'),
            'duration': track_data.get('Total Time', 0),  # in milliseconds
            'releaseDate': track_data.get('Release Date', ''),
            'composer': track_data.get('Composer', ''),
            'playCount': track_data.get('Play Count', 0),
            'loved': track_data.get('Loved', False) or track_data.get('Favorited', False),
            'trackNumber': track_data.get('Track Number'),
            'discNumber': track_data.get('Disc Number', 1),
        }
        
        # Only include tracks with play count > 0
        if track['playCount'] > 0:
            tracks.append(track)
    
    return tracks

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    if not text:
        return 'unknown'
    # Remove special characters and convert to lowercase
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.lower().strip('-')

def generate_music_data(tracks: List[Dict]) -> Dict:
    """Generate structured music data for the blog."""
    # Sort by play count descending
    sorted_tracks = sorted(tracks, key=lambda x: x['playCount'], reverse=True)[:200]
    
    # Organize by album, artist, and genre
    albums = defaultdict(list)
    artists = defaultdict(list)
    genres = defaultdict(list)
    
    for track in sorted_tracks:
        track_slug = slugify(track['name'])
        track['slug'] = track_slug
        
        album_key = track['album']
        artist_key = track['artist']
        genre_key = track['genre']
        
        albums[album_key].append(track)
        artists[artist_key].append(track)
        genres[genre_key].append(track)
    
    # Include ALL albums and artists from the top 200 tracks (not just top 20)
    # Sort by number of tracks for display purposes, but include all
    all_albums = sorted(albums.items(), key=lambda x: len(x[1]), reverse=True)
    all_artists = sorted(artists.items(), key=lambda x: len(x[1]), reverse=True)
    top_genres = sorted(genres.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    
    return {
        'tracks': sorted_tracks,
        'albums': [
            {
                'name': album_name,
                'slug': slugify(album_name),
                'artist': albums[album_name][0]['artist'] if albums[album_name] else 'Unknown',
                'year': albums[album_name][0].get('year'),
                'tracks': albums[album_name]
            }
            for album_name, _ in all_albums
        ],
        'artists': [
            {
                'name': artist_name,
                'slug': slugify(artist_name),
                'tracks': artists[artist_name]
            }
            for artist_name, _ in all_artists
        ],
        'genres': [
            {
                'name': genre_name,
                'slug': slugify(genre_name),
                'tracks': genres[genre_name]
            }
            for genre_name, _ in top_genres
        ]
    }

def main():
    xml_file = 'Library.xml'
    output_file = 'new_blog/src/data/music-data.json'
    
    print(f"Parsing {xml_file}...")
    tracks = parse_tracks(xml_file)
    print(f"Found {len(tracks)} tracks with play count > 0")
    
    print("Generating structured data...")
    music_data = generate_music_data(tracks)
    
    print(f"Top 200 tracks: {len(music_data['tracks'])}")
    print(f"All albums from top 200 tracks: {len(music_data['albums'])}")
    print(f"All artists from top 200 tracks: {len(music_data['artists'])}")
    print(f"Top genres: {len(music_data['genres'])}")
    
    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(music_data, f, ensure_ascii=False, indent=2)
    
    print(f"Data written to {output_file}")

if __name__ == '__main__':
    main()

