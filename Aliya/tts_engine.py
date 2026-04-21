"""
TTS Engine Alternativo - INSTANTÂNEO
Usa Windows TTS como primário (instantâneo)
Coqui XTTS como opcional (voice cloning)
"""
import os
import re
import subprocess
import threading

VOICE_FILE = "voz_referencia.wav"
use_voice_clone = True  # Mude para False se quiser TTS instantâneo
coqui_model = None

def inicializar_coqui():
    global coqui_model
    if not use_voice_clone:
        print(" [TTS] Modo: Windows TTS (instantâneo)")
        return True
    
    try:
        print(" [TTS] Carregando Coqui XTTS v2...")
        from TTS.api import TTS
        import torch
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f" [TTS] Device: {device}")
        
        coqui_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        
        if os.path.exists(VOICE_FILE):
            print(f" [TTS] Coqui XTTS pronto! Voice cloning ATIVADO")
        return True
    except Exception as e:
        print(f" [TTS] Coqui erro: {e}")
        print(" [TTS] Usando Windows TTS como fallback")
        return False

def speak(text):
    if not text:
        return
    
    text_limpo = re.sub(r'<[^>]+>', '', text).strip()
    text_limpo = text_limpo.replace('*', '')
    if not text_limpo:
        text_limpo = "Ok."
    
    if use_voice_clone and coqui_model:
        threading.Thread(target=speak_with_coqui, args=(text_limpo,), daemon=True).start()
    else:
        threading.Thread(target=speak_with_windows_tts, args=(text_limpo,), daemon=True).start()

def speak_with_coqui(text):
    try:
        import soundfile as sf
        import torch
        
        lang = detect_language(text)
        
        with torch.no_grad():
            if os.path.exists(VOICE_FILE):
                wav = coqui_model.tts(text=text, speaker_wav=VOICE_FILE, language=lang)
            else:
                wav = coqui_model.tts(text=text, language=lang)
        
        if wav is not None and len(wav) > 1000:
            # Converter para 16kHz (menos chiado)
            import numpy as np
            from scipy import signal
            
            # Resample 24kHz -> 16kHz
            num_samples = int(len(wav) * 16000 / 24000)
            wav_16k = signal.resample(wav, num_samples)
            
            # Normalizar
            max_val = np.max(np.abs(wav_16k))
            if max_val > 0:
                wav_16k = wav_16k / max_val * 0.95
            
            sf.write("vocal_temp.wav", wav_16k, 16000)
            tocar_audio("vocal_temp.wav")
        else:
            speak_with_windows_tts(text)
    except Exception as e:
        print(f" [TTS] Coqui erro: {e}")
        speak_with_windows_tts(text)

def speak_with_windows_tts(text):
    """TTS instantâneo do Windows -几乎没有延迟"""
    try:
        # Velocidade máxima (rate = 2)
        ps = f'''Add-Type -AssemblyName System.Speech; $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; $synth.Rate = 3; $synth.SelectVoice("Microsoft Zira Desktop"); $synth.Speak("{text.replace('"', '\\"')}")'''
        subprocess.run(["powershell", "-Command", ps], capture_output=True, timeout=30)
    except:
        pass

def detect_language(text):
    if any(ord(c) > 0x3000 for c in text):
        return "zh"
    if any(c in "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン" for c in text):
        return "ja"
    if any("áéíóúàèìòùãõâêîôû" for c in text.lower()):
        return "pt"
    return "en"

def tocar_audio(arquivo):
    if not arquivo or not os.path.exists(arquivo):
        return False
    try:
        ps = f'(New-Object System.Media.SoundPlayer "{arquivo}").PlaySync()'
        subprocess.run(["powershell", "-Command", ps], timeout=30, capture_output=True)
        return True
    except:
        return False

def stop():
    global coqui_model
    coqui_model = None