import requests
import urllib.parse
import secrets
import base64
import hashlib
from fastapi import Request

class SpotifyRepository:
    def generate_code_verifier(self, length: int) -> str:
        token = secrets.token_urlsafe(length)
        return token

    def generate_code_challenge(self, verifier: str) -> str:
        sha256 = hashlib.sha256(verifier.encode('utf-8')).digest()
        encoded = base64.urlsafe_b64encode(sha256).decode('utf-8')
        return encoded.replace('=', '')

    def create_auth_url(self, client_id: str, request: Request) -> str:
        verifier = self.generate_code_verifier(64)
        challenge = self.generate_code_challenge(verifier)
        
        request.session['code_verifier'] = verifier
        
        params = {
            'client_id': client_id,
            'response_type': 'code',
            'redirect_uri': 'http://localhost:8000/callback',
            'scope': 'user-read-private user-read-email playlist-read-private playlist-read-collaborative',
            'code_challenge_method': 'S256',
            'code_challenge': challenge
        }
        
        return f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"

    def get_access_token(self, client_id: str, code: str, request: Request) -> str:
        verifier = request.session.get('code_verifier')
        if not verifier:
            raise Exception("No code verifier found in session")
        
        params = {
            'client_id': client_id,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': 'http://localhost:8000/callback',
            'code_verifier': verifier
        }
        
        response = requests.post(
            'https://accounts.spotify.com/api/token',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=params
        )
        
        if response.status_code != 200:
            print("Token Error:", response.json())
            raise Exception(f"Failed to get access token: {response.json()}")
            
        return response.json()['access_token']

    def get_profile(self, token: str) -> dict:
        response = requests.get(
            'https://api.spotify.com/v1/me',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code != 200:
            print("Profile Error:", response.json())
            raise Exception("Failed to get user profile")
            
        return response.json()

    def get_user_playlists(self, token: str, limit: int = 50, offset: int = 0) -> dict:
        response = requests.get(
            'https://api.spotify.com/v1/me/playlists',
            headers={'Authorization': f'Bearer {token}'},
            params={
                'limit': limit,
                'offset': offset
            }
        )
        
        if response.status_code != 200:
            print("Playlist Error:", response.json())
            raise Exception("Failed to get playlists")
            
        return response.json()

    def get_playlist(self, token: str, playlist_id: str) -> dict:
        """Get a specific playlist and its tracks"""
        response = requests.get(
            f'https://api.spotify.com/v1/playlists/{playlist_id}',
            headers={'Authorization': f'Bearer {token}'},
            params={
                'fields': 'name,description,tracks.items(track(name,artists(name)))'  # Only get the fields we need
            }
        )
        
        if response.status_code != 200:
            print("Playlist Error:", response.json())
            raise Exception("Failed to get playlist")
            
        return response.json() 