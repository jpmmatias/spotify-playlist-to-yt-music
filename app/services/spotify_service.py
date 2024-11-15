from fastapi import Request, HTTPException
from app.repositories.spotify_repository import SpotifyRepository
import os

class SpotifyService:
    def __init__(self, repository: SpotifyRepository):
        self.repository = repository
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    async def get_auth_url(self, request: Request) -> str:
        """Get Spotify authorization URL"""
        return self.repository.create_auth_url(self.client_id, request)

    async def get_user_profile(self, code: str, request: Request) -> dict:
        """Get user profile and store access token"""
        access_token = self.repository.get_access_token(self.client_id, code, request)
        request.session['access_token'] = access_token
        profile = self.repository.get_profile(access_token)
        request.session['profile'] = profile
        return profile

    async def get_user_playlists(self, request: Request, limit: int = 50, offset: int = 0) -> dict:
        """Get user's playlists"""
        access_token = request.session.get('access_token')
        if not access_token:
            raise HTTPException(status_code=401, detail="Not authenticated. Please login first")
        return self.repository.get_user_playlists(access_token, limit, offset)

    async def get_playlist(self, playlist_id: str, request: Request) -> dict:
        """Get a specific playlist"""
        access_token = request.session.get('access_token')
        if not access_token:
            raise HTTPException(status_code=401, detail="Not authenticated. Please login first")
        return self.repository.get_playlist(access_token, playlist_id)
  