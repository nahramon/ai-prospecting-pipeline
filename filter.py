import os
from googleapiclient.discovery import build
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=API_KEY)

PALABRAS_DESCARTE = [
    "#shorts", "shorts", "reaction", "reaccion", "reacción",
    "react", "vlog", "haul", "unboxing", "challenge", "meme",
    "compilation", "compilacion", "compilación", "clip", "tiktok"
]

def obtener_ultimos_videos(playlist_id, cantidad=5):
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=cantidad
    )
    response = request.execute()
    
    videos = []
    for item in response["items"]:
        titulo = item["snippet"]["title"].lower()
        videos.append(titulo)
    return videos

def es_formato_largo(videos):
    """Retorna True si el canal publica formato largo como contenido principal."""
    if not videos:
        return False
    
    shorts_count = 0
    for titulo in videos:
        for palabra in PALABRAS_DESCARTE:
            if palabra in titulo:
                shorts_count += 1
                break
    
    # Descarta solo si MÁS DEL 60% son shorts/reacciones
    return (shorts_count / len(videos)) < 0.6

def filtrar_formato(canales):
    """Recibe lista de canales aprobados por scout y aplica filtro de formato."""
    aprobados = []
    descartados = []

    for c in canales:
        print(f"  Analizando formato: {c['nombre']}...")
        
        # Necesitamos la playlist de uploads
        request = youtube.channels().list(
            part="contentDetails",
            id=c["canal_id"]
        )
        response = request.execute()
        
        if not response["items"]:
            continue
        
        playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        videos = obtener_ultimos_videos(playlist_id, cantidad=10)
        
        if es_formato_largo(videos):
            aprobados.append(c)
        else:
            descartados.append(c)
            print(f"    ✗ Descartado por formato — últimos títulos: {videos[:2]}")

    return aprobados, descartados