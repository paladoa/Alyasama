import json
import os

IDIOMA_FILE = "Arcana/armazen/idioma.json"

IDIOMAS_SUPORTADOS = {
    "pt": {"nome": "Português", "nome_original": "Português", "codigo": "pt"},
    "en": {"nome": "Inglês", "nome_original": "English", "codigo": "en"},
    "fr": {"nome": "Francês", "nome_original": "Français", "codigo": "fr"},
    "ru": {"nome": "Russo", "nome_original": "Русский", "codigo": "ru"}
}

def carregar_idioma():
    if not os.path.exists(IDIOMA_FILE):
        return "pt"
    try:
        with open(IDIOMA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("idioma_atual", "pt")
    except:
        return "pt"

def salvar_idioma(codigo):
    os.makedirs("Arcana/armazen", exist_ok=True)
    with open(IDIOMA_FILE, 'w', encoding='utf-8') as f:
        json.dump({"idioma_atual": codigo}, f, indent=4)

def get_idioma_atual():
    return carregar_idioma()

def set_idioma(codigo):
    if codigo in IDIOMAS_SUPORTADOS:
        salvar_idioma(codigo)
        return True
    return False

def listar_idiomas():
    return IDIOMAS_SUPORTADOS