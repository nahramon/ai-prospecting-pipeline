import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SISTEMA = """Sos un experto en contenido documental y narrativa investigativa. 
Tu tarea es proponer un tema de investigación concreto para regalar como muestra a un creador de YouTube.

El tema tiene que cumplir tres condiciones:
1. Encajar perfectamente con el estilo y nicho del canal
2. No haber sido cubierto todavía por ese canal (o haberlo tocado muy superficialmente)
3. Ser lo suficientemente jugoso y específico para que recibir el research ya hecho sea irresistible

El tema NO puede ser genérico. Tiene que ser un caso, personaje, evento o historia específica.

Respondé SOLO en este formato JSON, sin texto adicional:
{
  "tema": "título concreto del tema propuesto",
  "angulo": "el ángulo narrativo específico que lo hace irresistible",
  "por_que_encaja": "una línea explicando por qué es perfecto para este canal",
  "por_que_no_lo_cubrieron": "una línea sobre por qué probablemente no lo cubrieron aún"
}"""

def proponer_tema(canal):
    prompt = f"""Proponé un tema de investigación narrativa para este canal de YouTube:

Nombre: {canal['nombre']}
Suscriptores: {canal['suscriptores']:,}
País: {canal['pais']}
Perfil: {canal['analisis']['perfil']}
Último video: {canal['titulo_ultimo_video']}
Razón de fit: {canal['analisis']['razon']}
Nota adicional: {canal['analisis']['nota']}

El tema tiene que ser un caso real, específico y con potencial narrativo fuerte.
Pensá en algo que genere tensión, misterio o revelación — no un tema académico frío."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=SISTEMA,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    texto = message.content[0].text.strip()
    texto = texto.replace("```json", "").replace("```", "").strip()
    
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        return {
            "tema": "Error al generar tema",
            "angulo": "",
            "por_que_encaja": "",
            "por_que_no_lo_cubrieron": texto
        }

def proponer_temas_lista(canales):
    print("\n=== PROPUESTA DE TEMAS DE MUESTRA ===\n")
    
    for c in canales:
        print(f"Canal: {c['nombre']}")
        print(f"Perfil: {c['analisis']['perfil']} | Puntaje: {c['analisis']['puntaje']}/10")
        print(f"Generando tema...\n")
        
        tema = proponer_tema(c)
        c["muestra"] = tema
        
        print(f"  TEMA:     {tema['tema']}")
        print(f"  ÁNGULO:   {tema['angulo']}")
        print(f"  ENCAJA:   {tema['por_que_encaja']}")
        print(f"  NOVEDAD:  {tema['por_que_no_lo_cubrieron']}")
        print()
    
    return canales