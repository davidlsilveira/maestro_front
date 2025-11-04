import json

def load_data(path: str):
    """Carrega dados mockados de um arquivo JSON."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar {path}: {e}")
        return []
