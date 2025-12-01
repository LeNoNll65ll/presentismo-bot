from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

RUTA_JSON = os.path.join(os.getcwd(), "datos_parte.json")

@app.route("/parte", methods=["GET"])
def obtener_parte():
    """Devuelve el contenido actual del archivo datos_parte.json."""
    if not os.path.exists(RUTA_JSON):
        return jsonify({"error": "El archivo datos_parte.json no existe"}), 404

    try:
        with open(RUTA_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"Error leyendo JSON: {str(e)}"}), 500


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "OK", "mensaje": "API Presentismo funcionando"})

if __name__ == "__main__":
    # Para Raspberry Pi: host='0.0.0.0'
    app.run(host="0.0.0.0", port=5000, debug=False)
