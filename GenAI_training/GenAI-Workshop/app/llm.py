import requests
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3"
def call_phi3(prompt: str) -> str:
    """
    Calls Llama 3 locally using Ollama.
    """
    payload = {
    "model": MODEL_NAME,
    "prompt": prompt,
    "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=60)
    
    if response.status_code != 200:
        raise RuntimeError(
            
    f"Ollama error: {response.status_code} - {response.text}"
    )
    return response.json()["response"]
