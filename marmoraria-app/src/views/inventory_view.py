import flet as ft
from src.views.components.sidebar import Sidebar
from src.config import (
    COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, COLOR_SECONDARY, COLOR_TEXT, 
    COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING,
    SHADOW_MD, BORDER_RADIUS_LG, BORDER_RADIUS_MD
)
from src.services import firebase_service

def InventoryView(page: ft.Page):
    
    lista_chapas = []
    chapa_em_edicao_id = None 
    caminho_foto_selecionada = None

    # --- COMPONENTES DO FORMULÁRIO ---
    txt_nome = ft.TextField(label="Nome da Pedra", border_radius=BORDER_RADIUS_MD, filled=True)
    txt_metros = ft.TextField(label="Medida (m²)", suffix_text="m²", keyboard_type=ft.KeyboardType.NUMBER, border_radius=BORDER_RADIUS_MD, filled=True, expand=True)
    txt_qtd = ft.TextField(label="Qtd.", suffix_text="un", keyboard_type=ft.KeyboardType.NUMBER, border_radius=BORDER_RADIUS_MD, filled=True, expand=True)

    grid_produtos = ft.ResponsiveRow(spacing=20, run_spacing=20)

    def carregar_dados():
        grid_produtos.controls.clear()
        lista = firebase_service.get_collection("estoque")
        
        for item in lista:
            try:
                # Se o item não tiver dados essenciais, pulamos para não travar a tela
                if not item.get('id') or not item.get('nome'):
                    continue

                card = ft.Container(
                    col={"xs": 12, "sm": 6, "md": 4, "lg": 3},
                    bgcolor=COLOR_WHITE,
                    padding=15,
                    border_radius=BORDER_RADIUS_MD,
                    shadow=SHADOW_MD,
                    content=ft.Column([
                        ft.Text(item.get('nome', 'Sem nome'), weight="bold", size=16, color=COLOR_PRIMARY),
                        ft.Row([
                            ft.Container(content=ft.Text(f"{item.get('metros', '0')} m²", size=11), padding=5, bgcolor="#F0F0F0", border_radius=5),
                            ft.Container(content=ft.Text(f"{item.get('quantidade', '0')} un", size=11, color="white"), padding=5, bgcolor=COLOR_SECONDARY, border_radius=5)
                        ], alignment="spaceBetween"),
                        ft.Row([
                            ft.IconButton(ft.icons.EDIT, icon_color=COLOR_PRIMARY, icon_size=20, on_click=lambda e, i=item: abrir_popup(e, i)),
                            ft.IconButton(ft.icons.DELETE, icon_color=COLOR_ERROR, icon_size=20, on_click=lambda e, id=item['id']: confirmar_exclusao(id))
                        ], alignment="end", spacing=0)
                    ], spacing=5)
                )
                grid_produtos.controls.append(card)
            except Exception as ex:
                print(f"Erro ao renderizar item do estoque: {ex}")
                continue

        page.update()

    def abrir_popup(e, item=None):
        nonlocal chapa_em_edicao_id
        if item:
            chapa_em_edicao_id = item['id']
            txt_nome.value = item.get('nome')
            txt_metros.value = str(item.get('metros'))
            txt_qtd.value = str(item.get('quantidade'))
        else:
            chapa_em_edicao_id = None
            txt_nome.value = ""; txt_metros.value = ""; txt_qtd.value = ""
        
        dlg = ft.AlertDialog(
            title=ft.Text("Cadastrar Pedra"),
            content=ft.Column([txt_nome, ft.Row([txt_metros, txt_qtd])], tight=True, spacing=15),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: page.close_dialog()),
                ft.ElevatedButton("Salvar", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=salvar_estoque)
            ]
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def salvar_estoque(e):
        dados = {
            "nome": txt_nome.value,
            "metros": txt_metros.value,
            "quantidade": txt_qtd.value
        }
        if chapa_em_edicao_id:
            firebase_service.update_document("estoque", chapa_em_edicao_id, dados)
        else:
            firebase_service.add_document("estoque", dados)
        page.close_dialog()
        carregar_dados()

    def confirmar_exclusao(id):
        def deletar(e):
            firebase_service.delete_document("estoque", id)
            page.close_dialog()
            carregar_dados()
        
        page.dialog = ft.AlertDialog(
            title=ft.Text("Excluir?"),
            actions=[ft.TextButton("Não", on_click=lambda _: page.close_dialog()), ft.TextButton("Sim", on_click=deletar)]
        )
        page.dialog.open = True
        page.update()

    header = ft.Container(
        content=ft.Row([
            ft.Text("Estoque", size=28, weight="bold", color=COLOR_PRIMARY),
            ft.ElevatedButton("Novo", icon=ft.icons.ADD, bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=abrir_popup)
        ], alignment="spaceBetween"),
        padding=ft.padding.only(bottom=10)
    )

    conteudo = ft.Container(
        expand=True, bgcolor=COLOR_BACKGROUND, padding=15,
        content=ft.Column([header, ft.Divider(), grid_produtos], scroll=ft.ScrollMode.AUTO)
    )

    carregar_dados()
    from src.views.layout_base import LayoutBase
    return LayoutBase(page, conteudo, "Estoque")