import requests

url = "http://127.0.0.1:8001/feedback/guardar_feedback/"
data = {
    "producto": "GPT Analizador",
    "mercado": "México",
    "observacion": "El modelo responde rápido y preciso.",
    "categoria": "producto",
    "impacto": "alto",
    "accion_recomendada": "Expandir a otros mercados",
    "fuente": "gpt_chat",
    "metadata": {"usuario": "test"}
}

print("Enviando feedback a la API...")
response = requests.post(url, json=data)
print(f"Status code: {response.status_code}")
print(f"Respuesta: {response.json()}") 