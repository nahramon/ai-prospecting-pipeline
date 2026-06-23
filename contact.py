import re
import requests
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=API_KEY)

EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
URL_REGEX = r'https?://[^\s\)>"]+'

PALABRAS_CONTACTO = [
    "contact", "contacto", "business", "booking", 
    "inquiries", "mail", "email", "reach"
]

def extraer_email(texto):
    emails = re.findall(EMAIL_REGEX, texto)
    # Filtrar emails de YouTube y Google
    emails = [e for e in emails if "youtube" not in e and "google" not in e]
    return emails[0] if emails else None

def extraer_links(texto):
    links = re.findall(URL_REGEX, texto)
    # Filtrar links de YouTube, Google, Instagram, Twitter
    links = [l for l in links if not any(x in l for x in [
        "youtube.com", "google.com", "goo.gl", "youtu.be"
    ])]
    return links

def buscar_formulario_en_web(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        texto = response.text.lower()
        
        # Buscar links de contacto en la página
        links = re.findall(URL_REGEX, texto)
        for link in links:
            if any(palabra in link.lower() for palabra in PALABRAS_CONTACTO):
                return link
        
        # Si la página tiene formulario directo
        if "<form" in texto and any(p in texto for p in PALABRAS_CONTACTO):
            return url
            
    except Exception:
        pass
    return None

def buscar_instagram(descripcion, nombre_canal):
    # Buscar link de Instagram en la descripción
    if "instagram.com" in descripcion:
        links = re.findall(r'instagram\.com/[a-zA-Z0-9_.]+', descripcion)
        if links:
            return f"https://www.{links[0]}"
    return None

def obtener_contacto(canal):
    print(f"  Buscando contacto: {canal['nombre']}...")
    
    # Obtener descripción completa del canal
    request = youtube.channels().list(
        part="snippet,brandingSettings",
        id=canal["canal_id"]
    )
    response = request.execute()
    
    if not response["items"]:
        return {"metodo": "YouTube DM", "valor": "", "instagram": ""}
    
    item = response["items"][0]
    descripcion = item["snippet"].get("description", "")
    
    # Paso 1: buscar email directo
    email = extraer_email(descripcion)
    if email:
        print(f"    ✓ Email encontrado: {email}")
        instagram = buscar_instagram(descripcion, canal["nombre"])
        return {
            "metodo": "Email",
            "valor": email,
            "instagram": instagram or ""
        }
    
    # Paso 2: buscar página web y formulario
    links = extraer_links(descripcion)
    for link in links:
        if any(x in link for x in ["instagram", "twitter", "x.com", "tiktok", "facebook", "linkedin", "spotify", "patreon"]):
            continue
        formulario = buscar_formulario_en_web(link)
        if formulario:
            print(f"    ✓ Formulario encontrado: {formulario}")
            instagram = buscar_instagram(descripcion, canal["nombre"])
            return {
                "metodo": "Formulario web",
                "valor": formulario,
                "instagram": instagram or ""
            }
        else:
            print(f"    ~ Web encontrada (sin formulario claro): {link}")
            instagram = buscar_instagram(descripcion, canal["nombre"])
            return {
                "metodo": "Página web",
                "valor": link,
                "instagram": instagram or ""
            }
    
    # Paso 3: fallback — Instagram o YouTube DM
    instagram = buscar_instagram(descripcion, canal["nombre"])
    if instagram:
        print(f"    ~ Solo Instagram: {instagram}")
        return {
            "metodo": "Instagram DM",
            "valor": instagram,
            "instagram": instagram
        }
    
    print(f"    ~ Sin contacto directo, usar YouTube DM")
    return {
        "metodo": "YouTube DM",
        "valor": f"https://www.youtube.com/channel/{canal['canal_id']}",
        "instagram": ""
    }

def buscar_contactos_lista(canales):
    print("\n=== BUSCANDO DATOS DE CONTACTO ===\n")
    for c in canales:
        contacto = obtener_contacto(c)
        c["contacto"] = contacto
    return canales