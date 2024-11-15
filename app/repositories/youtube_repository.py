from ytmusicapi import YTMusic
import ytmusicapi
from typing import List, Dict, Optional
import json
import re
import os
from fastapi import Request
import threading

class YouTubeMusicRepository:
    _lock = threading.Lock()
    _instance = None
    _ytmusic: Optional[YTMusic] = None
    _is_authenticated = False
    BROWSER_JSON_PATH = "browser.json"  # Path to store browser.json

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def _parse_curl_headers(self, headers_raw: str) -> str:
        """Parse cURL command and return headers in ytmusicapi format"""
        try:
            print("[Debug] Parsing cURL command...")
            
            # Extract headers from cURL command
            headers = {}
            lines = headers_raw.split('\n')
            
            for line in lines:
                line = line.strip()
                if "'-H '" in line or '"-H "' in line or line.startswith('-H '):
                    # Extract the header content
                    header_content = line.split("'")[-2] if "'" in line else line.split('"')[-2]
                    if ':' in header_content:
                        key, value = header_content.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        headers[key] = value

            # Required headers for YTMusic
            required_headers = {
                'accept': '*/*',
                'accept-language': headers.get('Accept-Language', 'en-US,en;q=0.9'),
                'authorization': headers.get('Authorization', ''),
                'content-type': 'application/json',
                'cookie': headers.get('Cookie', ''),
                'user-agent': headers.get('User-Agent', ''),
                'x-goog-authuser': headers.get('X-Goog-AuthUser', '0'),
                'x-goog-visitor-id': headers.get('X-Goog-Visitor-Id', ''),
                'x-origin': 'https://music.youtube.com'
            }

            # Verify required headers
            if not headers.get('Cookie'):
                raise Exception("Cookie header is missing")
            if not headers.get('X-Goog-AuthUser'):
                raise Exception("X-Goog-AuthUser header is missing")

            # Format headers for ytmusicapi
            formatted_headers = '\n'.join(f"{k}: {v}" for k, v in required_headers.items())

            print("[Debug] Headers formatted successfully")
            print("[Debug] Cookie length:", len(headers.get('Cookie', '')))
            print("[Debug] X-Goog-AuthUser value:", headers.get('X-Goog-AuthUser'))
            
            return formatted_headers

        except Exception as e:
            print(f"[Debug] Header parsing error: {str(e)}")
            raise Exception(
                "Failed to parse headers. Please ensure you copied the full cURL command "
                "and that you are logged into YouTube Music."
            )

    def authenticate(self, headers_raw: str, request: Request = None):
        """Authenticate with YouTube Music using browser headers"""
        try:
            print("[Debug] Starting YouTube Music authentication")
            with self.__class__._lock:
                # Parse and format headers
                formatted_headers = self._parse_curl_headers(headers_raw)
                print("[Debug] Headers parsed and formatted")
                
                # Setup YTMusic with formatted headers
                print("[Debug] Setting up browser.json...")
                auth_str = ytmusicapi.setup(
                    filepath=self.BROWSER_JSON_PATH,
                    headers_raw=formatted_headers
                )
                print("[Debug] browser.json created successfully")
                
                # Initialize YTMusic with the browser.json file
                print("[Debug] Initializing YTMusic with browser.json...")
                self.__class__._ytmusic = YTMusic(auth=self.BROWSER_JSON_PATH)
                
                # Test the connection
                print("[Debug] Testing YTMusic connection...")
                try:
                    self.__class__._ytmusic.get_home()
                    print("[Debug] YTMusic connection successful")
                except Exception as e:
                    print(f"[Debug] Connection test failed: {str(e)}")
                    raise Exception("Failed to verify YouTube Music connection")
                
                self.__class__._is_authenticated = True
                
                # Store authentication in session if request is provided
                if request and hasattr(request, 'session'):
                    request.session['youtube_authenticated'] = True
                    print("[Debug] Authentication stored in session")
                
                print("[Debug] Authentication data stored successfully")
                return self.__class__._ytmusic
                
        except Exception as e:
            print(f"[Debug] Authentication failed: {str(e)}")
            self._clear_auth(request)
            raise Exception(f"Failed to authenticate with YouTube Music: {str(e)}")

    def _ensure_authenticated(self, request: Request = None):
        """Ensure YouTube Music is authenticated"""
        try:
            with self.__class__._lock:
                # Check session first if request is provided
                if request and hasattr(request, 'session'):
                    if not request.session.get('youtube_authenticated'):
                        raise Exception("YouTube Music session expired")

                if not self.__class__._is_authenticated or not self.__class__._ytmusic:
                    print("[Debug] No valid YTMusic instance")
                    if os.path.exists(self.BROWSER_JSON_PATH):
                        print("[Debug] Found browser.json, reinitializing YTMusic")
                        try:
                            self.__class__._ytmusic = YTMusic(auth=self.BROWSER_JSON_PATH)
                            # Test connection
                            self.__class__._ytmusic.get_home()
                            self.__class__._is_authenticated = True
                            if request and hasattr(request, 'session'):
                                request.session['youtube_authenticated'] = True
                        except Exception as e:
                            print(f"[Debug] Reinitialization failed: {str(e)}")
                            raise Exception("Failed to reinitialize YouTube Music - Please re-authenticate")
                    else:
                        raise Exception("No YouTube Music authentication found")
                
                # Verify connection is still valid
                print("[Debug] Testing YTMusic connection...")
                try:
                    self.__class__._ytmusic.get_home()
                    print("[Debug] YTMusic connection successful")
                except Exception as e:
                    print(f"[Debug] Connection test failed: {str(e)}")
                    self._clear_auth(request)
                    raise Exception("YouTube Music connection failed - Please re-authenticate")
                
                return True
                
        except Exception as e:
            print(f"[Debug] Authentication error: {str(e)}")
            self._clear_auth(request)
            raise Exception(str(e))

    def _clear_auth(self, request: Request = None):
        """Clear authentication data"""
        with self.__class__._lock:
            self.__class__._ytmusic = None
            self.__class__._is_authenticated = False
            
            # Clear session if request is provided
            if request and hasattr(request, 'session'):
                request.session.pop('youtube_authenticated', None)
                print("[Debug] Cleared YouTube Music session")
            
            # Remove browser.json if it exists
            if os.path.exists(self.BROWSER_JSON_PATH):
                try:
                    os.remove(self.BROWSER_JSON_PATH)
                    print("[Debug] Removed browser.json file")
                except Exception as e:
                    print(f"[Debug] Error removing browser.json: {str(e)}")

    def is_authenticated(self) -> bool:
        """Check if YouTube Music is authenticated"""
        return self.__class__._is_authenticated and os.path.exists(self.BROWSER_JSON_PATH)

    def create_playlist(self, title: str, description: str, request: Request) -> str:
        """Create a new playlist and return its ID"""
        self._ensure_authenticated(request)
        return self.__class__._ytmusic.create_playlist(title, description)

    def search_song(self, query: str, request: Request) -> Dict:
        """Search for a song and return the first result"""
        self._ensure_authenticated(request)
        results = self.__class__._ytmusic.search(query, filter="songs", limit=1)
        return results[0] if results else None

    def add_playlist_items(self, playlist_id: str, video_ids: List[str], request: Request) -> bool:
        """Add songs to a playlist"""
        self._ensure_authenticated(request)
        self.__class__._ytmusic.add_playlist_items(playlist_id, video_ids)
        return True 