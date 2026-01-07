import flet as ft
from src.views.components.sidebar import Sidebar
from src.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_BACKGROUND, COLOR_WHITE, COLOR_SUCCESS, COLOR_WARNING, COLOR_INFO, COLOR_TEXT
from src.services import firebase_service

def DashboardView(page: ft.Page):
    
    firebase_service.initialize_firebase()
    qtd_estoque = firebase_service.get_collection_count("estoque")
    qtd_orcamentos = firebase_service.get_collection_count("orcamentos")
    
    # Busca faturamento real
    faturamento = firebase_service.get_faturamento_mes_atual()
    
    def card_indicador(titulo, valor, icone, cor_icone, cor_valor=COLOR_TEXT):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        width=50,
                        height=50,
                        border_radius=12,
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_left,
                            end=ft.alignment.bottom_right,
                            colors=[f"{cor_icone}15", f"{cor_icone}05"]
                        ),
                        content=ft.Icon(icone, color=cor_icone, size=24),
                        alignment=ft.alignment.center
                    ),
                    ft.Column([
                        ft.Text(titulo, color=ft.colors.GREY_600, size=13), 
                        ft.Text(valor, size=20, weight="bold", color=cor_valor)
                    ], spacing=2, expand=True) 
                ]),
                ft.Container(height=15),
                ft.ProgressBar(value=0.7, height=4, color=cor_icone, bgcolor=f"{cor_icone}15")
            ]),
            bgcolor=COLOR_WHITE,
            padding=20,
            border_radius=20,
            expand=True, 
            shadow=ft.BoxShadow(blur_radius=25, spread_radius=-10, color="#00000008"),
            border=ft.border.all(1, "#00000005"),
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN_OUT)
        )

    # Gráfico
    chart_data = [ft.LineChartData(data_points=[ft.LineChartDataPoint(1, 2), ft.LineChartDataPoint(5, 5)], color=COLOR_SECONDARY, stroke_width=3, curved=True)]
    chart = ft.LineChart(data_series=chart_data, border=ft.border.all(1, "#00000010"), expand=True)

    # Tabela Recentes
    lista_orcamentos = firebase_service.get_orcamentos_lista()
    tabela = ft.DataTable(
        columns=[ft.DataColumn(ft.Text("Cliente")), ft.DataColumn(ft.Text("Valor")), ft.DataColumn(ft.Text("Status"))],
        rows=[]
    )
    for orc in lista_orcamentos[-5:]:
        status = orc.get('status', 'Pendente')
        tabela.rows.append(ft.DataRow(cells=[
            ft.DataCell(ft.Text(orc.get('cliente_nome', '-'))),
            ft.DataCell(ft.Text(f"R$ {orc.get('total_geral', 0):.2f}")),
            ft.DataCell(ft.Container(content=ft.Text(status, color="white", size=10), bgcolor=COLOR_PRIMARY if status=='Produção' else "grey", padding=5, border_radius=5))
        ]))

    conteudo = ft.Container(
        expand=True,
        padding=20, 
        bgcolor=COLOR_BACKGROUND,
        content=ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("Visão Geral", size=32, weight="bold", color=COLOR_TEXT),
                    ft.Text("Resumo das atividades", color=ft.colors.GREY_600, size=15),
                ], expand=True),
                ft.IconButton(icon=ft.icons.REFRESH, on_click=lambda e: page.go("/dashboard")) 
            ], alignment="spaceBetween"),
            
            ft.Divider(height=30, color="transparent"),
            
            # Cards Responsivos
            ft.ResponsiveRow([
                ft.Container(card_indicador("Faturamento", f"R$ {faturamento:,.2f}", ft.icons.TRENDING_UP, COLOR_SUCCESS, COLOR_SUCCESS), col={"xs": 12, "sm": 6, "md": 4}),
                ft.Container(card_indicador("Orçamentos", str(qtd_orcamentos), ft.icons.DESCRIPTION, COLOR_PRIMARY), col={"xs": 12, "sm": 6, "md": 4}),
                ft.Container(card_indicador("Estoque", f"{qtd_estoque} un", ft.icons.INVENTORY_2, COLOR_WARNING), col={"xs": 12, "sm": 12, "md": 4}),
            ], spacing=15, run_spacing=15),
            
            ft.Divider(height=30, color="transparent"),
            
            ft.Text("Últimos Orçamentos", weight="bold", size=20, color=COLOR_TEXT),
            
            # --- CORREÇÃO AQUI: Scroll na Row, não no Container ---
            ft.Container(
                content=ft.Row([tabela], scroll=ft.ScrollMode.AUTO), 
                bgcolor=COLOR_WHITE, 
                border_radius=15, 
                padding=10,
                shadow=ft.BoxShadow(blur_radius=10, color="#00000005"),
            ),
            
            ft.Divider(height=20, color="transparent"),
            
            ft.Text("Ações Rápidas", weight="bold", size=20, color=COLOR_TEXT),
            ft.ResponsiveRow([
                ft.Container(
                    col={"xs": 6, "md": 3},
                    content=ft.ElevatedButton(
                        "Novo Orçamento", icon=ft.icons.ADD, 
                        bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, 
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), padding=15),
                        on_click=lambda e: page.go("/orcamentos")
                    )
                ),
                ft.Container(
                    col={"xs": 6, "md": 3},
                    content=ft.ElevatedButton(
                        "Ver Estoque", icon=ft.icons.INVENTORY_2, 
                        bgcolor=COLOR_SECONDARY, color=COLOR_WHITE,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), padding=15),
                        on_click=lambda e: page.go("/estoque")
                    )
                ),
            ], spacing=10)
        ], scroll=ft.ScrollMode.AUTO)
    )

    from src.views.layout_base import LayoutBase
    return LayoutBase(page, conteudo, "Dashboard")