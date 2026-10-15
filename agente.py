import os
import json
from groq import Groq
from dotenv import load_dotenv
from herramientas.consultas import ranking_peajes, comparar_departamentos
from herramientas.extras import comparar_peajes, calcular_tendencia, detectar_anomalias, generar_grafico, generar_pdf, enviar_telegram

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
modelo = os.environ.get("LLM_MODEL", "llama3-70b-8192")
cliente = Groq(api_key=api_key)

def consultar_agente(pregunta_usuario):
    herramientas_ia = [
        {
            "type": "function", "function": {
                "name": "ranking_peajes", "description": "Obtiene el ranking top de peajes con mayor flujo vehicular.",
                "parameters": {"type": "object", "properties": {"anio": {"type": "integer"}, "indicador": {"type": "string"}, "cantidad": {"type": "integer"}}, "required": ["anio"]}
            }
        },
        {
            "type": "function", "function": {
                "name": "comparar_departamentos", "description": "Compara el flujo vehicular total por departamento en un año.",
                "parameters": {"type": "object", "properties": {"anio": {"type": "integer"}, "indicador": {"type": "string"}}, "required": ["anio"]}
            }
        },
        {
            "type": "function", "function": {
                "name": "comparar_peajes", "description": "Compara el tráfico entre dos peajes específicos en un año.",
                "parameters": {"type": "object", "properties": {"peaje_1": {"type": "string"}, "peaje_2": {"type": "string"}, "anio": {"type": "integer"}}, "required": ["peaje_1", "peaje_2", "anio"]}
            }
        },
        {
            "type": "function", "function": {
                "name": "calcular_tendencia", "description": "Calcula la tendencia de crecimiento de un peaje respecto al año anterior.",
                "parameters": {"type": "object", "properties": {"nombre_peaje": {"type": "string"}, "anio": {"type": "integer"}}, "required": ["nombre_peaje", "anio"]}
            }
        },
        {
            "type": "function", "function": {
                "name": "detectar_anomalias", "description": "Detecta anomalías o eventos inusuales en un peaje.",
                "parameters": {"type": "object", "properties": {"nombre_peaje": {"type": "string"}, "anio": {"type": "integer"}}, "required": ["nombre_peaje", "anio"]}
            }
        },
        {
            "type": "function", "function": {
                "name": "generar_grafico", "description": "Genera un gráfico en PNG del flujo vehicular.",
                "parameters": {"type": "object", "properties": {"nombre_peaje": {"type": "string"}, "anio": {"type": "integer"}}, "required": ["nombre_peaje", "anio"]}
            }
        },
        {
            "type": "function", "function": {
                "name": "generar_pdf", "description": "Genera un reporte técnico ejecutivo en formato PDF y devuelve su ruta.",
                "parameters": {"type": "object", "properties": {"pregunta": {"type": "string"}}, "required": ["pregunta"]}
            }
        },
        {
            "type": "function", "function": {
                "name": "enviar_telegram", "description": "Envía un mensaje de texto y un documento al Telegram del usuario. Obligatorio: Si el usuario pide enviar un reporte/gráfico por telegram, primero ejecuta generar_pdf/generar_grafico, y luego usa la 'ruta_archivo' resultante aquí.",
                "parameters": {"type": "object", "properties": {"mensaje": {"type": "string"}, "ruta_archivo": {"type": "string"}}, "required": ["mensaje"]}
            }
        }
    ]

    mensajes = [
        {"role": "system", "content": "Eres un asistente de IA experto en flujo vehicular. Trabajas resolviendo problemas de forma secuencial."},
        {"role": "user", "content": pregunta_usuario}
    ]

    # --- INICIO DEL BUCLE DEL AGENTE (AGENTIC LOOP) ---
    while True:
        respuesta = cliente.chat.completions.create(
            model=modelo,
            messages=mensajes,
            tools=herramientas_ia,
            tool_choice="auto",
            max_tokens=1000
        )

        mensaje_respuesta = respuesta.choices[0].message
        
        # Si la IA decide que ya no necesita usar más herramientas, terminamos y mostramos su mensaje
        if not mensaje_respuesta.tool_calls:
            return mensaje_respuesta.content
            
        # Si decide usar una herramienta, guardamos su decisión en el historial
        mensajes.append(mensaje_respuesta)
        
        for tool_call in mensaje_respuesta.tool_calls:
            nombre_funcion = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            print(f"[🤖 Ejecutando herramienta: {nombre_funcion}...]")
            
            if nombre_funcion == "ranking_peajes":
                datos = ranking_peajes(args.get("anio"), args.get("indicador", "VEH_TOTAL"), args.get("cantidad", 5))
            elif nombre_funcion == "comparar_departamentos":
                datos = comparar_departamentos(args.get("anio"), args.get("indicador", "VEH_TOTAL"))
            elif nombre_funcion == "comparar_peajes":
                datos = comparar_peajes(args.get("peaje_1"), args.get("peaje_2"), args.get("anio"))
            elif nombre_funcion == "calcular_tendencia":
                datos = calcular_tendencia(args.get("nombre_peaje"), args.get("anio"))
            elif nombre_funcion == "detectar_anomalias":
                datos = detectar_anomalias(args.get("nombre_peaje"), args.get("anio"))
            elif nombre_funcion == "generar_grafico":
                datos = generar_grafico(args.get("nombre_peaje"), args.get("anio"))
            elif nombre_funcion == "generar_pdf":
                datos = generar_pdf(args.get("pregunta"))
            elif nombre_funcion == "enviar_telegram":
                datos = enviar_telegram(args.get("mensaje"), args.get("ruta_archivo", ""))
            else:
                datos = {"error": "Herramienta desconocida"}
            
            # Guardamos el resultado (ej. la ruta del PDF) para que la IA lo lea en la siguiente vuelta
            mensajes.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": nombre_funcion,
                "content": json.dumps(datos)
            })
            
        # Al terminar el 'for', el 'while' vuelve a iniciar. 
        # La IA leerá los datos recibidos y decidirá automáticamente si ejecuta otra herramienta o responde al usuario.