from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

RUTA_JSON = "/app/datos_parte.json"  # dentro del contenedor

@app.route("/parte", methods=["GET"])
def obtener_parte():
    if not os.path.exists(RUTA_JSON):
        return jsonify({"error": "datos_parte.json no existe"}), 404

    try:
        with open(RUTA_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "OK", "mensaje": "API Presentismo funcionando"})

if __name__ == "__main__":
    # En Docker SIEMPRE usar 0.0.0.0
    app.run(host="0.0.0.0", port=5000)
