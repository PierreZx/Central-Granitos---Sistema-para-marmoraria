import flet as ft

# --- IDENTIDADE VISUAL: VINHO & BRONZE ---
COLOR_PRIMARY = "#6A1B1B"      # Vinho Escuro (Elegante e Profissional)
COLOR_SECONDARY = "#B8860B"    # Bronze/Dourado Escuro (Para destaques)
COLOR_TERTIARY = "#F5DEB3"     # Bege Suave (Detalhes sutis)
COLOR_BACKGROUND = "#FDFCFB"   # Off-white quente (não cansa a vista)
COLOR_WHITE = "#FFFFFF"
COLOR_TEXT = "#2C1810"         # Marrom café bem escuro

# --- CORES DE STATUS ---
COLOR_SUCCESS = "#2E7D32" # Verde Floresta
COLOR_WARNING = "#F57C00" # Laranja Queimado
COLOR_ERROR = "#C62828"   # Vermelho Sangue
COLOR_INFO = "#1565C0"    # Azul

# --- SOMBRAS E BORDAS ---
# Corrigido: Usando HEX Code direto (#AARRGGBB) para evitar o erro 'ft.colors'
SHADOW_SM = ft.BoxShadow(
    blur_radius=8,
    color="#0D000000", # Preto com 5% de opacidade
    offset=ft.Offset(0, 2)
)

SHADOW_MD = ft.BoxShadow(
    blur_radius=15,
    color="#1A000000", # Preto com 10% de opacidade
    offset=ft.Offset(0, 4)
)

BORDER_RADIUS_MD = 12
BORDER_RADIUS_LG = 15

# --- CREDENCIAIS DE ACESSO ---
AUTH_EMAIL = "marmoraria.central@gmail.com"
AUTH_PASSWORD = "MarmorariaC55"