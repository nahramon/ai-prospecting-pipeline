import os
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SHEET_ID = "1TVsB0wslUVutgFvwjTqEkkDY07mlbOA0bC0EZryGtzk"

def conectar_sheet():
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).sheet1
    return sheet

def exportar(canales):
    print("\nExportando a Google Sheets...\n")
    
    sheet = conectar_sheet()
    
    # Encabezados
    headers = [
        "Canal", "Canal ID", "Suscriptores", "País",
        "Días último video", "Título último video",
        "Puntaje fit", "Perfil", "Razón fit", "Alerta IA",
        "Método contacto", "Contacto directo", "Instagram",
        "Tema muestra", "Ángulo", "Por qué encaja",
        "Mensaje", "Plataforma sugerida", "Estado"
    ]
    
    sheet.clear()
    sheet.append_row(headers)
    
    for c in canales:
        analisis = c.get("analisis", {})
        muestra = c.get("muestra", {})
        mensaje = c.get("mensaje", {})
        
        fila = [
            c.get("nombre", ""),
            c.get("canal_id", ""),
            c.get("suscriptores", ""),
            c.get("pais", ""),
            c.get("dias_desde_ultimo_video", ""),
            c.get("titulo_ultimo_video", ""),
            analisis.get("puntaje", ""),
            analisis.get("perfil", ""),
            analisis.get("razon", ""),
            "SÍ" if analisis.get("alerta_ia") else "NO",
            c.get("contacto", {}).get("metodo", ""),
            c.get("contacto", {}).get("valor", ""),
            c.get("contacto", {}).get("instagram", ""),
            muestra.get("tema", ""),
            muestra.get("angulo", ""),
            muestra.get("por_que_encaja", ""),
            mensaje.get("mensaje", ""),
            mensaje.get("plataforma_sugerida", ""),
            "Pendiente"
        ]
        
        sheet.append_row(fila)
        print(f"  ✓ {c.get('nombre')} exportado")
    
    print(f"\nTotal exportados: {len(canales)}")
    print(f"Sheet: https://docs.google.com/spreadsheets/d/{SHEET_ID}")