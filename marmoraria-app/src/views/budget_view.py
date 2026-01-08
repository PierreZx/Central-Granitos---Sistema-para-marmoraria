import flet as ft
from src.views.layout_base import LayoutBase
from src.views.components.budget_calculator import BudgetCalculator
from src.config import (
    COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, COLOR_SECONDARY, 
    COLOR_TEXT, COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING, 
    SHADOW_MD, BORDER_RADIUS_LG, BORDER_RADIUS_MD
)
from src.services import firebase_service
from src.services.pdf_service import gerar_pdf_orcamento
import datetime

def BudgetView(page: ft.Page):
    # Estado para controlar se vemos a lista ou o editor
    estado = {"orcamento_atual": None, "id_atual": None}
    conteudo_principal = ft.Container(expand=True)

    def render_lista_principal(e=None):
        """Renderiza a grade de orçamentos (Cards)"""
        lista_orcamentos = firebase_service.get_orcamentos_lista()
        
        grid = ft.ResponsiveRow(spacing=20, run_spacing=20)
        
        # Botão Novo Orçamento (Primeiro Card)
        grid.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.ADD_CIRCLE_OUTLINE, size=40, color=COLOR_PRIMARY),
                    ft.Text("Novo Orçamento", weight="bold", color=COLOR_PRIMARY)
                ], alignment="center", horizontal_alignment="center"),
                bgcolor=COLOR_WHITE,
                padding=30,
                border_radius=BORDER_RADIUS_LG,
                border=ft.border.all(2, COLOR_PRIMARY),
                on_click=lambda _: abrir_editor_novo(),
                col={"xs": 12, "sm": 6, "md": 4, "lg": 3}
            )
        )

        for orc in lista_orcamentos:
            grid.controls.append(criar_card_orcamento(orc))

        conteudo_principal.content = ft.Column([
            ft.Text("Orçamentos e Projetos", size=28, weight="bold", color=COLOR_TEXT),
            grid
        ], scroll=ft.ScrollMode.AUTO)
        page.update()

    def criar_card_orcamento(orc):
        status = orc.get('status', 'Pendente')
        cor_status = COLOR_SUCCESS if status == "Finalizado" else COLOR_WARNING
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"#{orc['id'][-5:]}", size=12, color="grey"),
                    ft.Container(
                        content=ft.Text(status, size=10, color=COLOR_WHITE, weight="bold"),
                        bgcolor=cor_status, padding=ft.padding.symmetric(6, 12), border_radius=15
                    )
                ], alignment="spaceBetween"),
                ft.Text(orc.get('cliente_nome', 'Cliente sem nome'), weight="bold", size=18, max_lines=1),
                ft.Text(f"R$ {float(orc.get('total_geral', 0)):,.2f}", size=20, weight="bold", color=COLOR_PRIMARY),
                ft.Divider(height=10, color="transparent"),
                ft.Row([
                    ft.IconButton(ft.icons.EDIT_OUT_LINED, on_click=lambda _: editar_orcamento(orc)),
                    ft.IconButton(ft.icons.PICTURE_AS_PDF, on_click=lambda _: gerar_pdf_orcamento(orc)),
                    ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color=COLOR_ERROR, on_click=lambda _: deletar_orcamento(orc))
                ], alignment="end")
            ]),
            bgcolor=COLOR_WHITE, padding=20, border_radius=BORDER_RADIUS_LG, shadow=SHADOW_MD,
            col={"xs": 12, "sm": 6, "md": 4, "lg": 3}
        )

    def abrir_editor_novo():
        estado['id_atual'] = None
        estado['orcamento_atual'] = {
            "cliente_nome": "", "cliente_telefone": "", "itens": [], 
            "total_geral": 0.0, "status": "Pendente", "data": datetime.datetime.now().isoformat()
        }
        render_tela_editor()

    def editar_orcamento(orc):
        estado['id_atual'] = orc['id']
        estado['orcamento_atual'] = orc
        render_tela_editor()

    def render_tela_editor():
        """Abre a calculadora e campos de cliente"""
        orc = estado['orcamento_atual']
        
        txt_nome = ft.TextField(label="Nome do Cliente", value=orc['cliente_nome'], border_radius=10)
        
        def salvar_tudo(e):
            orc['cliente_nome'] = txt_nome.value
            if estado['id_atual']:
                firebase_service.update_document("orcamentos", estado['id_atual'], orc)
            else:
                firebase_service.add_document("orcamentos", orc)
            render_lista_principal()

        conteudo_principal.content = ft.Column([
            ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, on_click=render_lista_principal),
                ft.Text("Editar Orçamento", size=20, weight="bold")
            ]),
            txt_nome,
            ft.Text("Itens do Orçamento", weight="bold"),
            # Aqui entraria a BudgetCalculator (Componente)
            ft.ElevatedButton("Adicionar Item / Calcular", icon=ft.icons.CALCULATOR, on_click=lambda _: ir_para_calculadora()),
            ft.ElevatedButton("Salvar Orçamento", bgcolor=COLOR_SUCCESS, color=COLOR_WHITE, on_click=salvar_tudo)
        ], scroll=ft.ScrollMode.AUTO)
        page.update()

    def ir_para_calculadora():
        def ao_salvar(novo_item):
            estado['orcamento_atual']['itens'].append(novo_item)
            # Recalcula total
            total = sum(float(i.get('subtotal', 0)) for i in estado['orcamento_atual']['itens'])
            estado['orcamento_atual']['total_geral'] = total
            render_tela_editor()
            
        calc = BudgetCalculator(page, on_save_item=ao_salvar, on_cancel=render_tela_editor)
        conteudo_principal.content = calc
        page.update()

    def deletar_orcamento(orc):
        firebase_service.delete_document("orcamentos", orc['id'])
        render_lista_principal()

    render_lista_principal()
    return LayoutBase(page, conteudo_principal, titulo="Orçamentos")