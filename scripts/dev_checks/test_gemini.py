import os
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GEMINI_API_KEY", "")
print("Key loaded:", bool(key))

for model in ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-2.5-flash"]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {"contents": [{"parts": [{"text": "Say hello in one short sentence."}]}]}
    try:
        r = requests.post(url, json=payload, headers={"x-goog-api-key": key}, timeout=30)
        print(model, "->", r.status_code, r.text[:100].replace("\n", " "))
    except Exception as exc:
        print(model, "-> error:", exc)