import os
import re
import subprocess
import threading
import time

VOICE_FILE = "voz_referencia.wav"
coqui_model = None

def inicializar_coqui():
    global coqui_model
    try:
        print(" [TTS] Carregando Coqui XTTS v2 (pode demorar)...")
        from TTS.api import TTS
        import torch
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        coqui_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        
        if os.path.exists(VOICE_FILE):
            size = os.path.getsize(VOICE_FILE)
            print(f" [TTS] Coqui XTTS pronto! Voz: {VOICE_FILE} ({size/1024:.1f}KB)")
        else:
            print(" [TTS] Coqui XTTS pronto! Sem voz referencia")
        return True
    except Exception as e:
        print(f" [TTS] Coqui erro: {e}")
        return False

def speak_with_coqui(text):
    if not text or coqui_model is None:
        return speak_with_windows_tts(text)
    
    text_limpo = re.sub(r'<[^>]+>', '', text).strip()
    text_limpo = text_limpo.replace('*', '')
    if not text_limpo:
        text_limpo = "Ok."
    
    try:
        import soundfile as sf
        import numpy as np
        
        lang = detect_language(text_limpo)
        
        if os.path.exists(VOICE_FILE):
            wav = coqui_model.tts(
                text=text_limpo,
                speaker_wav=VOICE_FILE,
                language=lang
            )
        else:
            wav = coqui_model.tts(text=text_limpo, language=lang)
        
        if wav is not None and len(wav) > 1000:
            sf.write("vocal_temp.wav", wav, 24000)
            return tocar_audio("vocal_temp.wav")
        else:
            return speak_with_windows_tts(text_limpo)
    except Exception as e:
        print(f" [TTS] Coqui erro: {e}")
        return speak_with_windows_tts(text_limpo)

def detect_language(text):
    if any(ord(c) > 0x3000 for c in text):
        return "zh"
    if any(c in "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン" for c in text):
        return "ja"
    if any("абвгдеёжзийклмнопрстуфхцчшщъыьэюя" in c.lower() for c in text if c.isalpha()):
        return "ru"
    if any(c in "áéíóúàèìòùãõâêîôû" for c in text.lower()):
        return "pt"
    return "en"

def speak_with_windows_tts(text):
    if not text:
        return False
    try:
        ps = f'''Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.SelectVoice("Microsoft Zira Desktop"); $synth.Speak("{text.replace('"', '\\"')}")'''
        subprocess.run(["powershell", "-Command", ps], capture_output=True, timeout=30)
        return True
    except:
        return False

def tocar_audio(arquivo):
    if not arquivo or not os.path.exists(arquivo):
        return False
    try:
        ps = f'(New-Object System.Media.SoundPlayer "{arquivo}").PlaySync()'
        subprocess.run(["powershell", "-Command", ps], timeout=30, capture_output=True)
        return True
    except:
        return False

def speak(text):
    if not text:
        return
    threading.Thread(target=speak_with_coqui, args=(text,), daemon=True).start()

def stop():
    global coqui_model
    coqui_model = None