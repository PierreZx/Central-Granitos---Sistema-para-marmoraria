import flet as ft
from src.config import (
    COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, COLOR_SECONDARY, 
    COLOR_TEXT, COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING, 
    SHADOW_MD, BORDER_RADIUS_LG, BORDER_RADIUS_MD
)
from src.services import firebase_service
import datetime

def BudgetView(page: ft.Page):
    # --- VARIÁVEIS DE ESTADO ---
    itens_orcamento = [] # Lista de dicionários {'descricao': str, 'valor': float}

    # --- COMPONENTES DE INTERFACE ---
    container_conteudo = ft.Column(spacing=20, scroll=ft.ScrollMode.AUTO, expand=True)
    lista_itens_ui = ft.Column(spacing=10)
    
    txt_cliente = ft.TextField(label="Nome do Cliente", border_radius=BORDER_RADIUS_MD, filled=True)
    txt_contato = ft.TextField(label="Contato (WhatsApp)", border_radius=BORDER_RADIUS_MD, filled=True)
    txt_endereco = ft.TextField(label="Endereço da Obra", border_radius=BORDER_RADIUS_MD, filled=True)
    
    lbl_total = ft.Text("Total: R$ 0,00", size=24, weight="bold", color=COLOR_PRIMARY)

    # --- FUNÇÕES DE LÓGICA ---
    
    def atualizar_total():
        total = sum(item['valor'] for item in itens_orcamento)
        lbl_total.value = f"Total: R$ {total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        page.update()

    def remover_item(item_dict, controle_ui):
        itens_orcamento.remove(item_dict)
        lista_itens_ui.controls.remove(controle_ui)
        atualizar_total()

    def adicionar_peca_na_lista(nome, valor):
        item_dict = {"descricao": nome, "valor": float(valor)}
        itens_orcamento.append(item_dict)
        
        # Cria a linha visual do item
        nova_linha = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.CHEVRON_RIGHT, color=COLOR_SECONDARY),
                ft.Text(nome, weight="w500", expand=True),
                ft.Text(f"R$ {float(valor):,.2f}", weight="bold"),
                ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color=COLOR_ERROR, on_click=lambda e: remover_item(item_dict, nova_linha))
            ]),
            bgcolor=ft.colors.GREY_50,
            padding=10,
            border_radius=BORDER_RADIUS_MD
        )
        
        lista_itens_ui.controls.append(nova_linha)
        atualizar_total()

    def abrir_dialogo_item(e):
        txt_peca_nome = ft.TextField(label="Nome/Descrição da Peça")
        txt_peca_valor = ft.TextField(label="Valor (R$)", keyboard_type=ft.KeyboardType.NUMBER)

        def confirmar(e):
            if txt_peca_nome.value and txt_peca_valor.value:
                adicionar_peca_na_lista(txt_peca_nome.value, txt_peca_valor.value.replace(',', '.'))
                page.dialog.open = False
                page.update()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Adicionar Peça/Serviço"),
            content=ft.Column([txt_peca_nome, txt_peca_valor], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: setattr(page.dialog, "open", False) or page.update()),
                ft.ElevatedButton("Adicionar", on_click=confirmar, bgcolor=COLOR_PRIMARY, color=COLOR_WHITE)
            ]
        )
        page.dialog.open = True
        page.update()

    def salvar_orcamento(e):
        if not txt_cliente.value or not itens_orcamento:
            page.snack_bar = ft.SnackBar(ft.Text("Preencha o cliente e adicione pelo menos um item!"))
            page.snack_bar.open = True
            page.update()
            return

        dados = {
            "cliente": txt_cliente.value,
            "contato": txt_contato.value,
            "endereco": txt_endereco.value,
            "itens": itens_orcamento,
            "total": sum(item['valor'] for item in itens_orcamento),
            "data": datetime.datetime.now().isoformat(),
            "status": "PENDENTE"
        }

        if firebase_service.add_document("orcamentos", dados):
            page.snack_bar = ft.SnackBar(ft.Text("Orçamento salvo com sucesso!", color=COLOR_WHITE), bgcolor=COLOR_SUCCESS)
            limpar_campos()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Erro ao salvar no servidor."), bgcolor=COLOR_ERROR)
        
        page.snack_bar.open = True
        page.update()

    def limpar_campos():
        txt_cliente.value = ""
        txt_contato.value = ""
        txt_endereco.value = ""
        itens_orcamento.clear()
        lista_itens_ui.controls.clear()
        atualizar_total()

    # --- MONTAGEM DA VIEW ---
    header = ft.Row([
        ft.Column([
            ft.Text("Novo Orçamento", size=28, weight="bold", color=COLOR_PRIMARY),
            ft.Text("Preencha os dados abaixo", size=14, color="grey"),
        ], expand=True),
    ], alignment="spaceBetween")

    form_cliente = ft.Container(
        content=ft.Column([
            ft.Text("Informações do Cliente", weight="bold", size=18),
            txt_cliente,
            ft.Row([txt_contato, txt_endereco], spacing=10),
        ]),
        padding=20,
        bgcolor=COLOR_WHITE,
        border_radius=BORDER_RADIUS_MD,
        shadow=SHADOW_MD
    )

    area_itens = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("Peças e Serviços", weight="bold", size=18, expand=True),
                ft.ElevatedButton("Adicionar Peça", icon=ft.icons.ADD, on_click=abrir_dialogo_item)
            ]),
            ft.Divider(),
            lista_itens_ui,
            ft.Divider(),
            ft.Row([lbl_total], alignment="end")
        ]),
        padding=20,
        bgcolor=COLOR_WHITE,
        border_radius=BORDER_RADIUS_MD,
        shadow=SHADOW_MD
    )

    btn_finalizar = ft.ElevatedButton(
        "SALVAR ORÇAMENTO",
        icon=ft.icons.SAVE_ALT,
        bgcolor=COLOR_SUCCESS,
        color=COLOR_WHITE,
        height=60,
        expand=True,
        on_click=salvar_orcamento
    )

    container_conteudo.controls = [
        header,
        form_cliente,
        area_itens,
        ft.Row([btn_finalizar])
    ]

    from src.views.layout_base import LayoutBase
    return LayoutBase(page, container_conteudo, titulo="Orçamentos - Central Granitos")