import flet as ft
from src.views.layout_base import LayoutBase
from src.config import (
    COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, COLOR_SECONDARY, COLOR_TEXT, 
    COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING, SHADOW_MD, BORDER_RADIUS_LG, BORDER_RADIUS_MD
)
from src.services import firebase_service

def InventoryView(page: ft.Page):
    # --- ESTADOS E COMPONENTES ---
    grid_produtos = ft.ResponsiveRow(spacing=20, run_spacing=20)
    
    # Campos do formulário (reutilizáveis para Novo e Editar)
    txt_nome = ft.TextField(label="Nome da Pedra", border_radius=BORDER_RADIUS_MD, filled=True)
    txt_metros = ft.TextField(label="Medida (m²)", suffix_text="m²", keyboard_type=ft.KeyboardType.NUMBER, border_radius=BORDER_RADIUS_MD, filled=True, expand=True)
    txt_qtd = ft.TextField(label="Qtd.", suffix_text="un", keyboard_type=ft.KeyboardType.NUMBER, border_radius=BORDER_RADIUS_MD, filled=True, expand=True)

    # --- FUNÇÕES DE APOIO ---
    def fechar_dialogo(e=None):
        page.dialog.open = False
        page.update()

    def carregar_dados():
        grid_produtos.controls.clear()
        lista = firebase_service.get_collection("estoque")
        
        if not lista:
            grid_produtos.controls.append(
                ft.Container(
                    content=ft.Text("Nenhum item encontrado no estoque.", color="grey"),
                    padding=50, alignment=ft.alignment.center, col=12
                )
            )
        else:
            for item in lista:
                grid_produtos.controls.append(
                    ft.Container(
                        col={"xs": 12, "sm": 6, "md": 4, "xl": 3},
                        padding=20,
                        bgcolor=COLOR_WHITE,
                        border_radius=BORDER_RADIUS_MD,
                        shadow=SHADOW_MD,
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.icons.LAYERS, color=COLOR_PRIMARY),
                                ft.Text(item.get('nome', 'Sem nome'), weight="bold", size=16, expand=True),
                            ], alignment="spaceBetween"),
                            ft.Divider(height=10, color="transparent"),
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(f"{item.get('quantidade')} un", size=11, weight="bold", color=COLOR_WHITE),
                                    bgcolor=COLOR_SECONDARY,
                                    padding=ft.padding.symmetric(vertical=2, horizontal=8),
                                    border_radius=10,
                                ),
                                ft.Text(f"{item.get('metros')} m²", size=14, color=ft.colors.GREY_700),
                            ], alignment="spaceBetween"),
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.icons.EDIT,
                                    icon_color=ft.colors.BLUE_700,
                                    tooltip="Editar item",
                                    on_click=lambda e, i=item: abrir_popup_editar(i)
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE, 
                                    icon_color=COLOR_ERROR, 
                                    tooltip="Excluir item",
                                    on_click=lambda e, i=item: confirmar_exclusao(i['id'], i['nome'])
                                )
                            ], alignment="end", spacing=0)
                        ])
                    )
                )
        page.update()

    # --- FUNÇÕES DE AÇÃO (CRUD) ---
    def salvar_produto(e):
        if not txt_nome.value or not txt_metros.value:
            return 

        try:
            # Garante que os valores são salvos como números
            metros_val = float(txt_metros.value.replace(',', '.'))
            qtd_val = int(txt_qtd.value) if txt_qtd.value else 0
            
            dados = {
                "nome": txt_nome.value,
                "metros": metros_val,
                "quantidade": qtd_val
            }
            
            if firebase_service.add_document("estoque", dados):
                fechar_dialogo()
                carregar_dados()
        except ValueError:
            print("Erro: Valores numéricos inválidos")

    def abrir_popup_novo(e):
        txt_nome.value = ""; txt_metros.value = ""; txt_qtd.value = ""
        page.dialog = ft.AlertDialog(
            title=ft.Text("Novo Item no Estoque", weight="bold"),
            content=ft.Column([
                txt_nome,
                ft.Row([txt_metros, txt_qtd], spacing=10)
            ], tight=True, spacing=15),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.ElevatedButton("Salvar", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=salvar_produto)
            ]
        )
        page.dialog.open = True
        page.update()

    def abrir_popup_editar(item):
        txt_nome.value = item.get('nome')
        txt_metros.value = str(item.get('metros'))
        txt_qtd.value = str(item.get('quantidade'))
        
        def salvar_edicao(e):
            try:
                dados_atualizados = {
                    "nome": txt_nome.value,
                    "metros": float(txt_metros.value.replace(',', '.')),
                    "quantidade": int(txt_qtd.value)
                }
                if firebase_service.update_document("estoque", item['id'], dados_atualizados):
                    fechar_dialogo()
                    carregar_dados()
            except ValueError:
                print("Erro: Valores numéricos inválidos na edição")

        page.dialog = ft.AlertDialog(
            title=ft.Text(f"Editar: {item.get('nome')}"),
            content=ft.Column([txt_nome, ft.Row([txt_metros, txt_qtd])], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.ElevatedButton("Atualizar", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=salvar_edicao)
            ]
        )
        page.dialog.open = True
        page.update()

    def confirmar_exclusao(id_item, nome_item):
        def deletar(e):
            if firebase_service.delete_document("estoque", id_item):
                fechar_dialogo()
                carregar_dados()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Exclusão"),
            content=ft.Text(f"Deseja realmente excluir '{nome_item}'?"),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_dialogo),
                ft.TextButton("Excluir", color=COLOR_ERROR, on_click=deletar)
            ]
        )
        page.dialog.open = True
        page.update()

    # --- MONTAGEM DA INTERFACE ---
    header = ft.Row([
        ft.Text("Gestão de Estoque", size=28, weight="bold", color=COLOR_PRIMARY),
        ft.ElevatedButton(
            "Adicionar Pedra", 
            icon=ft.icons.ADD, 
            bgcolor=COLOR_PRIMARY, 
            color=COLOR_WHITE, 
            on_click=abrir_popup_novo
        )
    ], alignment="spaceBetween")

    conteudo_principal = ft.Column([
        header,
        ft.Divider(height=20),
        grid_produtos
    ], scroll=ft.ScrollMode.AUTO, expand=True)

    # Inicializa os dados ao carregar a view
    carregar_dados()

    return LayoutBase(page, conteudo_principal, titulo="Estoque - Central Granitos")