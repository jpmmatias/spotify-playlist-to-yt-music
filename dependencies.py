from fastapi import Depends
from app.repositories.spotify_repository import SpotifyRepository
from app.repositories.youtube_repository import YouTubeMusicRepository
from app.services.spotify_service import SpotifyService
from app.services.youtube_service import YouTubeMusicService

def get_spotify_repository():
    return SpotifyRepository()

def get_youtube_repository():
    return YouTubeMusicRepository()

def get_spotify_service(repository: SpotifyRepository = Depends(get_spotify_repository)):
    return SpotifyService(repository)

def get_youtube_service(repository: YouTubeMusicRepository = Depends(get_youtube_repository)):
    return YouTubeMusicService(repository) 