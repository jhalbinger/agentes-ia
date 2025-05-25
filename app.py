#LIBRERÍAS
from flask import Flask, request, jsonify
from pyngrok import ngrok
from openai import OpenAI
import traceback
import requests

import os

api_key = os.getenv("OPENAI_API_KEY")


#CONFIGURAR OPENAI
project_id = "proj_90hYWAKi7NnXRjR6QFWEkPFw"
organization_id = "org-REHVgFUAg933jSsY2CgjLmd8"

client = OpenAI(
    api_key=api_key,
    project=project_id,
    organization=organization_id
)

#FLASK APP
app = Flask(__name__)

@app.route("/orquestador-ia", methods=["POST"])
def clasificar():
    try:
        datos = request.get_json()
        mensaje_usuario = datos.get("consulta", "")
        if not mensaje_usuario:
            return jsonify({"error": "No se recibió ninguna consulta"}), 400

        # Paso 1: Clasificar el tema con GPT
        respuesta = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu tarea es clasificar la consulta del usuario en una de las siguientes categorías fijas: "
                        "'saldo', 'préstamo', 'tarjeta', 'clave', 'fraude', 'viaje', 'otro'. "
                        "Respondé solamente con una palabra: la categoría."
                    )
                },
                {
                    "role": "user",
                    "content": mensaje_usuario
                }
            ]
        )

        tema = respuesta.choices[0].message.content.strip().lower()

        # Paso 2: Enrutamiento según el tema
        if tema == "tarjeta":
            #Llamar al agente de tarjetas 
            url_tarjetas = "https://agente-tarjetas.onrender.com"
            respuesta_tarjeta = requests.get(url_tarjetas)
            
            if respuesta_tarjeta.status_code == 200:
                data_tarjeta = respuesta_tarjeta.json()
                return jsonify({
                    "tema_detectado": tema,
                    "respuesta_agente": data_tarjeta.get("respuesta", "No se pudo obtener respuesta del agente.")
                })
            else:
                return jsonify({
                    "tema_detectado": tema,
                    "error": "El agente de tarjetas no respondió correctamente."
                })

        if tema == "otro":
            
            url_no_entendido = "https://no-entendidos.onrender.com/webhook"
            respuesta_no_entendido = requests.post(url_no_entendido, json={"consulta": mensaje_usuario})
            
            if respuesta_no_entendido.status_code == 200:
                data_no_entendido = respuesta_no_entendido.json()
                return jsonify({
                    "tema_detectado": tema,
                    "respuesta_agente": data_no_entendido.get("respuesta", "No se pudo obtener respuesta del agente.")
                })
            else:
                return jsonify({
                    "tema_detectado": tema,
                    "error": "El agente de no entendidos no respondió correctamente."
                })

        # Tema no manejado aún
        return jsonify({
            "tema_detectado": tema,
            "respuesta_agente": "Todavía no hay un agente implementado para este temaaa."
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Error interno en el servidor"}), 500

#INICIAR FLASK EN SEGUNDO PLANO
def iniciar_servidor():
    app.run(port=5000)
