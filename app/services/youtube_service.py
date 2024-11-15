from app.repositories.youtube_repository import YouTubeMusicRepository
from typing import List, Dict
from fastapi import Request

class YouTubeMusicService:
    def __init__(self, repository: YouTubeMusicRepository):
        self.repository = repository

    async def authenticate(self, headers_raw: str, request: Request):
        """Authenticate with YouTube Music"""
        return self.repository.authenticate(headers_raw, request)

    async def convert_spotify_playlist(self, playlist: Dict, request: Request) -> str:
        """Convert a Spotify playlist to YouTube Music"""
        # Create new playlist
        playlist_id = self.repository.create_playlist(
            title=f"{playlist['name']} (from Spotify)",
            description=f"Converted from Spotify playlist: {playlist['name']}",
            request=request
        )

        # Convert each track
        video_ids = []
        for track in playlist['tracks']['items']:
            track_info = track['track']
            search_query = f"{track_info['name']} {' '.join(artist['name'] for artist in track_info['artists'])}"
            
            # Search for equivalent song on YouTube Music
            result = self.repository.search_song(search_query, request)
            if result and 'videoId' in result:
                video_ids.append(result['videoId'])

        # Add all found songs to the playlist
        if video_ids:
            self.repository.add_playlist_items(playlist_id, video_ids, request)

        return playlist_id 