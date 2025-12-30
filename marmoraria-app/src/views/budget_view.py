import flet as ft
import flet.canvas as cv
import flet.canvas as cv
from src.views.components.sidebar import Sidebar
from src.config import COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, COLOR_SECONDARY
from src.services import firebase_service

def BudgetView(page: ft.Page):
    
    # --- Estado e Variáveis ---
    chapas_disponiveis = firebase_service.get_estoque_lista()
    opcoes_pedras = []
    mapa_precos = {} 
    
    for chapa in chapas_disponiveis:
        qtd = int(chapa.get('quantidade', 0) or 0)
        if qtd > 0:
            nome = chapa.get('nome', 'Sem Nome')
            valor_str = chapa.get('valor_m2', 0) or 0
            preco = float(valor_str)
            texto_opcao = f"{nome} - R$ {preco:.2f}/m²"
            opcoes_pedras.append(ft.dropdown.Option(key=chapa['id'], text=texto_opcao))
            mapa_precos[chapa['id']] = preco

    # --- Componentes de Entrada ---
    dd_pedra = ft.Dropdown(label="Selecione a Pedra", options=opcoes_pedras, width=400, border_radius=10)
    
    # TUDO EM METROS AGORA
    txt_largura = ft.TextField(label="Largura (m)", suffix_text="m", width=190, keyboard_type=ft.KeyboardType.NUMBER, border_radius=10)
    txt_profundidade = ft.TextField(label="Profundidade (m)", suffix_text="m", width=190, keyboard_type=ft.KeyboardType.NUMBER, border_radius=10)
    
    txt_rodabanca = ft.TextField(label="Alt. Rodabanca (m)", value="0", suffix_text="m", width=190, keyboard_type=ft.KeyboardType.NUMBER, border_radius=10)
    txt_saia = ft.TextField(label="Alt. Saia/Borda (m)", value="0", suffix_text="m", width=190, keyboard_type=ft.KeyboardType.NUMBER, border_radius=10)
    
    txt_custo_acabamento = ft.TextField(label="Preço Acabamento (R$/m linear)", value="50.00", prefix_text="R$ ", width=400, keyboard_type=ft.KeyboardType.NUMBER, border_radius=10)

    chk_cuba = ft.Checkbox(label="Incluir Recorte de Cuba/Pia", value=False)
    chk_cooktop = ft.Checkbox(label="Incluir Recorte de Cooktop", value=False)

    # --- Resultados ---
    lbl_area_total = ft.Text("0.00 m²", weight="bold")
    lbl_total_pedra = ft.Text("R$ 0.00", size=16, color=ft.colors.GREY_700)
    lbl_total_mao_obra = ft.Text("R$ 0.00", size=16, color=ft.colors.GREY_700)
    lbl_total_geral = ft.Text("R$ 0.00", size=30, weight="bold", color=COLOR_PRIMARY)

    # --- ÁREA DE DESENHO ---
    canvas_container = ft.Container(
        bgcolor=ft.colors.BLUE_GREY_50,
        border_radius=15,
        border=ft.border.all(1, ft.colors.GREY_300),
        alignment=ft.alignment.center,
        expand=True,
        padding=20
    )

    canvas_desenho = cv.Canvas(
        width=400,
        height=400,
        shapes=[cv.Text(200, 200, "Defina as medidas...", alignment=ft.alignment.center, style=ft.TextStyle(color=ft.colors.GREY_400, size=14))], 
    )
    canvas_container.content = canvas_desenho

    # --- Lógica de Cálculo ---
    def calcular_e_desenhar(e):
        if not dd_pedra.value or not txt_largura.value or not txt_profundidade.value:
            return

        try:
            # Inputs em METROS
            larg_m = float(txt_largura.value)
            prof_m = float(txt_profundidade.value)
            
            # Inputs em METROS também
            alt_rodabanca_m = float(txt_rodabanca.value) if txt_rodabanca.value else 0
            alt_saia_m = float(txt_saia.value) if txt_saia.value else 0
            
            preco_acab_linear = float(txt_custo_acabamento.value or 0)
            preco_m2_pedra = mapa_precos.get(dd_pedra.value, 0)
        except ValueError:
            return 

        # --- Matemática (Tudo em Metros = Fácil) ---
        
        # 1. Área Plana
        area_tampo = larg_m * prof_m
        
        # 2. Área Rodabanca (Metro x Metro)
        area_rodabanca = larg_m * alt_rodabanca_m
        
        # 3. Área Saia (Metro x Metro)
        area_saia = larg_m * alt_saia_m

        area_total = area_tampo + area_rodabanca + area_saia
        
        # Custos
        custo_pedra = area_total * preco_m2_pedra
        
        # Mão de obra (Perímetro linear em metros)
        custo_mao_obra = larg_m * preco_acab_linear
        
        custo_recortes = 0
        if chk_cuba.value: custo_recortes += 150.00
        if chk_cooktop.value: custo_recortes += 100.00
        
        custo_mao_obra += custo_recortes
        total = custo_pedra + custo_mao_obra

        # Atualiza UI
        lbl_area_total.value = f"{area_total:.2f} m² (Total)"
        lbl_total_pedra.value = f"Pedra: R$ {custo_pedra:.2f}"
        lbl_total_mao_obra.value = f"Acab./Recortes: R$ {custo_mao_obra:.2f}"
        lbl_total_geral.value = f"R$ {total:.2f}"
        
        # Para desenhar, multiplicamos por 100 para converter M -> CM apenas para o motor de desenho (escala)
        desenhar_planta_baixa(
            larg_m * 100, 
            prof_m * 100, 
            alt_rodabanca_m * 100, 
            alt_saia_m * 100, 
            chk_cuba.value, 
            chk_cooktop.value
        )
        page.update()

    def desenhar_planta_baixa(larg_cm, prof_cm, rodabanca_cm, saia_cm, tem_cuba, tem_cooktop):
        canvas_desenho.shapes.clear()
        
        W_CANVAS, H_CANVAS = 400, 400
        MARGIN = 40

        if larg_cm <= 0 or prof_cm <= 0: return

        # Escala
        scale = min((W_CANVAS - MARGIN*2) / larg_cm, (H_CANVAS - MARGIN*2) / (prof_cm + rodabanca_cm)) * 0.85
        
        w_px = larg_cm * scale
        h_px = prof_cm * scale
        h_rodabanca_px = rodabanca_cm * scale
        
        start_x = (W_CANVAS - w_px) / 2
        start_y = (H_CANVAS - h_px) / 2 + (h_rodabanca_px / 2)

        # Cores
        cor_pedra = ft.colors.BLUE_GREY_100
        cor_linha = ft.colors.BLACK
        
        # 1. Rodabanca
        if rodabanca_cm > 0:
            canvas_desenho.shapes.append(cv.Rect(start_x, start_y - h_rodabanca_px, w_px, h_rodabanca_px, paint=ft.Paint(style=ft.PaintingStyle.FILL, color=ft.colors.BLUE_GREY_200)))
            canvas_desenho.shapes.append(cv.Rect(start_x, start_y - h_rodabanca_px, w_px, h_rodabanca_px, paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=cor_linha, stroke_width=1)))
            # Texto Rodabanca em Metros
            canvas_desenho.shapes.append(cv.Text(start_x + w_px + 5, start_y - h_rodabanca_px/2 - 5, f"R: {rodabanca_cm/100:.2f}m", style=ft.TextStyle(size=10, color=ft.colors.GREY_600)))

        # 2. Tampo
        canvas_desenho.shapes.append(cv.Rect(start_x, start_y, w_px, h_px, paint=ft.Paint(style=ft.PaintingStyle.FILL, color=cor_pedra)))
        
        # 3. Recortes
        if tem_cuba and not tem_cooktop:
            cw, ch = w_px * 0.4, h_px * 0.6
            desenhar_cuba(canvas_desenho, start_x + (w_px - cw)/2, start_y + (h_px - ch)/2, cw, ch)
        elif tem_cooktop and not tem_cuba:
            cw, ch = w_px * 0.4, h_px * 0.6
            desenhar_cooktop(canvas_desenho, start_x + (w_px - cw)/2, start_y + (h_px - ch)/2, cw, ch)
        elif tem_cuba and tem_cooktop:
            cw, ch = w_px * 0.3, h_px * 0.6
            desenhar_cuba(canvas_desenho, start_x + (w_px * 0.15), start_y + (h_px - ch)/2, cw, ch)
            desenhar_cooktop(canvas_desenho, start_x + (w_px * 0.55), start_y + (h_px - ch)/2, cw, ch)

        # 4. Borda
        canvas_desenho.shapes.append(cv.Rect(start_x, start_y, w_px, h_px, paint=ft.Paint(style=ft.PaintingStyle.STROKE, stroke_width=2, color=cor_linha)))

        # 5. Saia
        if saia_cm > 0:
            # Texto Saia em Metros
            canvas_desenho.shapes.append(cv.Text(start_x + w_px/2 - 20, start_y + h_px + 5, f"Saia: {saia_cm/100:.2f}m", style=ft.TextStyle(size=10, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900)))

        # Cotas Principais (Em Metros)
        larg_m_display = larg_cm / 100
        prof_m_display = prof_cm / 100
        canvas_desenho.shapes.append(cv.Text(start_x + w_px/2 - 15, start_y - 15, f"{larg_m_display:.2f} m", style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD)))
        canvas_desenho.shapes.append(cv.Text(start_x - 45, start_y + h_px/2, f"{prof_m_display:.2f} m", style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD)))

        canvas_desenho.update()

    def desenhar_cuba(cv_obj, x, y, w, h):
        cv_obj.shapes.append(cv.Rect(x, y, w, h, border_radius=10, paint=ft.Paint(style=ft.PaintingStyle.FILL, color=ft.colors.WHITE)))
        cv_obj.shapes.append(cv.Rect(x, y, w, h, border_radius=10, paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=ft.colors.GREY_600)))
        cv_obj.shapes.append(cv.Circle(x + w/2, y - 5, 3, paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=ft.colors.BLACK)))

    def desenhar_cooktop(cv_obj, x, y, w, h):
        cv_obj.shapes.append(cv.Rect(x, y, w, h, paint=ft.Paint(style=ft.PaintingStyle.FILL, color=ft.colors.GREY_800)))
        r, offset = w * 0.15, w * 0.25
        for bx, by in [(x+offset, y+offset), (x+w-offset, y+offset), (x+offset, y+h-offset), (x+w-offset, y+h-offset)]:
            cv_obj.shapes.append(cv.Circle(bx, by, r, paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=ft.colors.GREY_400)))

    # Gatilhos
    dd_pedra.on_change = calcular_e_desenhar
    txt_largura.on_change = calcular_e_desenhar
    txt_profundidade.on_change = calcular_e_desenhar
    txt_rodabanca.on_change = calcular_e_desenhar
    txt_saia.on_change = calcular_e_desenhar
    txt_custo_acabamento.on_change = calcular_e_desenhar
    chk_cuba.on_change = calcular_e_desenhar
    chk_cooktop.on_change = calcular_e_desenhar

    conteudo = ft.Container(
        expand=True,
        padding=30,
        bgcolor=COLOR_BACKGROUND,
        content=ft.Column([
            ft.Text("Novo Orçamento", size=28, weight="bold", color=COLOR_PRIMARY),
            ft.Text("Novo Orçamento", size=28, weight="bold", color=COLOR_PRIMARY),
            ft.Divider(),
            ft.Row([
                ft.Container(
                    width=400,
                    content=ft.Column([
                        ft.Text("1. Dimensões Principais (Metros)", weight="bold"),
                        dd_pedra,
                        ft.Row([txt_largura, txt_profundidade]),
                        ft.Divider(),
                        ft.Text("2. Adicionais Verticais (Metros)", weight="bold"),
                        ft.Row([txt_rodabanca, txt_saia]),
                        txt_custo_acabamento,
                        ft.Divider(),
                        ft.Text("3. Recortes", weight="bold"),
                        ft.Row([chk_cuba, chk_cooktop]),
                        ft.Divider(),
                        ft.Text("Resumo Financeiro:", weight="bold", size=18),
                        lbl_area_total,
                        lbl_total_pedra,
                        lbl_total_mao_obra,
                        ft.Text("TOTAL FINAL:", size=14, weight="bold", color=COLOR_SECONDARY),
                        lbl_total_geral,
                        ft.ElevatedButton("Salvar Orçamento", icon=ft.icons.SAVE, style=ft.ButtonStyle(bgcolor=COLOR_PRIMARY, color=COLOR_WHITE), height=50, width=400, on_click=lambda e: print("Salvar"))
                    ], spacing=10, scroll=ft.ScrollMode.AUTO)
                ),
                ft.Container(
                    expand=True,
                    padding=20,
                    content=ft.Column([
                        ft.Text("Planta Baixa Esquemática", weight="bold"),
                        canvas_container,
                        ft.Text("Tudo em Metros | Visualização Ilustrativa", size=12, color=ft.colors.GREY_500)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                )
            ], vertical_alignment=ft.CrossAxisAlignment.START, expand=True)
        ])
    )

    return ft.View(route="/orcamentos", padding=0, controls=[ft.Row([Sidebar(page), conteudo], expand=True)])