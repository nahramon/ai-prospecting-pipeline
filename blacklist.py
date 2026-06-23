import json
import os

BLACKLIST_PATH = "blacklist.json"

def cargar_blacklist():
    if not os.path.exists(BLACKLIST_PATH):
        return set()
    with open(BLACKLIST_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {c["canal_id"] for c in data["canales"]}

def agregar_a_blacklist(canal_id, nombre, razon="descartado manualmente"):
    if not os.path.exists(BLACKLIST_PATH):
        data = {"canales": []}
    else:
        with open(BLACKLIST_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    
    # No agregar si ya existe
    ids_existentes = {c["canal_id"] for c in data["canales"]}
    if canal_id in ids_existentes:
        print(f"  {nombre} ya está en la blacklist.")
        return
    
    data["canales"].append({
        "canal_id": canal_id,
        "nombre": nombre,
        "razon": razon
    })
    
    with open(BLACKLIST_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ {nombre} agregado a la blacklist.")

def esta_en_blacklist(canal_id, blacklist):
    return canal_id in blacklist