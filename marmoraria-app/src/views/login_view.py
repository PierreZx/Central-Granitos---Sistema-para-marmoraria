import flet as ft
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_WHITE

def LoginView(page: ft.Page):
    
    # --- Lógica de Login ---
    def realizar_login(e):
        if campo_usuario.value == "admin" and campo_senha.value == "123":
            # Efeito de loading no botão
            btn_entrar.disabled = True
            progresso = ft.ProgressRing(width=20, height=20, stroke_width=2, color=COLOR_WHITE)
            btn_entrar.content = ft.Row(
                [progresso, ft.Text("Autenticando...")],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            )
            page.update()
            
            # Simular processamento
            import time
            time.sleep(0.5)
            
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Login realizado com sucesso!", color=COLOR_WHITE),
                bgcolor=ft.Colors.GREEN_400,
                behavior=ft.SnackBarBehavior.FLOATING,
                duration=2000,
                elevation=10
            )
            page.snack_bar.open = True
            page.go("/dashboard")
        else:
            # Efeito de shake no formulário
            import time
            container_form.offset = ft.Offset(-0.02, 0)
            page.update()
            time.sleep(0.05)
            container_form.offset = ft.Offset(0.02, 0)
            page.update()
            time.sleep(0.05)
            container_form.offset = ft.Offset(0, 0)
            page.update()
            
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Usuário ou senha incorretos", color=COLOR_WHITE),
                bgcolor=ft.Colors.RED_400,
                behavior=ft.SnackBarBehavior.FLOATING,
                duration=3000,
                elevation=10
            )
            page.snack_bar.open = True
            page.update()
    
    def on_submit(e):
        realizar_login(e)
    
    # --- Estilos Personalizados ---
    estilo_borda_arredondada = 25
    estilo_sombra = ft.BoxShadow(
        blur_radius=20,
        color="#00000019",
        offset=ft.Offset(0, 4)
    )
    
    # --- Gradiente de Fundo ---
    gradiente_fundo = ft.LinearGradient(
        begin=ft.alignment.top_left,
        end=ft.alignment.bottom_right,
        colors=[
            ft.Colors.BLUE_GREY_50,
            ft.Colors.GREY_100,
            ft.Colors.WHITE,
        ]
    )
    
    # --- Componentes do Formulário ---
    
    logo = ft.Container(
        content=ft.Image(
            src="logo.png",
            width=180,
            height=180,
            fit=ft.ImageFit.CONTAIN,
        ),
        padding=10
    )
    
    campo_usuario = ft.TextField(
        label="Usuário",
        hint_text="Digite seu usuário",
        width=350,
        height=56,
        text_size=16,
        border_radius=estilo_borda_arredondada,
        border_color=ft.Colors.TRANSPARENT,
        filled=True,
        fill_color=ft.Colors.WHITE,
        focused_border_color=COLOR_PRIMARY,
        focused_border_width=2,
        content_padding=20,
        cursor_color=COLOR_PRIMARY,
        prefix_icon=ft.Icon(ft.Icons.PERSON_OUTLINE, size=20, color=ft.Colors.GREY_500),
        on_submit=on_submit
    )
    
    campo_senha = ft.TextField(
        label="Senha",
        hint_text="Digite sua senha",
        password=True,
        can_reveal_password=True,
        width=350,
        height=56,
        text_size=16,
        border_radius=estilo_borda_arredondada,
        border_color=ft.Colors.TRANSPARENT,
        filled=True,
        fill_color=ft.Colors.WHITE,
        focused_border_color=COLOR_PRIMARY,
        focused_border_width=2,
        content_padding=20,
        cursor_color=COLOR_PRIMARY,
        prefix_icon=ft.Icon(ft.Icons.LOCK_OUTLINE, size=20, color=ft.Colors.GREY_500),
        on_submit=on_submit
    )
    
    btn_entrar = ft.ElevatedButton(
        content=ft.Text("Entrar", size=16, weight=ft.FontWeight.W_600),
        width=350,
        height=56,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=estilo_borda_arredondada),
            bgcolor={
                ft.ControlState.DEFAULT: COLOR_PRIMARY,
                ft.ControlState.HOVERED: COLOR_PRIMARY + "E6",
                ft.ControlState.FOCUSED: COLOR_PRIMARY + "CC",
            },
            color=COLOR_WHITE,
            elevation={
                ft.ControlState.DEFAULT: 4,
                ft.ControlState.HOVERED: 8,
                ft.ControlState.FOCUSED: 2,
            },
            animation_duration=200,
            padding=20,
        ),
        on_click=realizar_login
    )
    
    texto_esqueci_senha = ft.TextButton(
        text="Esqueceu sua senha?",
        style=ft.ButtonStyle(
            color=ft.Colors.GREY_600,
        )
    )
    
    texto_rodape = ft.Container(
        content=ft.Column([
            ft.Divider(height=1, color=ft.Colors.GREY_200),
            ft.Text("Central Granitos © 2025", size=12, color=ft.Colors.GREY_500),
            ft.Text("Todos os direitos reservados", size=10, color=ft.Colors.GREY_400),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=8),
        padding=ft.padding.only(top=20)
    )
    
    # Card do Formulário
    container_form = ft.Container(
        content=ft.Column(
            [
                logo,
                ft.Text("Bem-vindo de volta", 
                       size=28, 
                       weight=ft.FontWeight.W_700,
                       color=ft.Colors.GREY_800),
                ft.Text("Faça login para continuar", 
                       size=16, 
                       color=ft.Colors.GREY_600),
                ft.Divider(height=40, color=ft.Colors.TRANSPARENT),
                campo_usuario,
                ft.Divider(height=15, color=ft.Colors.TRANSPARENT),
                campo_senha,
                ft.Container(
                    content=texto_esqueci_senha,
                    alignment=ft.alignment.center_right,
                    width=350
                ),
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                btn_entrar,
                texto_rodape
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START,
            spacing=0,
        ),
        bgcolor=ft.Colors.WHITE,
        padding=40,
        border_radius=20,
        shadow=estilo_sombra,
        offset=ft.Offset(0, 0)
    )
    
    # Container da Imagem de Fundo (Desktop)
    container_imagem = ft.Container(
        content=ft.Stack([
            ft.Image(
                src="marmores.jpg",
                fit=ft.ImageFit.COVER,
                opacity=0.9,
            ),
            ft.Container(
                gradient=ft.LinearGradient(
                    begin=ft.alignment.center_left,
                    end=ft.alignment.center_right,
                    colors=[
                        "#00000099",
                        ft.Colors.TRANSPARENT
                    ]
                )
            )
        ]),
        expand=True
    )
    
    # Layout para Desktop
    layout_desktop = ft.Row(
        controls=[
            container_imagem,
            ft.Container(
                content=container_form,
                expand=True,
                alignment=ft.alignment.center,
                padding=40,
                bgcolor=gradiente_fundo
            )
        ],
        spacing=0,
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH
    )
    
    # Layout para Mobile
    layout_mobile = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    height=200,
                    content=ft.Image(
                        src="marmores.jpg",
                        fit=ft.ImageFit.COVER,
                        opacity=0.8,
                    ),
                    border_radius=ft.border_radius.only(bottom_left=40, bottom_right=40),
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                ),
                ft.Container(
                    content=container_form,
                    expand=True,
                    padding=20,
                    bgcolor=gradiente_fundo
                )
            ],
            spacing=0,
            expand=True,
        ),
        expand=True
    )
    
    # --- Responsividade Adaptativa ---
    def ajustar_layout(e=None):
        if page.width < 768:  # Mobile
            container_imagem.visible = False
            if hasattr(page, 'layout_atual') and page.layout_atual != 'mobile':
                page.controls[0].content = layout_mobile
                page.layout_atual = 'mobile'
        else:  # Desktop
            container_imagem.visible = True
            if hasattr(page, 'layout_atual') and page.layout_atual != 'desktop':
                page.controls[0].content = layout_desktop
                page.layout_atual = 'desktop'
        
        # Ajustar largura do formulário baseado na tela
        nova_largura = min(400, page.width - 100)
        campo_usuario.width = nova_largura
        campo_senha.width = nova_largura
        btn_entrar.width = nova_largura
        
        page.update()
    
    # Configurar página
    page.layout_atual = 'desktop' if page.width >= 768 else 'mobile'
    page.on_resize = ajustar_layout
    
    # Layout inicial baseado no tamanho atual
    layout_inicial = layout_mobile if page.width < 768 else layout_desktop
    
    return ft.View(
        route="/",
        padding=0,
        controls=[ft.Container(content=layout_inicial, expand=True)],
        bgcolor=gradiente_fundo
    )