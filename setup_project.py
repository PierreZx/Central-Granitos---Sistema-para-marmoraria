import os
from pathlib import Path

# Nome do projeto
project_name = "marmoraria-app"

# Estrutura de pastas e arquivos
structure = {
    "assets": [],
    "data": [], # Mantemos caso precise de cache local
    "src": [
        "__init__.py",
        "config.py",
    ],
    "src/models": [
        "__init__.py",
        "chapa_model.py",  # Adaptado para Firebase
        "orcamento_model.py"
    ],
    "src/controllers": [
        "__init__.py",
        "auth_controller.py",
        "stock_controller.py"
    ],
    "src/services": [ # Nova pasta para isolar a conexão com Firebase
        "__init__.py",
        "firebase_service.py" 
    ],
    "src/views": [
        "__init__.py",
        "login_view.py",
        "dashboard_view.py",
        "inventory_view.py",
    ],
    "src/views/components": [
        "__init__.py",
        "sidebar.py",
        "chapa_card.py"
    ],
}

# Conteúdo base para arquivos específicos
file_contents = {
    ".gitignore": """
__pycache__/
*.py[cod]
.venv/
.env
serviceAccountKey.json
*.log
.DS_Store
""",
    "requirements.txt": """
flet
firebase-admin
python-dotenv
""",
    "README.md": f"# {project_name}\n\nSistema de gestão para marmoraria usando Flet e Firebase.",
    "main.py": """
import flet as ft
# A importação das views virá depois

def main(page: ft.Page):
    page.title = "Marmoraria App"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    page.add(ft.Text("Ambiente Configurado com Sucesso!", size=30))

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
"""
}

def create_structure():
    base_path = Path(project_name)
    
    # Cria a pasta raiz
    if not base_path.exists():
        base_path.mkdir()
        print(f"✅ Pasta raiz '{project_name}' criada.")
    else:
        print(f"ℹ️ Pasta '{project_name}' já existe.")

    # Criação dos arquivos na raiz
    for filename, content in file_contents.items():
        file_path = base_path / filename
        if not file_path.exists():
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content.strip())
            print(f"📄 Arquivo criado: {filename}")

    # Criação da estrutura interna
    for folder, files in structure.items():
        folder_path = base_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"📂 Pasta criada: {folder}")
        
        for file in files:
            file_path = folder_path / file
            if not file_path.exists():
                with open(file_path, "w") as f:
                    pass # Cria arquivo vazio
                print(f"   📄 Arquivo criado: {file}")

    print("\n🚀 Estrutura finalizada! Agora entre na pasta:")
    print(f"cd {project_name}")

if __name__ == "__main__":
    create_structure()