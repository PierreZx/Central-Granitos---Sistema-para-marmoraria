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
    txt_nome = ft.TextField(
        label="Nome da Pedra",
        hint_text="Ex: Preto São Gabriel",
        border_radius=BORDER_RADIUS_MD,
        filled=True,
        fill_color=ft.colors.WHITE,
        focused_border_color=COLOR_PRIMARY
    )
    
    txt_metros = ft.TextField(
        label="Medida (m²)",
        suffix_text="m²",
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=BORDER_RADIUS_MD,
        filled=True,
        fill_color=ft.colors.WHITE,
        expand=True
    )
    
    txt_qtd = ft.TextField(
        label="Qtd.",
        suffix_text="un",
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=BORDER_RADIUS_MD,
        filled=True,
        fill_color=ft.colors.WHITE,
        expand=True
    )
    
    txt_valor = ft.TextField(
        label="Valor (m²)",
        prefix_text="R$ ",
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=BORDER_RADIUS_MD,
        filled=True,
        fill_color=ft.colors.WHITE
    )
    
    txt_foto_status = ft.Text("Nenhuma foto selecionada", size=12, color=ft.colors.GREY_600)
    
    def selecionar_foto_result(e: ft.FilePickerResultEvent):
        nonlocal caminho_foto_selecionada
        if e.files:
            caminho_foto_selecionada = e.files[0].path
            txt_foto_status.value = f"📸 {e.files[0].name}"
            txt_foto_status.color = COLOR_SUCCESS
            page.update()

    file_picker = ft.FilePicker(on_result=selecionar_foto_result)
    page.overlay.append(file_picker)

    def carregar_dados():
        nonlocal lista_chapas
        lista_chapas = firebase_service.get_estoque_lista()
        atualizar_grid()

    def abrir_popup(e, chapa=None):
        nonlocal chapa_em_edicao_id, caminho_foto_selecionada
        if chapa:
            chapa_em_edicao_id = chapa['id']
            txt_nome.value = chapa.get('nome', '')
            txt_metros.value = str(chapa.get('metros', ''))
            txt_qtd.value = str(chapa.get('quantidade', ''))
            txt_valor.value = str(chapa.get('valor_m2', ''))
            caminho_foto_selecionada = chapa.get('foto', None)
            txt_foto_status.value = "✅ Foto mantida" if caminho_foto_selecionada else "📷 Sem foto"
            txt_foto_status.color = COLOR_SUCCESS if caminho_foto_selecionada else ft.colors.GREY_600
            titulo_dialog.value = "✏️ Editar Chapa"
        else:
            chapa_em_edicao_id = None
            txt_nome.value = ""
            txt_metros.value = ""
            txt_qtd.value = ""
            txt_valor.value = ""
            caminho_foto_selecionada = None
            txt_foto_status.value = "📷 Nenhuma foto selecionada"
            txt_foto_status.color = ft.colors.GREY_600
            titulo_dialog.value = "➕ Adicionar Nova Chapa"
        
        page.dialog = dialog_form
        dialog_form.open = True
        page.update()

    def fechar_popup(e):
        dialog_form.open = False
        page.update()

    def salvar_chapa(e):
        if not txt_nome.value:
            page.snack_bar = ft.SnackBar(ft.Text("Nome é obrigatório!"), bgcolor=COLOR_ERROR)
            page.snack_bar.open = True
            page.update()
            return

        dados = {
            "nome": txt_nome.value,
            "metros": txt_metros.value,
            "quantidade": txt_qtd.value,
            "valor_m2": txt_valor.value,
            "foto": caminho_foto_selecionada 
        }

        if chapa_em_edicao_id:
            firebase_service.update_item_estoque(chapa_em_edicao_id, dados)
        else:
            firebase_service.add_item_estoque(dados)

        page.snack_bar = ft.SnackBar(ft.Text("Salvo com sucesso!"), bgcolor=COLOR_SUCCESS)
        page.snack_bar.open = True
        dialog_form.open = False
        carregar_dados()
        page.update()

    def confirmar_exclusao(id_para_deletar):
        def deletar(e):
            firebase_service.delete_item_estoque(id_para_deletar)
            confirm_dialog.open = False
            carregar_dados()
            page.snack_bar = ft.SnackBar(ft.Text("Item removido!"), bgcolor=COLOR_SUCCESS)
            page.snack_bar.open = True
            page.update()
        
        def cancelar(e):
            confirm_dialog.open = False
            page.update()

        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Tem certeza?", size=18, weight="bold"),
            content=ft.Text("Isso removerá o item do estoque permanentemente."),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.ElevatedButton("Excluir", bgcolor=COLOR_ERROR, color=COLOR_WHITE, on_click=deletar),
            ],
        )
        page.dialog = confirm_dialog
        confirm_dialog.open = True
        page.update()

    titulo_dialog = ft.Text("Chapa", size=20, weight="bold")
    
    # --- LAYOUT DO FORMULÁRIO (Vertical para não cortar no mobile) ---
    conteudo_form = ft.Column([
        ft.Text("Informações", weight="bold", color=COLOR_PRIMARY),
        txt_nome,
        ft.Container(height=10),
        ft.Text("Dimensões e Valores", weight="bold", color=COLOR_PRIMARY),
        ft.Row([txt_metros, txt_qtd], spacing=10),
        txt_valor,
        ft.Divider(),
        ft.Row([
            ft.ElevatedButton("Foto", icon=ft.icons.CAMERA_ALT, on_click=lambda _: file_picker.pick_files()),
            txt_foto_status
        ], alignment="spaceBetween")
    ], tight=True, width=320, scroll=ft.ScrollMode.AUTO)

    dialog_form = ft.AlertDialog(
        title=titulo_dialog,
        content=conteudo_form,
        actions=[
            ft.TextButton("Cancelar", on_click=fechar_popup),
            ft.ElevatedButton("Salvar", bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=salvar_chapa)
        ],
        shape=ft.RoundedRectangleBorder(radius=15),
    )

    grid_produtos = ft.GridView(
        expand=True,
        runs_count=2, # Menos colunas no mobile para caber info
        max_extent=250,
        child_aspect_ratio=0.75,
        spacing=10,
        run_spacing=10
    )

    def atualizar_grid():
        grid_produtos.controls.clear()
        
        if not lista_chapas:
            grid_produtos.controls.append(ft.Container(content=ft.Text("Estoque vazio.", color="grey"), alignment=ft.alignment.center, padding=40))
        else:
            for item in lista_chapas:
                try: val = float(str(item.get('valor_m2', 0)).replace(',', '.'))
                except: val = 0.0
                
                foto = item.get('foto')
                img_widget = ft.Image(src=foto, fit=ft.ImageFit.COVER) if foto else ft.Icon(ft.icons.IMAGE_NOT_SUPPORTED, size=40, color="grey")

                card = ft.Container(
                    bgcolor=COLOR_WHITE,
                    border_radius=12,
                    padding=10,
                    shadow=SHADOW_MD,
                    content=ft.Column([
                        ft.Container(content=img_widget, height=100, bgcolor="#F0F0F0", border_radius=8, alignment=ft.alignment.center, clip_behavior=ft.ClipBehavior.HARD_EDGE),
                        ft.Text(item.get('nome', 'Sem nome'), weight="bold", size=14, color=COLOR_TEXT, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"R$ {val:.2f} /m²", weight="bold", size=13, color=COLOR_PRIMARY),
                        ft.Row([
                            ft.Container(content=ft.Text(f"{item.get('metros')} m²", size=11), padding=5, bgcolor="#F0F0F0", border_radius=5),
                            ft.Container(content=ft.Text(f"{item.get('quantidade')} un", size=11, color="white"), padding=5, bgcolor=COLOR_SECONDARY, border_radius=5)
                        ], alignment="spaceBetween"),
                        ft.Row([
                            ft.IconButton(ft.icons.EDIT, icon_color=COLOR_PRIMARY, icon_size=20, on_click=lambda e, i=item: abrir_popup(e, i)),
                            ft.IconButton(ft.icons.DELETE, icon_color=COLOR_ERROR, icon_size=20, on_click=lambda e, id=item['id']: confirmar_exclusao(id))
                        ], alignment="end", spacing=0)
                    ], spacing=5)
                )
                grid_produtos.controls.append(card)
        page.update()

    header = ft.Container(
        content=ft.Row([
            ft.Text("Estoque", size=28, weight="bold", color=COLOR_PRIMARY),
            ft.ElevatedButton("Novo", icon=ft.icons.ADD, bgcolor=COLOR_PRIMARY, color=COLOR_WHITE, on_click=abrir_popup)
        ], alignment="spaceBetween"),
        padding=ft.padding.only(bottom=10)
    )

    conteudo = ft.Container(
        expand=True, 
        bgcolor=COLOR_BACKGROUND, 
        padding=15,
        content=ft.Column([header, ft.Divider(), ft.Container(content=grid_produtos, expand=True)])
    )

    carregar_dados()
    from src.views.layout_base import LayoutBase
    return LayoutBase(page, conteudo, "Estoque")