import type { MusicData } from '../types';
import musicDataJson from '../data/music-data.json';

const musicData = musicDataJson as MusicData;

export function findArtistSlug(artistName: string): string {
	const artist = musicData.artists.find(a => a.name === artistName);
	return artist?.slug || artistName.toLowerCase().replace(/\s+/g, '-');
}

export function findAlbumSlug(albumName: string): string {
	const album = musicData.albums.find(a => a.name === albumName);
	return album?.slug || albumName.toLowerCase().replace(/\s+/g, '-');
}

export function findGenreSlug(genreName: string): string {
	const genre = musicData.genres.find(g => g.name === genreName);
	return genre?.slug || genreName.toLowerCase().replace(/\s+/g, '-');
}

