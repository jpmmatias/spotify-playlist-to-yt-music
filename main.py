from fastapi import FastAPI, Request, Depends
from fastapi.responses import  RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.spotify_service import SpotifyService
from app.services.youtube_service import YouTubeMusicService
from dependencies import get_spotify_service, get_youtube_service

import secrets
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Generate a random secret key if not provided in environment
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))

class SessionIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if "session" in request.scope:
            # Always ensure there's a session ID
            if "session_id" not in request.session:
                request.session["session_id"] = str(uuid.uuid4())
                print(f"[Debug] New session ID created: {request.session['session_id']}")
            else:
                print(f"[Debug] Existing session ID: {request.session['session_id']}")
            
            print(f"[Debug] Current session state: {dict(request.session)}")
        
        response = await call_next(request)
        return response

app = FastAPI()

# Configure session middleware with more specific settings
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY"),
    session_cookie=os.getenv("SESSION_COOKIE_NAME"),
    max_age=int(os.getenv("SESSION_MAX_AGE")),
    same_site=os.getenv("SESSION_COOKIE_SAMESITE"),
    https_only=os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true",
)

# Add other middleware
app.add_middleware(SessionIDMiddleware)
app.add_middleware(GZipMiddleware)

CLIENT_SECRET = "ddac68e03229404ebab017782dba40ac"

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def login(
    request: Request,
    spotify_service: SpotifyService = Depends(get_spotify_service)
):
    auth_url = await spotify_service.get_auth_url(request)
    return RedirectResponse(auth_url)

@app.get("/callback")
async def callback(
    request: Request,
    code: str,
    spotify_service: SpotifyService = Depends(get_spotify_service)
):
    try:
        # Get user profile and store in session
        profile = await spotify_service.get_user_profile(code, request)
        
        # Add debug logging
        print("Spotify callback - Session state:", dict(request.session))
        print("Profile stored:", profile)
        
        # Use absolute URL for redirect
        return RedirectResponse(
            url="/playlists",
            status_code=303  # Using 303 See Other for POST-to-GET redirect
        )
    except Exception as e:
        print(f"Callback error: {str(e)}")
        return RedirectResponse(
            url="/?error=Authentication failed",
            status_code=303
        )

@app.get("/playlists")
async def get_playlists(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    spotify_service: SpotifyService = Depends(get_spotify_service)
):
    profile = request.session.get('profile')
    if not profile:
        return RedirectResponse("/login")
        
    playlists = await spotify_service.get_user_playlists(request, limit, offset)
    return templates.TemplateResponse(
        "spotify_playlists.html",
        {
            "request": request,
            "playlists": playlists['items'],
            "profile": profile
        }
    )

@app.post("/youtube/auth")
async def youtube_auth(
    request: Request,
    youtube_service: YouTubeMusicService = Depends(get_youtube_service)
):
    try:
        print(f"[Debug] Auth - Current session before: {dict(request.session)}")
        
        body = await request.json()
        headers_raw = body.get('headers_raw', '')
        
        # Ensure session ID exists
        if 'session_id' not in request.session:
            request.session['session_id'] = str(uuid.uuid4())
            print(f"[Debug] Created new session ID: {request.session['session_id']}")
        
        # Authenticate and verify it worked
        await youtube_service.authenticate(headers_raw, request)
        
        print(f"[Debug] Auth - Current session after: {dict(request.session)}")
        return {"status": "success"}
            
    except Exception as e:
        print(f"[Debug] Auth error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": str(e)}
        )

@app.post("/convert/{playlist_id}")
async def convert_playlist(
    playlist_id: str,
    request: Request,
    spotify_service: SpotifyService = Depends(get_spotify_service),
    youtube_service: YouTubeMusicService = Depends(get_youtube_service)
):
    try:
        print("[Debug] Starting playlist conversion")
        
        # Check YouTube authentication without using session
        if not youtube_service.repository.is_authenticated():
            print("[Debug] YouTube Music not authenticated!")
            return JSONResponse(
                status_code=401,
                content={"status": "error", "message": "Please authenticate with YouTube Music first"}
            )

        print("[Debug] Getting playlist from Spotify...")
        playlist = await spotify_service.get_playlist(playlist_id, request)
        
        print("[Debug] Converting to YouTube Music...")
        youtube_playlist_id = await youtube_service.convert_spotify_playlist(playlist, request)
        
        print("[Debug] Conversion successful!")
        return {
            "status": "success",
            "youtube_playlist_id": youtube_playlist_id
        }
    except Exception as e:
        print(f"[Debug] Conversion error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": str(e)}
        )

# Load environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")