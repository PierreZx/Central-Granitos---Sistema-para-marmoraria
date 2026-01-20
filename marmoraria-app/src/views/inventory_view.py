# src/views/inventory_view.py
import flet as ft
from src.views.layout_base import LayoutBase
from src.config import (
    COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, COLOR_SECONDARY,
    COLOR_TEXT, COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING,
    SHADOW_MD, BORDER_RADIUS_LG, BORDER_RADIUS_MD
)
from src.services import firebase_service

def InventoryView(page: ft.Page):
    # Container responsivo para os cards de pedras
    grid_produtos = ft.ResponsiveRow(spacing=20, run_spacing=20)
    
    # Campo de busca para facilitar no mobile
    txt_busca = ft.TextField(
        label="Buscar material...",
        prefix_icon=ft.icons.SEARCH,
        border_radius=15,
        bgcolor=COLOR_WHITE,
        on_change=lambda _: carregar_dados()
    )

    # --- CAMPOS DO FORMULÁRIO (REUTILIZADOS NOS MODAIS) ---
    txt_nome = ft.TextField(label="Nome da Pedra", filled=True, border_radius=BORDER_RADIUS_MD, autocapitalize=ft.TextCapitalization.CHARACTERS)
    txt_preco = ft.TextField(
        label="Preço por m²",
        prefix_text="R$ ",
        keyboard_type=ft.KeyboardType.NUMBER,
        filled=True,
        border_radius=BORDER_RADIUS_MD
    )
    txt_metros = ft.TextField(
        label="Medida (m²)",
        suffix_text="m²",
        keyboard_type=ft.KeyboardType.NUMBER,
        filled=True,
        border_radius=BORDER_RADIUS_MD,
        expand=True
    )
    txt_qtd = ft.TextField(
        label="Qtd Chapas",
        suffix_text="un",
        keyboard_type=ft.KeyboardType.NUMBER,
        filled=True,
        border_radius=BORDER_RADIUS_MD,
        expand=True
    )

    def fechar_dialogo(e=None):
        page.dialog.open = False
        page.update()

    def carregar_dados():
        grid_produtos.controls.clear()
        # Busca da lógica híbrida (SQLite + Firebase)
        lista = firebase_service.get_collection("estoque")
        
        termo = txt_busca.value.lower() if txt_busca.value else ""
        
        # Filtro em tempo real no banco local
        lista_filtrada = [i for i in lista if termo in i.get("nome", "").lower()]

        if not lista_filtrada:
            grid_produtos.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.INVENTORY_2_OUTLINED, size=50, color="grey400"),
                        ft.Text("Nenhum material encontrado.", color="grey400")
                    ], horizontal_alignment="center"),
                    padding=50, col=12, alignment=ft.alignment.center
                )
            )
        else:
            for item in lista_filtrada:
                grid_produtos.controls.append(criar_card_estoque(item))
        page.update()

    def criar_card_estoque(item):
        """Cria o card visual de cada pedra para o ambiente Android."""
        return ft.Container(
            col={"xs": 12, "sm": 6, "md": 4, "lg": 3},
            padding=20,
            bgcolor=COLOR_WHITE,
            border_radius=BORDER_RADIUS_MD,
            shadow=SHADOW_MD,
            content=ft.Column([
                ft.Row([
                    ft.Text(item.get("nome", "SEM NOME").upper(), weight="bold", size=16, expand=True),
                    ft.Container(
                        bgcolor=f"{COLOR_PRIMARY}10",
                        padding=5, border_radius=5,
                        content=ft.Text(f"ID: {item.get('id','')[-4:]}", size=9, color=COLOR_PRIMARY)
                    )
                ]),
                ft.Divider(height=10, color="transparent"),
                ft.Row([
                    ft.Icon(ft.icons.MONETIZATION_ON_OUTLINED, size=16, color=COLOR_SUCCESS),
                    ft.Text(f"R$ {float(item.get('preco_m2', 0)):,.2f} / m²", size=14, weight="w500"),
                ]),
                ft.Row([
                    ft.Icon(ft.icons.SQUARE_FOOT_OUTLINED, size=16, color="grey600"),
                    ft.Text(f"{item.get('metros', 0)} m² disponíveis", size=13),
                ]),
                ft.Row([
                    ft.Icon(ft.icons.LAYERS_OUTLINED, size=16, color="grey600"),
                    ft.Text(f"{item.get('quantidade', 0)} unidades (chapas)", size=13),
                ]),
                ft.Divider(height=10),
                ft.Row([
                    ft.IconButton(ft.icons.EDIT_OUTLINED, icon_color=COLOR_PRIMARY, on_click=lambda _: abrir_popup_editar(item)),
                    ft.IconButton(ft.icons.DELETE_OUTLINE_ROUNDED, icon_color=COLOR_ERROR, on_click=lambda _: confirmar_exclusao(item))
                ], alignment="end")
            ])
        )

    # --- LÓGICA DE PERSISTÊNCIA ---

    def salvar_produto(e):
        try:
            if not txt_nome.value or not txt_preco.value: return
            
            dados = {
                "nome": txt_nome.value.upper(),
                "preco_m2": float(txt_preco.value.replace(",", ".")),
                "metros": float(txt_metros.value.replace(",", ".")),
                "quantidade": int(txt_qtd.value or 0)
            }
            # Adiciona usando o serviço sincronizado
            if firebase_service.add_document("estoque", dados):
                fechar_dialogo()
                carregar_dados()
        except Exception as ex:
            print(f"Erro ao salvar: {ex}")

    def abrir_popup_novo(e):
        txt_nome.value = ""; txt_preco.value = ""; txt_metros.value = ""; txt_qtd.value = ""
        page.dialog = ft.AlertDialog(
            title=ft.Text("Cadastrar Nova Pedra"),
            content=ft.Column([txt_nome, txt_preco, ft.Row([txt_metros, txt_qtd], spacing=10)], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.ElevatedButton("Salvar no Estoque", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=salvar_produto)
            ]
        )
        page.dialog.open = True
        page.update()

    def abrir_popup_editar(item):
        txt_nome.value = item.get("nome")
        txt_preco.value = str(item.get("preco_m2", 0))
        txt_metros.value = str(item.get("metros", 0))
        txt_qtd.value = str(item.get("quantidade", 0))

        def salvar_edicao(e):
            try:
                dados = {
                    "nome": txt_nome.value.upper(),
                    "preco_m2": float(txt_preco.value.replace(",", ".")),
                    "metros": float(txt_metros.value.replace(",", ".")),
                    "quantidade": int(txt_qtd.value)
                }
                if firebase_service.update_document("estoque", item["id"], dados):
                    fechar_dialogo()
                    carregar_dados()
            except: pass

        page.dialog = ft.AlertDialog(
            title=ft.Text("Editar Material"),
            content=ft.Column([txt_nome, txt_preco, ft.Row([txt_metros, txt_qtd], spacing=10)], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.ElevatedButton("Atualizar", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=salvar_edicao)
            ]
        )
        page.dialog.open = True
        page.update()

    def confirmar_exclusao(item):
        def deletar(e):
            firebase_service.delete_document("estoque", item["id"])
            fechar_dialogo()
            carregar_dados()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Exclusão"),
            content=ft.Text(f"Tem certeza que deseja remover {item.get('nome')} do estoque?"),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.ElevatedButton("Sim, Excluir", bgcolor=COLOR_ERROR, color=COLOR_WHITE, on_click=deletar)
            ]
        )
        page.dialog.open = True
        page.update()

    # --- LAYOUT FINAL ---
    header = ft.Row([
        ft.Column([
            ft.Text("Estoque de Pedras", size=28, weight="bold", color=COLOR_TEXT),
            ft.Text("Gerencie suas chapas e materiais disponíveis", size=14, color="grey600"),
        ]),
        ft.FloatingActionButton(
            icon=ft.icons.ADD,
            bgcolor=COLOR_PRIMARY,
            content=ft.Text("Novo", color=COLOR_WHITE, weight="bold"),
            on_click=abrir_popup_novo,
            width=120
        )
    ], alignment="spaceBetween")

    carregar_dados()

    return LayoutBase(
        page,
        ft.Column([
            header,
            ft.Divider(height=20, color="transparent"),
            txt_busca,
            ft.Divider(height=10, color="transparent"),
            grid_produtos
        ], expand=True, scroll=ft.ScrollMode.AUTO),
        titulo="Estoque Central"
    )