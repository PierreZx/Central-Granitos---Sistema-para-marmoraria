# src/config.py
import flet as ft

# --- IDENTIDADE VISUAL: VINHO & BRONZE ---
COLOR_PRIMARY = "#6A1B1B"      # Vinho Escuro
COLOR_SECONDARY = "#B8860B"    # Bronze/Dourado Escuro
COLOR_TERTIARY = "#F5DEB3"     # Bege Suave
COLOR_BACKGROUND = "#FDFCFB"   # Off-white quente
COLOR_WHITE = "#FFFFFF"
COLOR_TEXT = "#2C1810"         # Marrom café

# --- CORES DE STATUS ---
COLOR_SUCCESS = "#2E7D32"
COLOR_WARNING = "#F57C00"
COLOR_ERROR = "#C62828"
COLOR_INFO = "#1565C0"

# --- SOMBRAS E BORDAS ---
SHADOW_SM = ft.BoxShadow(
    blur_radius=8,
    spread_radius=1,
    color="#0D000000",
    offset=ft.Offset(0, 2)
)

SHADOW_MD = ft.BoxShadow(
    blur_radius=15, # Reduzido levemente para performance mobile
    spread_radius=-3,
    color="#1A000000",
    offset=ft.Offset(0, 5)
)

BORDER_RADIUS_SM = 8
BORDER_RADIUS_MD = 12
BORDER_RADIUS_LG = 20

# --- TIPOGRAFIA ---
FONT_SIZE_H1 = 28
FONT_SIZE_H2 = 20
FONT_SIZE_BODY = 14

# --- CREDENCIAIS DE ACESSO ---
AUTH_EMAIL = "marmoraria.central@gmail.com"
AUTH_PASSWORD = "MarmorariaC55"
ROLE_ADMIN = "admin"
ROLE_PRODUCAO = "producao"

# --- CONFIGURAÇÕES DE LAYOUT (ADAPTADO APK) ---
PADDING_VIEW = 30  # Desktop
PADDING_MOBILE = 15 # Novo: Padding ideal para telas de celular