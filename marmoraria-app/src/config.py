import flet as ft

# Paleta de Cores (Use Strings Hexadecimais para evitar erros de versão)
COLOR_PRIMARY = "#8A1C26"    
COLOR_SECONDARY = "#6D4C3D"  
COLOR_TEXT = "#333333"       
COLOR_BACKGROUND = "#F7F7F7" 
COLOR_WHITE = "#FFFFFF"

# Estilo padrão dos Botões
BUTTON_STYLE = ft.ButtonStyle(
    shape=ft.RoundedRectangleBorder(radius=8),
    bgcolor=COLOR_PRIMARY,
    color=COLOR_WHITE,
)

# Credencial administrativa padrão (usada como fallback e para criação inicial no Firestore)
AUTH_EMAIL = "marmoraria.central@gmail.com"
AUTH_PASSWORD = "MarmorariaC55"