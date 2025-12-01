import json
import re

def formato_json(reporte, nombres_completos):
    lista = []

    for apellido, estado in reporte.items():
        nombre_completo = nombres_completos.get(apellido, apellido)

        # Determinar estado normalizado
        if "PRESENTE" in estado:
            estado_final = "Presente"
            causa = ""
        elif "SIN CAUSA" in estado:
            estado_final = "Ausente"
            causa = "Sin causa declarada"
        else:
            estado_final = "Ausente"
            # Extraer texto dentro de los paréntesis
            match = re.search(r"\((.*?)\)", estado)
            causa = match.group(1) if match else ""

        lista.append({
            "1. Identifíquese:": nombre_completo,
            "2. Indique estado:": estado_final,
            "3. En caso de ausente: indicar la causa textual para transcribir al Parte Oficial.": causa
        })

    return lista
