# Alya - VTuber AI Assistant com Voice Cloning

Assistente virtual com IA que pode conversar em múltiplos idiomas e falar com sua voz clonada.

## Funcionalidades

- **Chatbot IA** - Usa Ollama com modelos locais (Qwen2.5-VL, DeepSeek-R1)
- **Análise de Tela** - Vision API para ver o que está na tela
- **Memória** - ChromaDB para lembrar conversas
- **Voice Cloning** - Coqui XTTS v2 para falar com sua voz

## Requisitos

- Windows 10/11
- Python 3.12
- GPU NVIDIA (RTX 4060 Ti+ recomendado)
- 15GB+ RAM livre

## Instalação

```bash
# Clone ou extraia o projeto
cd Alya2

# Crie ambiente virtual
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt

# Baixe modelos Ollama
ollama pull qwen2.5vl:7b
ollama pull deepseek-r1:1.5b

# Grave sua voz de referência
# grave um audio de 30 segundos falando em voz_referencia.wav

# Execute
.venv\Scripts\python run.py
```

## Uso

1. Execute `Alya.bat` no desktop
2. Digite sua mensagem
3. Alya responde falando com sua voz clonada!

## Estrutura

```
Alya2/
├── run.py              # Aplicação principal
├── Aliya/
│   ├── tts_engine.py  # Engine TTS (Coqui XTTS)
│   └── memoria_avancada.py # Sistema de memória
├── voz_referencia.wav # Sua voz (adicione este arquivo)
└── .venv/            # Ambiente virtual
```

## Idiomas

Suporta: Português, Inglês, Japonês, Chinês, Coreano, Russo e mais.

## Créditos

- [Coqui TTS](https://github.com/idiap/coqui-ai-TTS) - XTTS v2
- [Ollama](https://ollama.ai/) - Modelos locais
- [Qwen2.5-VL](https://huggingface.co/Qwen/Qwen2.5-VL) - Vision