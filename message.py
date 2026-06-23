import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SISTEMA = """Sos un asistente que redacta mensajes de contacto en nombre de Nahuel Ramon,
un investigador narrativo argentino que ofrece research estructurado para creadores de contenido documental.

SOBRE NAHUEL:
- Trabaja con its.blanko (1.8M suscriptores), canal documental en inglés
- 5 meses, +30 documentos entregados, máximo 4 horas semanales de trabajo activo
- Argentino, inglés C1 real, español nativo
- NUNCA menciona: IA, automatización, sistema, pipeline, proceso técnico

FÓRMULA EXACTA — en este orden, sin excepciones:

1. ELOGIO ESPECÍFICO (1 línea)
   - Mencioná una decisión editorial concreta del último video largo: un ángulo, algo que eligió hacer o no hacer, una distinción que la mayoría ignora
   - Tiene que sonar a que viste ese video específico
   - Usá el título Y la descripción del video para encontrar ese detalle
   - NUNCA: "your content is amazing", "I love your channel", elogios genéricos

2. QUÉ HACE NAHUEL (1 línea)
   - Sin mencionar IA ni proceso técnico
   - Ejemplo: "I do historical research for documentary creators. I handle the sourcing and structuring so you keep your time for the writing and explaining."

3. INSINUACIÓN DEL TEMA — NUNCA revelar el tema (1 línea)
   - Solo decir que tenés algo en mente que encaja con su canal
   - NUNCA mencionar el caso, el nombre, ni ningún detalle de la muestra
   - Ejemplo exacto: "I had a topic in mind that fits your channel well, and I'd be glad to put together a research sample on it, free, so you can judge the quality yourself."

4. CREDENCIAL (1 línea)
   - its.blanko + 30 docs de forma natural, sin autoelogio
   - Ejemplo: "I currently work with its.blanko (1.8M subs), around 30 docs delivered in five months."

5. CIERRE CON PREGUNTA DIRECTA (1 línea)
   - Ejemplo: "Would that be useful?"

VOZ EN INGLÉS:
- Contracciones naturales: I'm, don't, I've, it's
- Directo, sin florituras
- Errores reales ocasionales (C1, no nativo perfecto)
- Cierra con "Best regards, Nahuel" en email, "— Nahuel 🇦🇷" en DM
- NUNCA raya larga dentro del texto
- Menos de 100 palabras en total

VOZ EN ESPAÑOL:
- Directo y sin rodeos
- Cálido pero no efusivo
- Frases cortas, párrafos cortos
- Cierra con "Nahuel Ramon"
- Menos de 100 palabras en total

NUNCA:
- Revelar el tema de muestra en el primer mail
- "I hope this message finds you well"
- Cualquier frase que suene a template de LinkedIn
- Más de 100 palabras

Respondé SOLO en este formato JSON, sin texto adicional:
{
  "idioma": "inglés/español",
  "canal": "nombre del canal",
  "mensaje": "el mensaje completo listo para copiar y pegar",
  "plataforma_sugerida": "Email / YouTube DM / Instagram DM"
}"""

def redactar_mensaje(canal):
    pais = canal.get("pais", "N/A")
    idioma = "español" if pais in ["AR", "MX", "ES", "CO", "CL", "PE", "VE"] else "inglés"

    prompt = f"""Redactá un mensaje de contacto para este creador:

Canal: {canal['nombre']}
Suscriptores: {canal['suscriptores']:,}
País: {pais}
Idioma a usar: {idioma}
Perfil del creador: {canal['analisis']['perfil']}

ÚLTIMO VIDEO:
Título: {canal['titulo_ultimo_video']}
Descripción: {canal.get('descripcion_ultimo_video', 'No disponible')}

Usá el título y la descripción del último video para construir un elogio específico y real.
NO reveles el tema de muestra. Solo insinuá que tenés algo en mente."""

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
            "idioma": idioma,
            "canal": canal['nombre'],
            "mensaje": texto,
            "plataforma_sugerida": "Email"
        }

def redactar_mensajes_lista(canales):
    print("\n=== MENSAJES DE CONTACTO ===\n")

    for c in canales:
        print(f"Canal: {c['nombre']}")
        resultado = redactar_mensaje(c)
        c["mensaje"] = resultado

        print(f"Idioma: {resultado['idioma']}")
        print(f"Plataforma sugerida: {resultado['plataforma_sugerida']}")
        print(f"\n{resultado['mensaje']}\n")
        print("-" * 80)

    return canales