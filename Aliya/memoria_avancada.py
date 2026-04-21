import os
import json
import chromadb
from chromadb.config import Settings
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class MemoriaAvancada:
    def __init__(self, pasta_dados="Arcana/armazen"):
        self.pasta_dados = pasta_dados
        os.makedirs(pasta_dados, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=pasta_dados)
        
        try:
            self.colecao_fatos = self.client.get_collection("fatos")
        except:
            self.colecao_fatos = self.client.create_collection("fatos", metadata={"description": "Fatos duradouros sobre o usuario"})
        
        try:
            self.colecao_conversas = self.client.get_collection("conversas")
        except:
            self.colecao_conversas = self.client.create_collection("conversas", metadata={"description": "Conversas resumidas"})
        
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    
    def extrair_fatos(self, conversas):
        import requests
        prompt = f"""Você é um extrator de fatos. Analise estas mensagens e extraia APENAS fatos importantes e duradouros sobre o usuário.
Cada fato deve ser uma frase curta e independente.
 Exemplos de fatos:
- "Guilherme gosta de anime romance"
- "Prefere conversar à noite"
- "Está Estudando Python"

Mensagens:
{conversas}

Fatos extraidos (um por linha):"""
        
        try:
            r = requests.post(
                f"{self.ollama_url}/api/chat",
                json={"model": "qwen2:7b", "messages": [{"role": "user", "content": prompt}], "stream": False},
                timeout=60
            )
            if r.status_code == 200:
                return r.json().get("message", {}).get("content", "")
        except Exception as e:
            print(f" [MEMORIA] Erro ao extrair fatos: {e}")
        return ""
    
    def adicionar_fatos(self, fatos):
        if not fatos:
            return
        lista_fatos = [f.strip() for f in fatos.split("\n") if f.strip() and len(f.strip()) > 10]
        for i, fato in enumerate(lista_fatos):
            try:
                self.colecao_fatos.add(
                    documents=[fato],
                    ids=[f"fato_{datetime.now().timestamp()}_{i}"]
                )
            except Exception as e:
                pass
    
    def buscar_fatos(self, query, n=5):
        try:
            resultados = self.colecao_fatos.query(
                query_texts=[query],
                n_results=n
            )
            return resultados.get("documents", [[]])[0]
        except:
            return []
    
    def adicionarConversa(self, resumo):
        if not resumo:
            return
        try:
            self.colecao_conversas.add(
                documents=[resumo],
                ids=[f"conv_{datetime.now().timestamp()}"]
            )
        except Exception as e:
            print(f" [MEMORIA] Erro ao guardar conversa: {e}")
    
    def buscar_conversas(self, query, n=3):
        try:
            resultados = self.colecao_conversas.query(
                query_texts=[query],
                n_results=n
            )
            return resultados.get("documents", [[]])[0]
        except:
            return []
    
    def consolidar_fatos(self, fatos_recentes):
        if not fatos_recentes:
            return
        self.adicionar_fatos(fatos_recentes)
    
    def limpar_memoria_antiga(self, dias=30):
        pass

memoria_global = None

def inicializar_memoria():
    global memoria_global
    memoria_global = MemoriaAvancada()
    return memoria_global

def get_memoria():
    global memoria_global
    if memoria_global is None:
        memoria_global = inicializar_memoria()
    return memoria_global