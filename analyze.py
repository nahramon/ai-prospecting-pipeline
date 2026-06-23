import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SISTEMA = """Sos un agente especializado en evaluar si un canal de YouTube es un buen prospecto para el servicio de investigación narrativa de Nahuel Ramon.

EL SERVICIO: Investigación narrativa estructurada para contenido documental. Nahuel recibe un tema, desarrolla el storytelling y entrega un documento Word estructurado cronológicamente con toda la información lista para guionizar. Es investigación profunda, no research genérico.

PERFIL DEL CLIENTE IDEAL:
- Creadores de contenido documental, educativo, histórico, cultural, científico, filosófico o de investigación
- Videos largos y guionados (10+ min) que requieren research profundo
- Contenido en inglés o español
- Sin equipo de research visible

FILTROS ELIMINATORIOS:
1. Actividad reciente: publicó en los últimos 30 días
2. Tamaño: entre 50.000 y 5.000.000 suscriptores
3. Formato: largo y guionado, no vlogs, reacciones, shorts ni entretenimiento puro

NO SON CLIENTES IDEALES:
- Entretenimiento puro (gaming, lifestyle, humor, deportes)
- Instituciones u organizaciones (OMS, BBC, National Geographic, etc.)
- Empresas de producción con equipo grande
- Creadores con postura anti-IA conocida
- Canales de música, meditación o contenido ASMR
- Canales de distribución/agregadores de contenido ajeno

CLASIFICACIÓN DE PERFIL OBLIGATORIA:
Antes de dar el veredicto, clasificá al creador en uno de estos perfiles:
- EMPRESARIO/CREATOR: productividad, negocios, marca personal
- ACADÉMICO/INTELECTUAL: profesores, divulgadores, ensayistas, filósofos
- ARTISTA/NARRATIVO: documentalistas, storytellers, true crime, ensayo cultural
- CIENTÍFICO/TÉCNICO: ciencia, medicina, tecnología, neurociencia
- DESARROLLO HUMANO: psicología, bienestar, espiritualidad con base

SEÑALES DE ALERTA ANTI-IA (alerta_ia: true):
- Menciona explícitamente que su contenido es hecho por humanos
- Tiene postura pública contra la IA
- Su audiencia lo elogia por "no ser AI slop"
- Aclara en descripción "scripts written by human beings"

Respondé SOLO en este formato JSON, sin texto adicional:
{
  "apto": true/false,
  "puntaje": 0-10,
  "perfil": "ARTISTA/NARRATIVO | ACADÉMICO/INTELECTUAL | CIENTÍFICO/TÉCNICO | EMPRESARIO/CREATOR | DESARROLLO HUMANO",
  "razon": "una línea explicando por qué sí o por qué no",
  "alerta_ia": true/false,
  "nota": "observación adicional relevante, o vacío"
}"""

def analizar_canal(canal):
    prompt = f"""Analizá este canal de YouTube:

Nombre: {canal['nombre']}
Suscriptores: {canal['suscriptores']:,}
País: {canal['pais']}
Días desde último video: {canal['dias_desde_ultimo_video']}
Título último video: {canal['titulo_ultimo_video']}
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=SISTEMA,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    texto = message.content[0].text.strip()
    texto = texto.replace("```json", "").replace("```", "").strip()
    print(f"    DEBUG respuesta: {texto[:200]}")
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        return {
            "apto": False,
            "puntaje": 0,
            "perfil": "N/A",
            "razon": "Error al parsear respuesta",
            "alerta_ia": False,
            "nota": texto
        }

def analizar_lista(canales):
    print("\n=== ANÁLISIS DE FIT CON CLAUDE ===\n")
    
    aprobados = []
    descartados = []

    for c in canales:
        print(f"  Analizando: {c['nombre']}...")
        resultado = analizar_canal(c)
        c["analisis"] = resultado

        if resultado["apto"]:
            aprobados.append(c)
            print(f"    ✓ APTO | Puntaje: {resultado['puntaje']}/10 | {resultado['perfil']}")
            print(f"      {resultado['razon']}")
        else:
            descartados.append(c)
            print(f"    ✗ DESCARTADO | {resultado['razon']}")
            # Blacklist automática para descartados estructurales
            from blacklist import agregar_a_blacklist
            agregar_a_blacklist(c["canal_id"], c["nombre"], resultado["razon"])

    print(f"\n=== RESUMEN ===")
    print(f"Aptos: {len(aprobados)} | Descartados: {len(descartados)}\n")

    if aprobados:
        print(f"{'Canal':<40} {'Subs':>10} {'Puntaje':>8} {'Perfil'}")
        print("-" * 90)
        for c in sorted(aprobados, key=lambda x: x["analisis"]["puntaje"], reverse=True):
            print(f"{c['nombre']:<40} {c['suscriptores']:>10,} {c['analisis']['puntaje']:>7}/10  {c['analisis']['perfil']}")

    return aprobados