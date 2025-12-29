import flet as ft
import flet.canvas as cv
from src.views.components.sidebar import Sidebar
from src.config import COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, COLOR_SECONDARY, COLOR_TEXT
from src.services import firebase_service
import math

def BudgetView(page: ft.Page):
    
    # --- Estado e Variáveis ---
    chapas_disponiveis = firebase_service.get_estoque_lista()
    
    opcoes_pedras = []
    mapa_precos = {} 
    
    for chapa in chapas_disponiveis:
        if int(chapa.get('quantidade', 0)) > 0:
            nome = chapa.get('nome', 'Sem Nome')
            preco = float(chapa.get('valor_m2', 0))
            texto_opcao = f"{nome} - R$ {preco:.2f}/m²"
            
            opcoes_pedras.append(ft.dropdown.Option(key=chapa['id'], text=texto_opcao))
            mapa_precos[chapa['id']] = preco

    # --- Componentes de Entrada ---
    dd_pedra = ft.Dropdown(
        label="Selecione a Pedra",
        options=opcoes_pedras,
        width=400,
        border_radius=10,
    )

    txt_largura = ft.TextField(label="Largura (cm)", suffix_text="cm", width=150, keyboard_type=ft.KeyboardType.NUMBER, border_radius=10)
    txt_altura = ft.TextField(label="Altura (cm)", suffix_text="cm", width=150, keyboard_type=ft.KeyboardType.NUMBER, border_radius=10)
    txt_custo_acabamento = ft.TextField(label="Custo Acabamento (Linear)", value="50.00", prefix_text="R$ ", width=200, keyboard_type=ft.KeyboardType.NUMBER, border_radius=10)

    # --- Componentes de Resultado ---
    lbl_total_pedra = ft.Text("R$ 0.00", size=16, color=ft.Colors.GREY_700)
    lbl_total_mao_obra = ft.Text("R$ 0.00", size=16, color=ft.Colors.GREY_700)
    lbl_total_geral = ft.Text("R$ 0.00", size=30, weight="bold", color=COLOR_PRIMARY)

    # --- O CANVAS (Área de Desenho) ---
    canvas_desenho = cv.Canvas(
        width=400,
        height=300,
        shapes=[],
        content=ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
            alignment=ft.alignment.center,
            content=ft.Text("Defina as medidas para visualizar", color=ft.Colors.GREY_300)
        )
    )

    # --- Lógica de Cálculo e Desenho ---
    def calcular_e_desenhar(e):
        if not dd_pedra.value or not txt_largura.value or not txt_altura.value:
            return

        try:
            largura_cm = float(txt_largura.value)
            altura_cm = float(txt_altura.value)
            preco_acabamento_linear = float(txt_custo_acabamento.value)
            preco_m2_pedra = mapa_precos.get(dd_pedra.value, 0)
        except ValueError:
            return 

        # Cálculos
        area_m2 = (largura_cm * altura_cm) / 10000 
        perimetro_linear = (largura_cm * 2) + (altura_cm * 2) 
        perimetro_m = perimetro_linear / 100 
        
        custo_pedra = area_m2 * preco_m2_pedra
        custo_mao_obra = perimetro_m * preco_acabamento_linear
        total = custo_pedra + custo_mao_obra

        # Atualiza Textos
        lbl_total_pedra.value = f"Pedra ({area_m2:.2f} m²): R$ {custo_pedra:.2f}"
        lbl_total_mao_obra.value = f"Acabamento ({perimetro_m:.2f} m): R$ {custo_mao_obra:.2f}"
        lbl_total_geral.value = f"R$ {total:.2f}"
        
        desenhar_peca(largura_cm, altura_cm)
        page.update()

    def desenhar_peca(largura_real, altura_real):
        canvas_desenho.shapes.clear()
        
        W_CANVAS = 400
        H_CANVAS = 300
        PADDING = 50

        if largura_real == 0 or altura_real == 0: return

        fator_escala = min((W_CANVAS - PADDING*2) / largura_real, (H_CANVAS - PADDING*2) / altura_real)
        
        w = largura_real * fator_escala
        h = altura_real * fator_escala
        espessura = 20 

        start_x = (W_CANVAS - w) / 2
        start_y = (H_CANVAS - h) / 2

        cor_pedra = ft.Colors.BLUE_GREY_200
        cor_borda = ft.Colors.BLUE_GREY_700
        cor_lateral = ft.Colors.BLUE_GREY_400 

        # --- CORREÇÃO DEFINITIVA ---
        # Usamos cv.Path.MoveTo (classe dentro de Path dentro de canvas)
        pontos_lateral = [
            cv.Path.MoveTo(start_x + w, start_y),             
            cv.Path.LineTo(start_x + w + espessura, start_y - espessura), 
            cv.Path.LineTo(start_x + w + espessura, start_y + h - espessura), 
            cv.Path.LineTo(start_x + w, start_y + h),         
            cv.Path.Close()
        ]
        
        pontos_topo = [
            cv.Path.MoveTo(start_x, start_y),                 
            cv.Path.LineTo(start_x + espessura, start_y - espessura), 
            cv.Path.LineTo(start_x + w + espessura, start_y - espessura), 
            cv.Path.LineTo(start_x + w, start_y),             
            cv.Path.Close()
        ]

        # Adiciona formas ao Canvas
        canvas_desenho.shapes.append(cv.Path(pontos_topo, paint=ft.Paint(style=ft.PaintingStyle.FILL, color=cor_lateral)))
        canvas_desenho.shapes.append(cv.Path(pontos_lateral, paint=ft.Paint(style=ft.PaintingStyle.FILL, color=cor_lateral)))
        
        canvas_desenho.shapes.append(cv.Path(pontos_topo, paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=cor_borda, stroke_width=2)))
        canvas_desenho.shapes.append(cv.Path(pontos_lateral, paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=cor_borda, stroke_width=2)))

        # Face Frontal
        canvas_desenho.shapes.append(
            cv.Rect(start_x, start_y, w, h, paint=ft.Paint(color=cor_pedra, style=ft.PaintingStyle.FILL))
        )
        canvas_desenho.shapes.append(
            cv.Rect(start_x, start_y, w, h, paint=ft.Paint(color=cor_borda, style=ft.PaintingStyle.STROKE, stroke_width=2))
        )

        # Cotas
        canvas_desenho.shapes.append(
            cv.Text(start_x + (w/2) - 20, start_y + h + 10, f"{largura_real:.0f} cm", style=ft.TextStyle(color=ft.Colors.BLACK, size=14, weight=ft.FontWeight.BOLD))
        )
        canvas_desenho.shapes.append(
            cv.Text(start_x - 50, start_y + (h/2), f"{altura_real:.0f} cm", style=ft.TextStyle(color=ft.Colors.BLACK, size=14, weight=ft.FontWeight.BOLD))
        )

        canvas_desenho.update()

    dd_pedra.on_change = calcular_e_desenhar
    txt_largura.on_change = calcular_e_desenhar
    txt_altura.on_change = calcular_e_desenhar
    txt_custo_acabamento.on_change = calcular_e_desenhar

    conteudo = ft.Container(
        expand=True,
        padding=30,
        bgcolor=COLOR_BACKGROUND,
        content=ft.Column([
            ft.Text("Novo Orçamento", size=28, weight="bold", color=COLOR_PRIMARY),
            ft.Divider(),
            
            ft.Row([
                ft.Container(
                    width=400,
                    content=ft.Column([
                        ft.Text("1. Material e Medidas", weight="bold"),
                        dd_pedra,
                        ft.Row([txt_largura, txt_altura]),
                        ft.Divider(),
                        ft.Text("2. Mão de Obra e Acabamento", weight="bold"),
                        txt_custo_acabamento,
                        ft.Text("O acabamento é calculado pelo perímetro linear da peça.", size=12, italic=True, color=ft.Colors.GREY_500),
                        ft.Divider(),
                        ft.Text("Resumo do Custo:", weight="bold", size=18),
                        lbl_total_pedra,
                        lbl_total_mao_obra,
                        ft.Divider(),
                        ft.Text("TOTAL DO ORÇAMENTO:", size=14, weight="bold", color=COLOR_SECONDARY),
                        lbl_total_geral,
                        ft.ElevatedButton(
                            "Gerar PDF e Salvar", 
                            icon=ft.Icons.PICTURE_AS_PDF, 
                            style=ft.ButtonStyle(bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, shape=ft.RoundedRectangleBorder(radius=10)),
                            height=50,
                            width=400,
                            on_click=lambda e: print("Salvar clicado") 
                        )
                    ], spacing=15)
                ),
                ft.Container(
                    expand=True,
                    padding=20,
                    content=ft.Column([
                        ft.Text("Visualização Técnica", weight="bold"),
                        ft.Container(
                            content=canvas_desenho,
                            alignment=ft.alignment.center,
                            bgcolor=ft.Colors.GREY_50,
                            border_radius=15,
                            padding=20,
                            shadow=ft.BoxShadow(blur_radius=10, color="#00000010")
                        ),
                        ft.Text("* Visualização ilustrativa (Sem escala real)", size=12, color=ft.Colors.GREY)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                )
            ], vertical_alignment=ft.CrossAxisAlignment.START, scroll=ft.ScrollMode.AUTO)
        ])
    )

    return ft.View(
        route="/orcamentos",
        padding=0,
        controls=[
            ft.Row([Sidebar(page), conteudo], expand=True)
        ]
    )