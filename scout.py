import os
from googleapiclient.discovery import build
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=API_KEY)

# ── NICHOS Y KEYWORDS ──────────────────────────────────────────────────────────
NICHOS = {
    "1": {
        "nombre": "Historia",
        "subnichos": {
            "1": {"nombre": "Historia antigua",          "keywords": ["ancient history documentary", "ancient civilizations explained", "historia antigua documental"]},
            "2": {"nombre": "Historia medieval",         "keywords": ["medieval history documentary", "middle ages explained", "historia medieval documental"]},
            "3": {"nombre": "Segunda Guerra Mundial",    "keywords": ["world war 2 documentary", "wwii history channel", "segunda guerra mundial documental"]},
            "4": {"nombre": "Imperios y civilizaciones", "keywords": ["empire history documentary", "lost civilizations youtube", "imperios historia documental"]},
            "5": {"nombre": "Biografías históricas",     "keywords": ["historical biography documentary", "history biography channel", "biografias historicas youtube"]},
        }
    },
    "2": {
        "nombre": "True Crime",
        "subnichos": {
            "1": {"nombre": "Cold cases",           "keywords": ["cold case documentary youtube", "unsolved murder documentary", "casos sin resolver documental"]},
            "2": {"nombre": "Serial killers",       "keywords": ["serial killer documentary", "true crime serial killer youtube"]},
            "3": {"nombre": "Investigación criminal","keywords": ["criminal investigation documentary", "crime investigation youtube"]},
            "4": {"nombre": "Conspiraciones",       "keywords": ["conspiracy documentary youtube", "conspiracy investigation channel"]},
        }
    },
    "3": {
        "nombre": "Ciencia",
        "subnichos": {
            "1": {"nombre": "Astronomía y espacio", "keywords": ["astronomy documentary youtube", "space science channel", "astronomia documental"]},
            "2": {"nombre": "Neurociencia",         "keywords": ["neuroscience explained youtube", "brain science documentary"]},
            "3": {"nombre": "Física y matemáticas", "keywords": ["physics explained youtube", "mathematics documentary channel"]},
            "4": {"nombre": "Biología y evolución", "keywords": ["biology evolution documentary", "evolution science youtube"]},
        }
    },
    "4": {
        "nombre": "Filosofía",
        "subnichos": {
            "1": {"nombre": "Filosofía práctica",        "keywords": ["philosophy explained youtube", "practical philosophy channel"]},
            "2": {"nombre": "Ética y moral",             "keywords": ["ethics morality youtube", "moral philosophy channel"]},
            "3": {"nombre": "Historia de la filosofía",  "keywords": ["history of philosophy documentary", "philosophers explained youtube"]},
            "4": {"nombre": "Estoicismo",                "keywords": ["stoicism youtube channel", "stoic philosophy explained"]},
        }
    },
    "5": {
        "nombre": "Desarrollo personal",
        "subnichos": {
            "1": {"nombre": "Psicología",          "keywords": ["psychology explained youtube", "psychology documentary channel"]},
            "2": {"nombre": "Productividad",       "keywords": ["productivity systems youtube", "productivity creator channel"]},
            "3": {"nombre": "Espiritualidad",      "keywords": ["spirituality youtube channel", "consciousness awakening youtube"]},
            "4": {"nombre": "Bienestar",           "keywords": ["wellbeing documentary youtube", "mental health explained channel"]},
        }
    },
}

# ── FUNCIONES ──────────────────────────────────────────────────────────────────
def obtener_detalles_canales(canal_ids):
    request = youtube.channels().list(
        part="snippet,statistics,contentDetails",
        id=",".join(canal_ids)
    )
    response = request.execute()
    detalles = {}
    for item in response["items"]:
        cid = item["id"]
        stats = item.get("statistics", {})
        snippet = item.get("snippet", {})
        detalles[cid] = {
            "suscriptores": int(stats.get("subscriberCount", 0)),
            "pais": snippet.get("country", "N/A"),
            "uploads_playlist": item["contentDetails"]["relatedPlaylists"]["uploads"]
        }
    return detalles

def obtener_ultimo_video(playlist_id):
    # Traemos los últimos 10 para encontrar el último video largo
    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=10
    )
    response = request.execute()
    
    if not response["items"]:
        return None, None, None

    PALABRAS_CORTO = ["#shorts", "#short", "shorts", " short"]

    for item in response["items"]:
        titulo = item["snippet"]["title"]
        titulo_lower = titulo.lower()
        
        # Saltear si es short
        if any(p in titulo_lower for p in PALABRAS_CORTO):
            continue
        
        descripcion = item["snippet"]["description"][:500]
        fecha_str = item["snippet"]["publishedAt"]
        fecha = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
        dias = (datetime.now(timezone.utc) - fecha).days
        return titulo, dias, descripcion

    # Si todos son shorts, devolver el primero igual
    item = response["items"][0]
    titulo = item["snippet"]["title"]
    descripcion = item["snippet"]["description"][:500]
    fecha_str = item["snippet"]["publishedAt"]
    fecha = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
    dias = (datetime.now(timezone.utc) - fecha).days
    return titulo, dias, descripcion

def buscar_por_keyword(keyword, max_results=15):
    request = youtube.search().list(
        part="snippet",
        q=keyword,
        type="video",
        maxResults=max_results,
        videoDuration="long"
    )
    response = request.execute()
    
    canales = []
    vistos = set()
    for item in response["items"]:
        canal_id = item["snippet"]["channelId"]
        canal_nombre = item["snippet"]["channelTitle"]
        
        if canal_id not in vistos:
            vistos.add(canal_id)
            canales.append({
                "nombre": canal_nombre,
                "canal_id": canal_id,
            })
    
    return canales

def aplicar_filtros(canales_base):
    from blacklist import cargar_blacklist, esta_en_blacklist
    blacklist = cargar_blacklist()
    
    ids = list({c["canal_id"] for c in canales_base})
    detalles = {}
    for i in range(0, len(ids), 50):
        detalles.update(obtener_detalles_canales(ids[i:i+50]))

    aprobados = []
    vistos = set()

    for c in canales_base:
        cid = c["canal_id"]
        if cid in vistos or cid not in detalles:
            continue
        vistos.add(cid)

        # Blacklist
        if esta_en_blacklist(cid, blacklist):
            print(f"  ✗ Blacklist: {c['nombre']}")
            continue

        d = detalles[cid]
        subs = d["suscriptores"]

        if subs < 50_000 or subs > 5_000_000:
            continue

        titulo_video, dias, descripcion_video  = obtener_ultimo_video(d["uploads_playlist"])
        if dias is None or dias > 30:
            continue

        aprobados.append({
            "nombre": c["nombre"],
            "canal_id": cid,
            "suscriptores": subs,
            "pais": d["pais"],
            "dias_desde_ultimo_video": dias,
            "titulo_ultimo_video": titulo_video,
            "descripcion_ultimo_video": descripcion_video or ""
        })

    return aprobados

def mostrar_resultados(aprobados):
    if not aprobados:
        print("\nNingún canal pasó los filtros.")
        return
    print(f"\n{'Canal':<40} {'Subs':>10} {'País':>6} {'Último video':>14} {'Título último video'}")
    print("-" * 110)
    for c in sorted(aprobados, key=lambda x: x["suscriptores"]):
        dias_str = f"{c['dias_desde_ultimo_video']}d"
        titulo_str = (c["titulo_ultimo_video"][:50] + "...") if c["titulo_ultimo_video"] and len(c["titulo_ultimo_video"]) > 50 else (c["titulo_ultimo_video"] or "N/A")
        print(f"{c['nombre']:<40} {c['suscriptores']:>10,} {c['pais']:>6} {dias_str:>14} {titulo_str}")
    print(f"\nTotal aprobados: {len(aprobados)}")

# ── MENÚ INTERACTIVO ───────────────────────────────────────────────────────────
def menu():
    print("\n=== PROSPECCIÓN NAHUEL — SCOUT ===\n")
    print("¿Qué nicho querés prospectar?\n")
    for k, v in NICHOS.items():
        print(f"  {k}. {v['nombre']}")
    print()

    nicho_key = input("Elegí un número: ").strip()
    if nicho_key not in NICHOS:
        print("Opción inválida.")
        return

    nicho = NICHOS[nicho_key]
    print(f"\nSubnichos de {nicho['nombre']}:\n")
    for k, v in nicho["subnichos"].items():
        print(f"  {k}. {v['nombre']}")
    print(f"  0. Todos")
    print()

    sub_key = input("Elegí un número: ").strip()

    if sub_key == "0":
        keywords = [kw for s in nicho["subnichos"].values() for kw in s["keywords"]]
    elif sub_key in nicho["subnichos"]:
        keywords = nicho["subnichos"][sub_key]["keywords"]
    else:
        print("Opción inválida.")
        return

    print(f"\nBuscando con {len(keywords)} keywords...\n")
    canales_base = []
    for kw in keywords:
        print(f"  → {kw}")
        canales_base.extend(buscar_por_keyword(kw))

    print(f"\nCanales encontrados (con duplicados): {len(canales_base)}")
    print("Aplicando filtros...\n")

    aprobados = aplicar_filtros(canales_base)
    mostrar_resultados(aprobados)
    return aprobados

if __name__ == "__main__":
    from filter import filtrar_formato
    from analyze import analizar_lista
    from sample import proponer_temas_lista
    from message import redactar_mensajes_lista
    from contact import buscar_contactos_lista
    from export import exportar

    canales = menu()

    if canales:
        print("\nAplicando filtro de formato...\n")
        aprobados_formato, _ = filtrar_formato(canales)

        if aprobados_formato:
            aprobados_finales = analizar_lista(aprobados_formato)

            if aprobados_finales:
                aprobados_con_tema = proponer_temas_lista(aprobados_finales)
                aprobados_con_mensaje = redactar_mensajes_lista(aprobados_con_tema)
                aprobados_con_contacto = buscar_contactos_lista(aprobados_con_mensaje)
                exportar(aprobados_con_contacto)
        
    menu()