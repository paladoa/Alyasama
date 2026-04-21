# ============//======================//================
#region 📚 CHAMADAS E MODOS
# ======================================================
import asyncio
import json
import re
import io
import wave
import torch
import numpy as np
import pyaudio
import requests
import random
import pygame
import keyboard
import threading
import os
import base64
import tkinter as tk
import subprocess
import sys
from tkinter import ttk
from PIL import ImageGrab
from datetime import datetime
from dotenv import load_dotenv

# 🔥 IMPORTAÇÃO DA INTERFACE GRÁFICA ATUALIZADA
from Arcana.Apps.gui_handler import RemGUI

# 🔥 NOVO: TTS Windows (offline, sem API)
from Aliya.tts_engine import speak

# 🔥 NOVO: Memória Avançada (ChromaDB)
from Aliya.memoria_avancada import inicializar_memoria, get_memoria

# 🔥 IMPORTAÇÃO DO SEU MÓDULO DE PESQUISA
import Arcana.Net.search_ddg as search_ddg

#from Arcana.Net.discord_Rem import run_discord_bot

# 🔥 IMPORTAÇÃO DO SEU MÓDULO DE AUTOMAÇÃO DE APPS
from Arcana.Aura.app_launcher import AppLauncher
from Arcana.Aura.idioma import get_idioma_atual, set_idioma, listar_idiomas 

# Carrega as chaves do ficheiro .env
load_dotenv()
GROQ_API_KEY_LLM = os.getenv("GROQ_API_KEY_LLM")
GROQ_API_KEY_VISION = os.getenv("GROQ_API_KEY_VISION")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY") # Chave da NVIDIA

# 🔥 CLIENTE OLLAMA (Para Qwen2 local)
OLLAMA_BASE_URL = "http://localhost:11434"
def verificar_ollama():
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            modelos = response.json().get("models", [])
            nomes = [m.get("name", "") for m in modelos]
            print(f" [OLLAMA] Modelos disponíveis: {nomes}")
            return True
    except:
        return False
    return False

def iniciar_ollama_se_nao_estiver():
    import subprocess
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        if response.status_code == 200:
            modelos = response.json().get("models", [])
            nomes = [m.get("name", "") for m in modelos]
            print(f" [OLLAMA] Modelos disponíveis: {nomes}")
            
            # Verifica se qwen2:7b está instalado
            if not any("qwen2:7b" in n.lower() or n.startswith("qwen2") for n in nomes):
                print(" [OLLAMA] Modelo qwen2:7b não encontrado. Baixando...")
                subprocess.Popen(
                    ["ollama", "pull", "qwen2:7b"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print(" [OLLAMA] Aguardando download do modelo (pode levar alguns minutos)...")
                import time
                for i in range(120):  # Espera até 2 minutos
                    time.sleep(1)
                    try:
                        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
                        if response.status_code == 200:
                            modelos = response.json().get("models", [])
                            if any("qwen2" in m.get("name", "").lower() for m in modelos):
                                print(" [OLLAMA] Modelo qwen2 baixado com sucesso!")
                    except:
                        pass
            
            # Verifica se qwen2.5vl:7b está instalado (para visão)
            if not any("qwen2.5vl" in n.lower() for n in modelos):
                print(" [OLLAMA] Modelo qwen2.5vl:7b (visão) não encontrado. Baixando...")
                subprocess.Popen(
                    ["ollama", "pull", "qwen2.5vl:7b"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print(" [OLLAMA] Baixando modelo de visão (pode levar 3-5 minutos)...")
                import time
                for i in range(300):  # Espera até 5 minutos
                    time.sleep(1)
                    try:
                        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
                        if response.status_code == 200:
                            modelos = response.json().get("models", [])
                            if any("qwen2.5vl" in m.get("name", "").lower() for m in modelos):
                                print(" [OLLAMA] Modelo qwen2.5vl:7b baixado com sucesso!")
                                break
                    except:
                        pass
            
            return True
    except:
        pass
    try:
        print(" [OLLAMA] Tentando iniciar Ollama...")
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import time
        for i in range(10):
            time.sleep(1)
            try:
                response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
                if response.status_code == 200:
                    print(" [OLLAMA] Servidor iniciado com sucesso!")
                    return True
            except:
                pass
    except Exception as e:
        print(f" [OLLAMA] Não foi possível iniciar: {e}")
    return False

def get_ollama_response(prompt, model="qwen2:7b", temperature=0.7):
    try:
        import time
        for tentativa in range(3):
            try:
                response = requests.post(
                    f"{OLLAMA_BASE_URL}/api/chat",
                    json={"model": model, "messages": [{"role": "user", "content": prompt[:2000]}], "temperature": temperature, "stream": False},
                    timeout=90
                )
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("message", {}).get("content", "")
                    if content:
                        return content.strip()
            except Exception as e:
                if tentativa < 2:
                    time.sleep(1)
                    continue
                else:
                    print(f" Erro Ollama: {e}")
        return None
    except Exception as e:
        print(f" Erro Ollama: {e}")
    return None

def get_ollama_response_full(messages, model="qwen2:7b", temperature=0.7):
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={"model": model, "messages": messages, "temperature": temperature, "stream": False},
            timeout=120
        )
        if response.status_code == 200:
            try:
                data = response.json()
                content = data.get("message", {}).get("content", "")
                if content:
                    return content.strip()
            except:
                print(f" Erro parsing Ollama: {response.text[:200]}")
    except Exception as e:
        print(f" Erro Ollama: {e}")
    return None

async def speak_with_sbv2(text, style="neutral"):
    if not text:
        return
    speak(text)

# ======================================================
# Cria a pasta automaticamente se ela não existir
os.makedirs("Arcana/armazen", exist_ok=True)

# 🔥 ARQUIVOS FIXOS
BRAIN_FILE = "Arcana/armazen/brain.json"
MEMORIA_FILE = "Arcana/armazen/memoria.json"
SEARCH_MEMORY_FILE = "Arcana/armazen/pesquisa_memoria.json" 

VISAO_HABILITADA = False # Controlo global do F2
COMMAND_FILE = "Arcana/armazen/comando.txt"

def ler_comando_ahk():
    try:
        if os.path.exists(COMMAND_FILE):
            with open(COMMAND_FILE, 'r', encoding='utf-8') as f:
                cmd = f.read().strip()
            with open(COMMAND_FILE, 'w', encoding='utf-8') as f:
                f.write("")
            return cmd
    except:
        pass
    return None
CONTADOR_VISAO = 0       # Contador para limpar a memória visual

def abrir_gui_modelos():
    def salvar():
        if os.path.exists(BRAIN_FILE):
            with open(BRAIN_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
            data["modelos_ativos"] = {"local": var_local.get(), "discord": var_discord.get()}
            with open(BRAIN_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"\n [SISTEMA] Cérebro atualizado! Local: {var_local.get().upper()} | Discord: {var_discord.get().upper()}")
        janela.destroy()

    janela = tk.Tk()
    janela.title("Painel de Controle IA - Rem")
    janela.geometry("400x320")
    janela.configure(bg="#1e1e2e")
    style = ttk.Style()
    style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4", font=("Segoe UI", 11))
    style.configure("TRadiobutton", background="#1e1e2e", foreground="#a6adc8", font=("Segoe UI", 10))

    ttk.Label(janela, text=" Cérebro Principal (Local):", font=("Segoe UI", 12, "bold"), foreground="#f38ba8").pack(pady=(15, 5))
    var_local = tk.StringVar()
    ttk.Radiobutton(janela, text="NVIDIA (Kimi 2.5)", variable=var_local, value="nvidia").pack()
    ttk.Radiobutton(janela, text="GROQ (Scout 17b)", variable=var_local, value="groq").pack()
    ttk.Radiobutton(janela, text="OLLAMA (Qwen2 7B Local)", variable=var_local, value="ollama").pack()

    ttk.Label(janela, text=" Cérebro do Discord:", font=("Segoe UI", 12, "bold"), foreground="#a6e3a1").pack(pady=(20, 5))
    var_discord = tk.StringVar()
    ttk.Radiobutton(janela, text="NVIDIA (Kimi 2.5)", variable=var_discord, value="nvidia").pack()
    ttk.Radiobutton(janela, text="GROQ (Scout 17b)", variable=var_discord, value="groq").pack()

    try:
        with open(BRAIN_FILE, 'r', encoding='utf-8') as f:
            mod = json.load(f).get("modelos_ativos", {"local": "nvidia", "discord": "groq"})
            var_local.set(mod.get("local", "nvidia")); var_discord.set(mod.get("discord", "groq"))
    except: var_local.set("nvidia"); var_discord.set("groq")

    tk.Button(janela, text=" Salvar e Aplicar", command=salvar, bg="#89b4fa", fg="#1e1e2e", font=("Segoe UI", 10, "bold")).pack(pady=25)
    janela.attributes('-topmost', True)
    janela.mainloop()
#endregion
# ======================================================
# ======================================================
#region 🌐 VISÃO COMPUTACIONAL E INJETORES
# ======================================================
VISAO_ULTIMA_ANALISE = 0
VISAO_INTERVALO_MINIMO = 300  # Segundos entre análises (5 minutos)
visao_comentario_aleatorio = True  # Se True, às vezes analisa mesmo sem pedir

def toggle_visao(e):
    global VISAO_HABILITADA
    VISAO_HABILITADA = not VISAO_HABILITADA
    play_beep("inicio" if VISAO_HABILITADA else "fim")
    print(f"\n[SISTEMA] Visao (F2): {'LIGADA' if VISAO_HABILITADA else 'DESLIGADA'}")
    if VISAO_HABILITADA:
        print(" [SISTEMA] Visao ATIVA - F2 novamente para desligar")

def toggle_gatilho(e):
    if os.path.exists(BRAIN_FILE):
        try:
            with open(BRAIN_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            novo_estado = not data.get("trigger_active", False)
            data["trigger_active"] = novo_estado
            with open(BRAIN_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            play_beep("inicio" if novo_estado else "fim")
            print(f"\n[SISTEMA] Gatilho de Voz (F3): {'LIGADO' if novo_estado else 'DESLIGADO'}")
        except Exception as ex:
            pass

def requer_visao(texto):
    texto_min = texto.lower()
    padrao_palavras = r"\b(olha|veja|tela|imagem|foto|analisa|analise|lê|leia|vendo)\b"
    frases_exatas = ["o que é isso", "o que e isso", "o que tem na tela"]
    if re.search(padrao_palavras, texto_min): return True
    if any(frase in texto_min for frase in frases_exatas): return True
    return False

def requer_despertar(texto, nome_ai):
    texto_min = texto.lower()
    padrao_gatilhos = rf"\b({nome_ai.lower()}|ei|acorda|ouve|escuta)\b"
    return bool(re.search(padrao_gatilhos, texto_min))

def deve_analisar_tela():
    """Decide se deve analisar a tela agora"""
    import time
    agora = time.time()
    
    # Verifica se passou tempo suficiente desde última análise
    if agora - VISAO_ULTIMA_ANALISE < VISAO_INTERVALO_MINIMO:
        return False
    
    # 30% chance de analisar mesmo sem pedido explícito
    if visao_comentario_aleatorio and random.random() < 0.3:
        return True
    
    return False

def analisar_tela_com_qwen2vl(texto_pergunta=None):
    """Analisa a tela usando Qwen2-VL via Ollama"""
    try:
        b64_img = capturar_tela_b64()
        if not b64_img:
            return None
        
        if texto_pergunta:
            prompt = f"""O usuário perguntou: '{texto_pergunta}'. 
Analise a tela e responda de forma 自然 e curta (1-2 frases).
Se for anime/música/filme entretenimento: seja descontraído e divertido.
Se for algo sério (trabalho, código, notícias, documentos): seja objetivo e profissional."""
        else:
            prompt = """Olhe a tela e faça um comentário breve e natural.
Detecte o tipo de conteúdo:
- Se for anime, desenho, clipe de música, filme, série, game → seja DESCONTRAÍDO, faça piada ou observation divertida
- Se for trabalho, código, planilha, documento, notícias sérias → seja OBJETIVO e breve

Seja curto! 1 frase no máximo. Falando como uma persona."""
        
        messages = [
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                ]
            }
        ]
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": "qwen2.5vl:7b",
                "messages": messages,
                "stream": False,
                "temperature": 0.8
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            conteudo = data.get("message", {}).get("content", "").strip()
            if conteudo:
                import time
                global VISAO_ULTIMA_ANALISE
                VISAO_ULTIMA_ANALISE = time.time()
                return conteudo
    except Exception as e:
        print(f" [VISAO] Erro ao analisar: {e}")
    return None

# 🔥 O SEU NOVO INJETOR CIRÚRGICO DE COMANDOS DE MÚSICA
def detectar_comando_musica(texto):
    t = texto.lower().strip()
    if re.search(r'\b(pausar|pausa|despausa|resume)\b', t): return "PAUSE"
    if re.search(r'\b(para a música|para tudo|stop|desliga a música|calar a boca)\b', t): return "STOP"
    if re.search(r'\b(pula|próxima|skip|pular|passa)\b', t): return "SKIP"
    
    padrao_tocar = r'\b(toca|tocar|coloca|colocar|põe|bota)\b.*?(música|músicas|som|playlist|rock|kpop|pop|lofi|clássica|jazz|rap|funk|metal|eletrônica|abertura|encerramento)'
    if re.search(padrao_tocar, t):
        query = re.sub(r'\b(toca|tocar|coloca|colocar|põe|bota|a|o|um|umas|uma|alguma|algumas|música|músicas|som|playlist|ai|aí|pra|mim)\b', '', t).strip()
        query = re.sub(r'[^a-zA-Z0-9\s\-\u00C0-\u00FF]', '', query).strip()
        return f"PLAY:{query}" if query else "PLAY:uma música aleatória"
    
    if len(t.split()) <= 6 and re.match(r'^(toca|coloca|põe|bota)\b', t):
        query = re.sub(r'^(toca|coloca|põe|bota|a|o|um|uma|umas|alguma)\b', '', t).strip()
        return f"PLAY:{query}" if query else "PLAY:uma recomendação aleatória"
        
    return None

def capturar_tela_b64():
    try:
        import PIL
        from PIL import ImageGrab, Image
        img = ImageGrab.grab()
        img.thumbnail((1024, 1024))
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=70)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        print(f" Erro captura tela: {e}")
        return None
#endregion
# ======================================================
#region 🧠 BRAIN E PERSISTÊNCIA
# ======================================================
def carregar_brain():
    if not os.path.exists(BRAIN_FILE):    
        return {}, "Sistema Padrão", "Assistente", False, False, {"local": "nvidia"}, False # Agora retorna 7 valores corretos
    
    with open(BRAIN_FILE, 'r', encoding='utf-8') as f:
        brain = json.load(f)
        
    p = brain.get('personality', {'name': 'Assistente', 'role': 'Assistente de IA'})
    nome_ai = p.get('name', 'Assistente')
    traits = "\n- ".join(p.get('traits', []))
    
    r = "\n- ".join(brain.get('rules', {}).get('response_style', []))
    s = brain.get('emotional_analysis', {}).get('sentiment', 'Neutral')
    trigger = brain.get("trigger_active", False)
    discord_active = brain.get("discord_active", False) 
    modelos = brain.get("modelos_ativos", {"local": "nvidia", "discord": "groq"})
    vtuber_ativo = brain.get("vtuber_overlay_ativo", False)
    
    relacionamentos = brain.get('relationships', {})
    nome_user = list(relacionamentos.keys())[0] if relacionamentos else "Mestre"
    user_data = relacionamentos.get(nome_user, {})
    relacao = f"Nome do Usuário com quem você está falando: {nome_user}\nRelação: {user_data.get('relationship', 'Mestre')}\nComportamento com ele: {user_data.get('behavior', '')}"
    
    vocab_dict = brain.get('vocabulário', {})
    vocabulario = "\n- ".join([f"{k}: {v}" for k, v in vocab_dict.items()])

    tela_atual = brain.get('visual_context', {}).get('screen_content', '')

    prompt = (
        f"Nome: {nome_ai}\n"
        f"Papel: {p.get('role', 'Assistente')}\n\n"
        f"Traços de Personalidade:\n- {traits}\n\n"
        f"Sobre o Usuário:\n{relacao}\n\n"
        f"Estado Emocional: {s}\n\n"
        f"Diretrizes de Conversa (Incorpore de forma fluida e natural, varie as estruturas das frases):\n- {r}\n\n"
        f"Vocabulário Contextual (Use estas palavras/gírias de forma esporádica e APENAS se encaixar perfeitamente no assunto):\n- {vocabulario}"
    )
    
    if tela_atual:
        prompt += f"\n\n[CONTEXTO VISUAL ATUAL DA TELA]:\n- {tela_atual}"
    
    # 🔥 Retornando 7 variáveis rigorosamente na ordem correta
    return brain, prompt, nome_ai, trigger, discord_active, modelos, vtuber_ativo

def salvar_gatilho_brain(estado):
    if os.path.exists(BRAIN_FILE):
        with open(BRAIN_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
        data["trigger_active"] = estado
        with open(BRAIN_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4, ensure_ascii=False)

def salvar_discord_brain(estado):
    if os.path.exists(BRAIN_FILE):
        with open(BRAIN_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
        data["discord_active"] = estado
        with open(BRAIN_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4, ensure_ascii=False)

def salvar_visao_brain(descricao):
    if os.path.exists(BRAIN_FILE):
        with open(BRAIN_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if "visual_context" not in data: data["visual_context"] = {}
        data["visual_context"]["screen_content"] = descricao
        with open(BRAIN_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
#endregion
# ======================================================
#region 📚 GERENCIADOR DE MEMÓRIA
# ======================================================
def carregar_memoria():
    if not os.path.exists(MEMORIA_FILE): return {"master_summary": "", "recent_summaries": [], "mensagens": []}
    try:
        with open(MEMORIA_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {"master_summary": "", "recent_summaries": [], "mensagens": []}

def salvar_memoria(memoria):
    with open(MEMORIA_FILE, 'w', encoding='utf-8') as f:
        json.dump(memoria, f, indent=4, ensure_ascii=False)

def carregar_memoria_pesquisa():
    if not os.path.exists(SEARCH_MEMORY_FILE): return {"master_search_summary": "", "recent_searches": []}
    try:
        with open(SEARCH_MEMORY_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {"master_search_summary": "", "recent_searches": []}

def resumir_com_ollama(textos, comando):
    texto_junto = "\n".join(textos)
    prompt = f"{comando}\n\n{texto_junto}"
    try:
        resposta = get_ollama_response(prompt, "qwen2:7b", 0.3)
        return resposta if resposta else ""
    except Exception as e:
        print(f" Erro ao resumir memória: {e}")
        return ""

def salvar_memoria_simples(memoria):
    salvar_memoria(memoria)

async def gerenciar_memoria_pesquisa(query, resultados):
    memoria = carregar_memoria_pesquisa()
    memoria["recent_searches"].append({"query": query, "resultados": resultados[:400]})

    if len(memoria["recent_searches"]) >= 5:
        print("\n [SISTEMA] Otimizando banco de dados de Pesquisas (Resumindo web)...")
        textos_resumo = [f"Busca: '{m['query']}' | Resultado: {m['resultados']}" for m in memoria["recent_searches"]]
        if memoria["master_search_summary"]: textos_resumo.insert(0, f"Conhecimento Web Anterior: {memoria['master_search_summary']}")
        master_resumo = resumir_com_ollama(textos_resumo, "Você é um bibliotecário digital. Faça um resumo direto e conciso de todo o conhecimento e fatos adquiridos nestas pesquisas web. Descarte informações irrelevantes e foque apenas nos fatos úteis que podem servir de contexto no futuro.")
        if master_resumo:
            memoria["master_search_summary"] = master_resumo
            memoria["recent_searches"] = [] 

    with open(SEARCH_MEMORY_FILE, 'w', encoding='utf-8') as f: json.dump(memoria, f, indent=4, ensure_ascii=False)
    return memoria

def gerenciar_e_salvar_memoria(sender, message):
    memoria = carregar_memoria()
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    memoria["mensagens"].append({"timestamp": agora, "sender": sender, "message": message})

    if len(memoria["mensagens"]) >= 15:
        print("\n [SISTEMA] Otimizando memória (Resumindo conversas antigas)...")
        msgs_para_resumir = memoria["mensagens"][:10]
        textos_resumo = [f"[{m['timestamp']}] {m['sender']}: {m['message']}" for m in msgs_para_resumir]
        
        novo_resumo = resumir_com_ollama(textos_resumo, "Faça um resumo direto e curto sobre o que foi conversado nessas mensagens.")
        if novo_resumo:
            memoria["recent_summaries"].append(novo_resumo)
            memoria["mensagens"] = memoria["mensagens"][10:] 

        if len(memoria["recent_summaries"]) >= 5:
            print(" [SISTEMA] Consolidando Resumo Mestre...")
            textos_master = memoria["recent_summaries"].copy()
            if memoria["master_summary"]: textos_master.insert(0, f"Resumo Histórico: {memoria['master_summary']}")
            master_resumo = resumir_com_ollama(textos_master, "Integre todos esses resumos em um único 'Resumo Mestre' detalhando tudo o que já aconteceu com o usuário.")
            if master_resumo:
                memoria["master_summary"] = master_resumo
                memoria["recent_summaries"] = [] 

    salvar_memoria(memoria)
    return memoria

def construir_historico_para_api(sys_prompt, memoria, nome_ai, launcher=None):
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 🔥 INJETOR DE AUTORIDADE E CAPACIDADES CRÍTICAS 🔥
    prompt_completo = sys_prompt + f"\n\n[SISTEMA DE CAPACIDADES MÁXIMAS]:"
    prompt_completo += "\n1. CONTROLO DE MÚSICA: Você É o bot de música. Nunca diga que não pode tocar. Use OBRIGATORIAMENTE a tag <PLAY:pedido> para tocar qualquer coisa no Discord."
    prompt_completo += "\n2. CONTROLO DO PC: Você tem acesso total ao PC do Nero. Use <APP:abrir:alvo> ou <APP:fechar:alvo> para comandar o computador. Não invente que é apenas uma IA de texto."
    prompt_completo += "\n3. BUSCA WEB: Use [PESQUISAR: termo] para ler notícias e dados atuais. Você é conectada à internet."
    
    prompt_completo += f"\n\n[SISTEMA DE TEMPO]\nO momento atual exato é: {agora}.\nVocê recebe o horário para entender o ritmo da conversa."
    
    prompt_completo += "\n\n[REGRAS ESTRITAS DE RESPOSTA]:"
    prompt_completo += "\n- ZERO ROLEPLAY: Proibido narrar ações físicas, usar itálicos ou asteriscos (ex: *sorri*). Fale como uma pessoa real."
    prompt_completo += "\n- ZERO TAGS FALSAS: Nunca invente tags como <ignore> ou <pensamento>. Use apenas as oficiais ensinadas aqui."
    prompt_completo += "\n- SEJA CURTA E GROSSA: Responda em 1 ou 2 frases curtas. Você odeia textões e explicações desnecessárias."
    
    if launcher and hasattr(launcher, 'obter_nomes_dos_apps'):
        nomes_apps = launcher.obter_nomes_dos_apps()
        prompt_completo += f"\n\n[INTEGRAÇÃO COM O COMPUTADOR]:"
        prompt_completo += f"\n📂 APLICATIVOS INSTALADOS: {nomes_apps}."
        prompt_completo += "\nPara abrir ou pesquisar no navegador/youtube, use: <APP:abrir:alvo:termo_de_busca>."
        
        prompt_completo += "\n\n[MANUAL DO PLAYER DE MÚSICA]:"
        prompt_completo += "\n- TOCAR: <PLAY:nome_da_musica>"
        prompt_completo += "\n- PULAR: <SKIP>"
        prompt_completo += "\n- PAUSAR: <PAUSE>"
        prompt_completo += "\n- PARAR: <STOP>"
        prompt_completo += "\n🚨 REGRA DE OURO DA MÚSICA:"
        prompt_completo += "\n1. É OBRIGATÓRIO escrever uma frase sua (entre 1 e 7 palavras) ANTES de colocar a tag. NUNCA envie apenas a tag! (Ex: 'Aqui está a sua música. <PLAY:rock>')."
        prompt_completo += "\n2. NUNCA tente adivinhar nomes de músicas de animes ou séries. O sistema usa o YouTube, por isso gere a tag EXATAMENTE com as palavras que o usuário usou."
        prompt_completo += "\n3. É ESTRITAMENTE PROIBIDO tocar música do nada. NUNCA use a tag <PLAY> se o usuário não lhe deu uma ordem clara para tocar algo."
    # 🔥 Integração de Memória Avançada (ChromaDB)
    try:
        from Aliya.memoria_avancada import get_memoria
        mem = get_memoria()
        if mem:
            fatos = mem.buscar_fatos("usuario preferências interesses")
            if fatos:
                prompt_completo += f"\n\n[FATOS IMPORTANTES DO USUÁRIO]:\n" + "\n".join([f"- {f}" for f in fatos[:5]])
    except:
        pass
    
    # Integração de Memórias Antiga
    memoria_pesquisa = carregar_memoria_pesquisa()
    if memoria_pesquisa.get("master_search_summary"):
        prompt_completo += f"\n\n[CONHECIMENTO WEB ADQUIRIDO]:\n{memoria_pesquisa['master_search_summary']}"

    if memoria["master_summary"]:
        prompt_completo += f"\n\n[MEMÓRIA DE LONGO PRAZO]:\n{memoria['master_summary']}"
        
    if memoria["recent_summaries"]:
        prompt_completo += f"\n\n[ACONTECIMENTOS RECENTES]:\n" + "\n".join(memoria["recent_summaries"])

    # Construção do histórico para a API
    historico = [{"role": "system", "content": prompt_completo}]
    
    for m in memoria["mensagens"]:
        role = "assistant" if m["sender"] == nome_ai else "user"
        if role == "user":
            historico.append({"role": role, "content": f"[Enviado em {m['timestamp']}] {m['message']}"})
        else:
            msg_limpa = m['message'].split("] ", 1)[-1] if m['message'].startswith("[2026") else m['message']
            msg_limpa = re.sub(rf"^{nome_ai} disse:\s*", "", msg_limpa, flags=re.IGNORECASE)
            msg_limpa = re.sub(rf"^{nome_ai}:\s*", "", msg_limpa, flags=re.IGNORECASE)
            historico.append({"role": role, "content": msg_limpa.strip()})
            
    return historico
#endregion
# ======================================================
#region 🎵 FEEDBACKS SONOROS E ÁUDIO
# ======================================================
def play_beep(tipo="inicio"):
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2)
        duration = 0.1
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        freq = 800 if tipo == "inicio" else 400
        t = np.linspace(0, duration, n_samples, False)
        signal = np.sin(2 * np.pi * freq * t) * 0.3
        sound_array = (signal * 32767).astype(np.int16)
        stereo_array = np.column_stack((sound_array, sound_array))
        sound = pygame.sndarray.make_sound(stereo_array)
        sound.play()
    except Exception as e:
        pass

class LocalVoiceFilter:
    def __init__(self):
        self.model, _ = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False)
    
    def is_human_voice(self, audio_data, rate=16000):
        audio_int16 = np.frombuffer(audio_data, dtype=np.int16)
        if np.max(np.abs(audio_int16)) < 300: return False
        audio_float32 = audio_int16.astype(np.float32) / 32768.0
        tensor = torch.from_numpy(audio_float32)
        with torch.no_grad():
            confidence = self.model(tensor, rate).item()
        return confidence > 0.75

def tocar_audio(wav_file):
    import subprocess
    import os
    
    if not os.path.exists(wav_file):
        return
    
    ext = os.path.splitext(wav_file)[1].lower()
    if ext == ".mp3":
        subprocess.run(['powershell', '-c', f'(New-Object System.Media.SoundPlayer "{wav_file}").PlaySync()'], 
                     capture_output=True)
    else:
        subprocess.run(['powershell', '-c', f'(New-Object Media.SoundPlayer "{wav_file}").PlaySync()'], 
                     capture_output=True)

async def whisper_transcription(audio_frames, api_key):
    audio_data = b''.join(audio_frames)
    with io.BytesIO() as wb:
        with wave.open(wb, 'wb') as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(16000)
            wf.writeframes(audio_data)
        wb.seek(0)
        final_wav = wb.read()
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    head = {"Authorization": f"Bearer {api_key}"}
    files = {"file": ("input.wav", final_wav, "audio/wav"), "model": (None, "whisper-large-v3-turbo"), "language": (None, "pt")}
    resp = await asyncio.to_thread(requests.post, url, headers=head, files=files)
    return resp.json().get("text", "") if resp.status_code == 200 else None
#endregion
# ======================================================
#region 🕹️ CÉREBRO DA IA (PROCESSAMENTO INTEGRADO LLM + SCOUT)
# ======================================================
async def processar_ia(sys_prompt, texto, nome_ai, usuario_nome, launcher, modo_chat=False):
    if not modo_chat:
        print(f"{usuario_nome}: {texto}")
    
    texto_lower = texto.lower().strip()
    idiomas_disponiveis = listar_idiomas()
    idioma_trocado = None
    
    for codigo, info in idiomas_disponiveis.items():
        if f"mude para {info['nome'].lower()}" in texto_lower or f"fale em {info['nome'].lower()}" in texto_lower:
            set_idioma(codigo)
            idioma_trocado = info['nome']
            break
        if f"change to {info['nome_original'].lower()}" in texto_lower or f"speak {info['nome_original'].lower()}" in texto_lower:
            set_idioma(codigo)
            idioma_trocado = info['nome']
            break
    
    idioma_atual = get_idioma_atual()
    instrucoes_idioma = {
        "pt": "IDIOMA PRINCIPAL: Responda em Português do Brasil. Fale naturalmente.",
        "en": "IDIOMA PRINCIPAL: Respond in English. Speak naturally.",
        "fr": "IDIOMA PRINCIPAL: Répondez en français. Parlez naturellement.",
        "ru": "IDIOMA PRINCIPAL: Отвечайте на русском языке. Говорите естественно."
    }
    
    memoria_atual = carregar_memoria()
    
    historico_api = construir_historico_para_api(sys_prompt, memoria_atual, nome_ai, launcher)
    
    if historico_api and historico_api[0].get("role") == "system":
        historico_api[0]["content"] += f"\n\n{instrucoes_idioma.get(idioma_atual, instrucoes_idioma['pt'])}"
    
    if idioma_trocado:
        print(f" [SISTEMA] Idioma mudado para: {idioma_trocado}")
        if modo_chat:
            return f"✅ Idioma alterado para {idioma_trocado}!"
    
    # 🔥 INJETOR DE PRESSÃO: Força o LLM a não esquecer a tag da música
    comando_musica = detectar_comando_musica(texto)
    if comando_musica:
        alerta = f"\n\n[ALERTA DE SISTEMA DO CÉREBRO]: Você OBRIGATORIAMENTE deve incluir a tag <{comando_musica}> no final da sua próxima fala para a música obedecer ao usuário. Sem a tag, a música não mudará!"
        historico_api[-1]["content"] += alerta
    
    # 👁️ LÓGICA DE VISÃO ATIVA (Qwen2-VL via Ollama)
    descricao_tela = None
    if VISAO_HABILITADA:
        # Verifica se o usuário pediu para ver algo
        if requer_visao(texto):
            print(" [VISAO] Analisando tela por pedido...")
            descricao_tela = analisar_tela_com_qwen2vl(texto)
        # Ou analisa aleatoriamente de vez em quando
        elif deve_analisar_tela():
            print(" [VISAO] Analisando tela brevemente...")
            descricao_tela = analisar_tela_com_qwen2vl()
        
        if descricao_tela:
            print(f" [VISAO] {descricao_tela[:80]}...")
            salvar_visao_brain(descricao_tela)
    
    # 🧠 LÓGICA DO CÉREBRO PRINCIPAL (apenas Ollama local)
    try:
        messages_ollama = []
        for msg in historico_api:
            role = msg.get("role", "user")
            if role == "system": role = "user"
            content = msg.get("content", "")
            messages_ollama.append({"role": role, "content": content})
        
        if not messages_ollama:
            messages_ollama = [{"role": "user", "content": "Olá"}]
        
        last_message = messages_ollama[-1]["content"]
        resposta_inicial = await asyncio.to_thread(get_ollama_response, last_message, "phi3:mini", 0.7)
        
        if not resposta_inicial:
            print(" Erro: Ollama não respondeu")
            resposta_inicial = "Desculpe, tive um problema ao processar sua solicitação."
        
        resposta_final = resposta_inicial
        precisa_nova_resposta = False

        # 🔥 1. INTERCEPTADOR E LIMPEZA DE MÚSICA LOCAL
        match_musica = re.search(r'<(PLAY:[^>]+|SKIP|PAUSE|STOP|RESUME)[^>]*>', resposta_inicial, re.IGNORECASE)
        if match_musica:
            tag_musica = match_musica.group(1).upper()
            tag_completa = match_musica.group(0)
            
            resposta_inicial = resposta_inicial.replace(tag_completa, "").strip()
            resposta_final = resposta_inicial 

            try:
                if os.path.exists(BRAIN_FILE):
                    with open(BRAIN_FILE, "r+", encoding="utf-8") as f:
                        brain_data = json.load(f)
                        brain_data["pending_music"] = f"<{tag_musica}>"
                        f.seek(0)
                        json.dump(brain_data, f, indent=4, ensure_ascii=False)
                        f.truncate()
                print(f"[SISTEMA] Comando de musica enviado ao Discord: <{tag_musica}>")
            except Exception as e:
                print(f"❌ Erro ao enviar comando remoto para o Discord: {e}")

        # 🔥 2. VERIFICAÇÃO DE AÇÕES (APP E PESQUISA)
        if "<APP:" in resposta_inicial:
            resultado_app = launcher.process_llm_tag(resposta_inicial)
            if resultado_app:
                historico_api.append({"role": "assistant", "content": resposta_inicial})
                historico_api.append({"role": "user", "content": f"[SISTEMA DE AUTOMAÇÃO]: {resultado_app}"})
                precisa_nova_resposta = True

        if "PESQUISAR:" in resposta_inicial.upper():
            match = re.search(r"[\[<]PESQUISAR:\s*(.*?)[\]>]", resposta_inicial, re.IGNORECASE)
            if match:
                termo = match.group(1).strip()
                print(f" [SISTEMA] IA ativou busca autônoma para: '{termo}'")
                
                resultados_web = search_ddg.search_ddg(termo)
                await gerenciar_memoria_pesquisa(termo, resultados_web)
                
                if not precisa_nova_resposta:
                    msg_limpa = re.sub(r"[\[<]PESQUISAR:.*?[\]>]", "", resposta_inicial, flags=re.IGNORECASE).strip()
                    if msg_limpa:
                        historico_api.append({"role": "assistant", "content": msg_limpa})
                
                historico_api.append({"role": "user", "content": f"[SISTEMA DE BUSCA]: Resultados encontrados para '{termo}':\n{resultados_web}"})
                precisa_nova_resposta = True

        if precisa_nova_resposta:
            historico_api.append({"role": "user", "content": "Agora dê a sua resposta definitiva ao usuário incorporando o que aconteceu. REGRA ABSOLUTA: Fale com a sua personalidade de forma fluida. É PROIBIDO FAZER ROLEPLAY DE AÇÕES (NUNCA use asteriscos). NUNCA use a palavra 'pesquisa', não diga que buscou na web, e não mencione tags ou comandos. Aja simplesmente como se você tivesse lembrado dessa informação de cabeça."})
            
            prompt_final = ""
            for msg in historico_api:
                prompt_final += f"{msg.get('role', 'user')}: {msg.get('content', '')}\n"
            resposta_final = await asyncio.to_thread(get_ollama_response, prompt_final, "phi3:mini", 0.7)

        # 🧹 LIMPEZA BRUTAL FINAL: Remove qualquer outra tag <...> do terminal 
        resposta_final = re.sub(r'<[^>]+>', '', resposta_final).strip()

        # 🔥 NOVO: Se a IA enviar só a tag e a resposta ficar vazia, o próprio LLM gera a frase curta!
        if not resposta_final:
            prompt_fallback = f"system: Ava como {nome_ai}, usando a sua personalidade. Fale uma frase curta (entre 1 a 7 palavras) confirmando que completou o comando. Não use tags."
            resposta_final = await asyncio.to_thread(get_ollama_response, prompt_fallback, "phi3:mini", 0.9)
            if not resposta_final:
                resposta_final = "Feito."

        print(f"{nome_ai}: {resposta_final}")
        await speak_with_sbv2(resposta_final)
        
    except Exception as e:
        print(f" Erro na API LLM (Ollama): {e}")
#endregion
# ======================================================
# region 🎤 MODOS DE OPERAÇÃO
# ======================================================
async def run_modo_continuo(sys_prompt, voice_filter, api_key_whisper, nome_ai, usuario_nome, launcher):
    print("\n" + "="*30)
    print(" MODO VOZ ATIVA (ESCUTA CONTÍNUA)")
    print("F1: Gatilho de Voz | F2: Visão Computacional | HOME: Menu")
    print("="*30)
    
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=512)
    frames, is_recording, silence_timer = [], False, 0

    while True:
        if keyboard.is_pressed('home'): break

        data = stream.read(512, exception_on_overflow=False)
        if voice_filter.is_human_voice(data):
            if not is_recording: is_recording = True
            frames.append(data); silence_timer = 0
        elif is_recording:
            silence_timer += 1
            if silence_timer > 35: # Tempo de silêncio para processar
                is_recording = False
                texto = await whisper_transcription(frames, api_key_whisper)
                frames = []
                if texto:
                    # 🔥 LÊ O ESTADO ATUALIZADO DO GATILHO ANTES DE PROCESSAR
                    _, _, _, trigger_ativo, _, _, *_ = carregar_brain()
                    if trigger_ativo:
                        if requer_despertar(texto, nome_ai): 
                            await processar_ia(sys_prompt, texto, nome_ai, usuario_nome, launcher, modo_chat=False)
                        else:
                            print(f" [IGNORADO] Áudio captado: '{texto}' (Palavra de despertar não detetada)")
                    else:
                        await processar_ia(sys_prompt, texto, nome_ai, usuario_nome, launcher, modo_chat=False)
        await asyncio.sleep(0.01)
    stream.stop_stream(); stream.close(); p.terminate()
    
async def run_modo_click(sys_prompt, api_key_whisper, nome_ai, usuario_nome, launcher):
    print("\n" + "="*30)
    print(" MODO CLICK-TO-TALK")
    print("R-SHIFT: Clica Grava / Clica Envia")
    print("F3: Gatilho | F2: Visão | HOME: Menu")
    print("="*30)
    
    RATE = 16000
    CHUNK = 1024

    while True:
        try:
            while True:
                if keyboard.is_pressed('home'): return
                if keyboard.is_pressed('right shift'):
                    play_beep("inicio")
                    break
                await asyncio.sleep(0.05)

            while keyboard.is_pressed('right shift'): await asyncio.sleep(0.01)

            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
            frames = []
            
            print(" A gravar... (Clica R-SHIFT para enviar)")
            while True:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
                
                if keyboard.is_pressed('home'):
                    stream.stop_stream(); stream.close(); p.terminate()
                    return
                if keyboard.is_pressed('right shift'):
                    play_beep("fim")
                    break
                await asyncio.sleep(0.001)
                
            stream.stop_stream(); stream.close(); p.terminate()
            print(" A enviar para a IA...")
            while keyboard.is_pressed('right shift'): await asyncio.sleep(0.01)

            texto = await whisper_transcription(frames, api_key_whisper)
            if texto: 
                # 🔥 LÊ O ESTADO ATUALIZADO DO GATILHO ANTES DE PROCESSAR
                _, _, _, trigger_ativo, _, _, *_ = carregar_brain()
                if trigger_ativo:
                    if nome_ai.lower() in texto.lower(): 
                        await processar_ia(sys_prompt, texto, nome_ai, usuario_nome, launcher, modo_chat=False)
                    else:
                        print(f" [IGNORADO] Gatilho ativo, mas o nome '{nome_ai}' não foi mencionado.")
                else:
                    await processar_ia(sys_prompt, texto, nome_ai, usuario_nome, launcher, modo_chat=False)

        except Exception as e:
            print(f" Erro no Modo Clique: {e}")
            break
#endregion
# ======================================================
#region 🚀 MAIN
# ======================================================
async def main():
    brain_raw, sys_prompt, nome_ai, trigger, discord_active, modelos, vtuber_ativo = carregar_brain()

    print(f"Iniciando Painel de Configuracoes em segundo plano (Pressione F4 para acessar)...")
    gui_thread = threading.Thread(target=RemGUI.iniciar_gui_loop, args=(nome_ai,), daemon=True)
    gui_thread.start()

    # 🔥 REGISTRANDO OS ATALHOS GLOBAIS ABSOLUTOS (AGORA APENAS UMA ÚNICA VEZ!)
    keyboard.add_hotkey('f4', RemGUI.toggle)
    keyboard.on_press_key('f2', toggle_visao)
    keyboard.on_press_key('f3', toggle_gatilho) 

    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
    GROQ_API_KEY_LLM = os.getenv("GROQ_API_KEY_LLM")
    GROQ_API_KEY_VISION = os.getenv("NVIDIA_API_KEY")

    # ============================================
    # 🚀 INICIALIZAÇÃO AUTOMÁTICA DOS SERVIÇOS
    # ============================================
    
    # 1. Iniciar Ollama
    print(" [OLLAMA] Verificando servidor local...")
    if not verificar_ollama():
        print(" [OLLAMA] Servidor não encontrado. Tentando iniciar...")
        iniciar_ollama_se_nao_estiver()
    else:
        print(" [OLLAMA] Servidor ja esta rodando!")
    
    # 2. TTS Coqui XTTS v2 (voice cloning!)
    from Aliya.tts_engine import inicializar_coqui
    try:
        inicializar_coqui()
    except Exception as e:
        print(f" [TTS] Coqui XTTS erro: {e}")
        print(" [TTS] Usando Windows TTS como fallback")
    
    # Atualiza as variáveis do cérebro caso o usuário tenha salvo algo no painel
    brain_raw, sys_prompt, nome_ai, trigger, discord_active, modelos, vtuber_ativo = carregar_brain()

    # 🔥 CHAMA O SCRIPT DO VTUBER SE ESTIVER ATIVADO
    if vtuber_ativo:
        print("🎭 Iniciando módulo VTuber Overlay em segundo plano...")
        try:
            subprocess.Popen([sys.executable, "Arcana/Net/vtuber_overlay.py"])
        except Exception as e:
            print(f"❌ Erro ao iniciar o VTuber Overlay: {e}")

    # 🧠 CÉREBRO LOCAL (apenas Ollama)
    client_llm = None  # Não usado mais
    
    voice_filter = LocalVoiceFilter()
    
    # Puxando o nome do Usuário dinamicamente
    relacionamentos_main = brain_raw.get('relationships', {})
    usuario_nome = list(relacionamentos_main.keys())[0] if relacionamentos_main else "Usuário"
    
    # 🔥 INICIA O MÓDULO DE AUTOMAÇÃO INVISÍVEL
    launcher = AppLauncher()

    carregar_memoria()
    
    # [O ERRO ESTAVA AQUI: Existia um keyboard.on_press_key('f2', toggle_visao) fantasma! Removido.]

    while True:
        # Verificar comandos do AHK
        cmd_ahk = ler_comando_ahk()
        if cmd_ahk:
            print(f"\n [AHK] Comando recebido: {cmd_ahk}")
            if cmd_ahk == "GATILHO":
                print("\n[SISTEMA] Gatilho ativado!")
            elif cmd_ahk == "VISAO":
                toggle_visao(None)
            elif cmd_ahk == "TOGGLE":
                toggle_gatilho(None)
            elif cmd_ahk == "PAINEL":
                RemGUI.toggle()
        
        _, _, _, trigger, discord_active, modelos, _ = carregar_brain()
        print(f"\n{'='*15} MENU {nome_ai} {'='*15}")
        print(f"Gatilho F3: {'LIGADO' if trigger else 'DESLIGADO'}")
        print(f"Visão F2: {'LIGADA' if VISAO_HABILITADA else 'DESLIGADA'}")
        print(f"Discord: {'LIGADO' if discord_active else 'DESLIGADO'}")
        print(f"Utilizador atual: {usuario_nome}")
        print("| 1. Chat")
        print("| 2. Voz Contínua")
        print("| 3. Click-to-Talk")
        print("| 0. Sair")
        
        op = await asyncio.to_thread(input, "Opção: ")
        if op == '1':
            while True:
                msg = await asyncio.to_thread(input, "Você: ")
                if msg == '0': break
                await processar_ia(sys_prompt, msg, nome_ai, usuario_nome, launcher, modo_chat=True)
        elif op == '2': await run_modo_continuo(sys_prompt, voice_filter, GROQ_API_KEY_LLM, nome_ai, usuario_nome, launcher)
        elif op == '3': await run_modo_click(sys_prompt, GROQ_API_KEY_LLM, nome_ai, usuario_nome, launcher)
        
        elif op == '0': break
if __name__ == "__main__":
    asyncio.run(main())
#endregion
# ============//======================//================