@router.post("/create-playlist")
async def create_playlist(
    request: Request,
    playlist_data: dict,
    youtube_service: YouTubeService = Depends(get_youtube_service)
):
    try:
        print("[Debug] Received create playlist request")
        print("[Debug] Playlist data:", playlist_data)
        
        spotify_playlist_id = playlist_data.get('spotify_playlist_id')
        if not spotify_playlist_id:
            raise HTTPException(status_code=400, detail="Missing spotify_playlist_id")
            
        # Get Spotify playlist details
        spotify_playlist = await spotify_service.get_playlist(spotify_playlist_id, request)
        print("[Debug] Got Spotify playlist:", spotify_playlist['name'])
        
        # Create YouTube Music playlist
        playlist_id = youtube_service.create_playlist(
            title=spotify_playlist['name'],
            description=f"Converted from Spotify playlist: {spotify_playlist['name']}",
            request=request
        )
        print("[Debug] Created YouTube playlist:", playlist_id)
        
        return {"playlist_id": playlist_id}
        
    except Exception as e:
        print("[Debug] Error in create_playlist endpoint:", str(e))
        raise HTTPException(status_code=500, detail=str(e)) 