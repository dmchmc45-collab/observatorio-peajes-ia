# REQUIREMENTS — Agente IA de Flujo Vehicular

## Objetivo
Construir un agente que responda consultas en lenguaje natural sobre la tabla `flujo_vehicular` de Supabase.

## Requisitos funcionales
- Consultar por año, departamento y peaje.
- Generar rankings y comparaciones.
- Calcular indicadores mediante Python.
- Usar Groq con `openai/gpt-oss-20b`.
- Mostrar resultados mediante Streamlit.
- No modificar la base de datos.

## Restricciones
- No inventar cifras.
- No inferir causalidad sin evidencia.
- Tratar 2026 como periodo parcial cuando corresponda.
- Credenciales fuera del código fuente.
