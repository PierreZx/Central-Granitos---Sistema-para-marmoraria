import flet as ft

# --- IDENTIDADE VISUAL: VINHO & BRONZE ---
# Cores principais para branding
COLOR_PRIMARY = "#6A1B1B"      # Vinho Escuro (Elegante e Profissional)
COLOR_SECONDARY = "#B8860B"    # Bronze/Dourado Escuro (Para destaques)
COLOR_TERTIARY = "#F5DEB3"     # Bege Suave (Detalhes sutis)
COLOR_BACKGROUND = "#FDFCFB"   # Off-white quente (Fundo)
COLOR_WHITE = "#FFFFFF"
COLOR_TEXT = "#2C1810"         # Marrom café (Texto principal)

# --- CORES DE STATUS ---
# Cores semânticas para feedback do usuário
COLOR_SUCCESS = "#2E7D32"      # Verde (Sucesso/Pago/Finalizado)
COLOR_WARNING = "#F57C00"      # Laranja (Pendente/Alerta)
COLOR_ERROR = "#C62828"        # Vermelho (Atrasado/Erro/Cancelar)
COLOR_INFO = "#1565C0"         # Azul (Informações/Detalhes)

# --- SOMBRAS E BORDAS ---
# Usando opacidade HEX (ex: 1A = 10% de preto)
SHADOW_SM = ft.BoxShadow(
    blur_radius=8,
    spread_radius=1,
    color="#0D000000",
    offset=ft.Offset(0, 2)
)

SHADOW_MD = ft.BoxShadow(
    blur_radius=20,
    spread_radius=-5,
    color="#1A000000",
    offset=ft.Offset(0, 8)
)

# Raio de borda consistente em todo o app
BORDER_RADIUS_SM = 8
BORDER_RADIUS_MD = 12
BORDER_RADIUS_LG = 20

# --- TIPOGRAFIA ---
# Tamanhos padrão para manter a hierarquia visual
FONT_SIZE_H1 = 28
FONT_SIZE_H2 = 20
FONT_SIZE_BODY = 14

# --- CREDENCIAIS DE ACESSO ---
# Centralização de dados sensíveis para facilitar manutenção
AUTH_EMAIL = "marmoraria.central@gmail.com"
AUTH_PASSWORD = "MarmorariaC55"
ROLE_ADMIN = "admin"
ROLE_PRODUCAO = "producao"

# --- CONFIGURAÇÕES DE LAYOUT ---
PADDING_VIEW = 30  # Padding padrão para telas Desktop