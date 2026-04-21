import os
import re
import asyncio
import subprocess
import threading
import torch
from dotenv import load_dotenv

load_dotenv()

F5_TTS_DISPONIVEL = False
vibevoice_disponivel = False

def verificar_gpu():
    if torch.cuda.is_available():
        gpu = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
        return True, gpu, vram
    return False, "N/A", 0

def inicializar_f5tts():
    global F5_TTS_DISPONIVEL
    try:
        print(" [F5-TTS] Verificando GPU...")
        tem_gpu, gpu, vram = verificar_gpu()
        if tem_gpu:
            print(f" [F5-TTS] GPU detectada: {gpu} ({vram:.1f}GB)")
            print(" [F5-TTS] Instalando F5-TTS...")
            subprocess.run([".venv\Scripts\pip.exe", "install", "f5-tts"], 
                        capture_output=True, timeout=300)
            F5_TTS_DISPONIVEL = True
            print(" [F5-TTS] Pronto!")
        else:
            print(" [F5-TTS] GPU não disponível, usando alternativa...")
    except Exception as e:
        print(f" [F5-TTS] Erro: {e}")

async def speak_with_f5(text, voice_ref="voz_referencia.wav"):
    if not text:
        return False
    text_limpo = re.sub(r'<[^>]+>', '', text).strip()
    text_limpo = text_limpo.replace('*', '')
    if not text_limpo:
        text_limpo = "Ok."
    
    if F5_TTS_DISPONIVEL:
        try:
            from f5_tts import F5TTS
            model = F5TTS(device="cuda")
            audio = model.generate(
                text=text_limpo,
                ref_audio=voice_ref if os.path.exists(voice_ref) else None,
                ref_text="audio reference text"
            )
            return True
        except Exception as e:
            print(f" [F5-TTS] Erro: {e}")
    return False

def speak_f5_thread(text):
    asyncio.run(speak_with_f5(text))