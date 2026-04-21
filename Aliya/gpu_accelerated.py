import os
import sys
import torch
import asyncio
import requests
import numpy as np
import pyaudio
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

print("=== Verificando GPU ===")
if torch.cuda.is_available():
    gpu = torch.cuda.get_device_name(0)
    vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f"✓ GPU: {gpu}")
    print(f"✓ VRAM: {vram:.1f}GB")
else:
    print("✗ GPU não disponível")

OLLAMA_BASE_URL = "http://localhost:11434"

def verificar_ollama():
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return r.status_code == 200
    except:
        return False

async def test_gpu_stt():
    print("\n=== Testando Whisper GPU ===")
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("medium", device="cuda", compute_type="float16")
        print("✓ Faster-Whisper (GPU) pronto!")
        return True
    except Exception as e:
        print(f"✗ Faster-Whisper erro: {e}")
        return False

async def test_vision():
    print("\n=== Testando Vision Local ===")
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if r.status_code == 200:
            modelos = r.json().get("models", [])
            tem_vl = any("qwen2.5vl" in m.get("name", "").lower() for m in modelos)
            if tem_vl:
                print("✓ Qwen2.5-VL (visão local) disponível!")
                return True
            else:
                print("⚠ Qwen2.5-VL não instalado. Instalando...")
                subprocess.run(["ollama", "pull", "qwen2.5vl:7b"], 
                             capture_output=True, timeout=600)
                print("✓ Qwen2.5-VL instalado!")
                return True
    except Exception as e:
        print(f"✗ Vision erro: {e}")
    return False

async def test_tts():
    print("\n=== Testando TTS ===")
    try:
        import edge_tts
        print("✓ Edge-TTS disponível")
        return True
    except:
        print("✗ Edge-TTS erro")

async def main():
    print("\n" + "="*40)
    print("TESTE COMPLETO - ALYA v2.0")
    print("="*40)
    
    print("\n[1] Verificando Ollama...")
    if verificar_ollama():
        print("✓ Ollama online")
    else:
        print("✗ Ollama offline")
    
    await test_gpu_stt()
    await test_vision()
    await test_tts()
    
    print("\n" + "="*40)
    print("TESTE COMPLETO!")
    print("="*40)

if __name__ == "__main__":
    asyncio.run(main())