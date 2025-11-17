export interface Track {
	id: string;
	name: string;
	artist: string;
	albumArtist: string;
	album: string;
	genre: string;
	year: number | null;
	duration: number;
	releaseDate: string;
	composer: string;
	playCount: number;
	loved: boolean;
	trackNumber: number | null;
	discNumber: number;
	slug: string;
	albumCover?: string;
}

export interface Album {
	name: string;
	slug: string;
	artist: string;
	year: number | null;
	tracks: Track[];
	coverImage?: string;
}

export interface Artist {
	name: string;
	slug: string;
	tracks: Track[];
	image?: string;
}

export interface Genre {
	name: string;
	slug: string;
	tracks: Track[];
}

export interface MusicData {
	tracks: Track[];
	albums: Album[];
	artists: Artist[];
	genres: Genre[];
}

