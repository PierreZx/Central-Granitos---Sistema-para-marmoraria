import flet as ft
from src.views.components.sidebar import Sidebar
from src.config import COLOR_BACKGROUND, COLOR_PRIMARY, COLOR_WHITE, COLOR_SECONDARY, COLOR_TEXT
from src.services import firebase_service

def InventoryView(page: ft.Page):
    
    # --- Variáveis de Estado ---
    lista_chapas = []
    chapa_em_edicao_id = None 
    caminho_foto_selecionada = None

    # --- Componentes do Formulário (Popup) ---
    txt_nome = ft.TextField(label="Nome da Pedra (Ex: Preto São Gabriel)", border_radius=10)
    
    # Novos campos organizados
    txt_metros = ft.TextField(label="Medida (m²)", suffix_text="m²", keyboard_type=ft.KeyboardType.NUMBER, border_radius=10, width=130)
    txt_qtd = ft.TextField(label="Qtd.", suffix_text="un", keyboard_type=ft.KeyboardType.NUMBER, border_radius=10, width=100)
    
    # --- NOVO CAMPO: VALOR ---
    txt_valor = ft.TextField(label="Valor", prefix_text="R$ ", keyboard_type=ft.KeyboardType.NUMBER, border_radius=10, width=130)
    
    txt_foto_status = ft.Text("Nenhuma foto selecionada", size=12, color=ft.Colors.GREY_600)
    
    # Seletor de Arquivos
    def selecionar_foto_result(e: ft.FilePickerResultEvent):
        nonlocal caminho_foto_selecionada
        if e.files:
            caminho_foto_selecionada = e.files[0].path
            txt_foto_status.value = f"Foto: {e.files[0].name}"
            page.update()

    file_picker = ft.FilePicker(on_result=selecionar_foto_result)
    page.overlay.append(file_picker)

    # --- Funções Lógicas ---

    def carregar_dados():
        nonlocal lista_chapas
        lista_chapas = firebase_service.get_estoque_lista()
        atualizar_grid()

    def abrir_popup(e, chapa=None):
        nonlocal chapa_em_edicao_id, caminho_foto_selecionada
        
        if chapa:
            # Modo Edição
            chapa_em_edicao_id = chapa['id']
            txt_nome.value = chapa.get('nome', '')
            txt_metros.value = str(chapa.get('metros', ''))
            txt_qtd.value = str(chapa.get('quantidade', ''))
            txt_valor.value = str(chapa.get('valor_m2', '')) # Carrega valor
            caminho_foto_selecionada = chapa.get('foto', None)
            txt_foto_status.value = "Foto mantida" if caminho_foto_selecionada else "Sem foto"
            titulo_dialog.value = "Editar Chapa"
        else:
            # Modo Criação
            chapa_em_edicao_id = None
            txt_nome.value = ""
            txt_metros.value = ""
            txt_qtd.value = ""
            txt_valor.value = "" # Limpa valor
            caminho_foto_selecionada = None
            txt_foto_status.value = "Nenhuma foto selecionada"
            titulo_dialog.value = "Adicionar Nova Chapa"
        
        page.open(dialog_form)
        page.update()

    def fechar_popup(e):
        page.close(dialog_form)
        page.update()

    def salvar_chapa(e):
        if not txt_nome.value:
            page.snack_bar = ft.SnackBar(ft.Text("O nome é obrigatório!"), bgcolor=ft.Colors.RED)
            page.snack_bar.open = True
            page.update()
            return

        dados = {
            "nome": txt_nome.value,
            "metros": txt_metros.value,
            "quantidade": txt_qtd.value,
            "valor_m2": txt_valor.value, # Salva valor
            "foto": caminho_foto_selecionada 
        }

        if chapa_em_edicao_id:
            sucesso, msg = firebase_service.update_item_estoque(chapa_em_edicao_id, dados)
        else:
            sucesso, msg = firebase_service.add_item_estoque(dados)

        page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=ft.Colors.GREEN if sucesso else ft.Colors.RED)
        page.snack_bar.open = True
        
        page.close(dialog_form)
        carregar_dados()
        page.update()

    def confirmar_exclusao(id_para_deletar):
        def deletar(e):
            firebase_service.delete_item_estoque(id_para_deletar)
            page.close(confirm_dialog)
            carregar_dados()
            page.snack_bar = ft.SnackBar(ft.Text("Item removido!"), bgcolor=ft.Colors.GREEN)
            page.snack_bar.open = True
            page.update()
        
        def cancelar(e):
            page.close(confirm_dialog)
            page.update()

        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Tem certeza?"),
            content=ft.Text("Você realmente deseja apagar este item do estoque?"),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.TextButton("Sim, Apagar", on_click=deletar, style=ft.ButtonStyle(color=ft.Colors.RED)),
            ],
        )
        page.open(confirm_dialog)
        page.update()

    # --- Elementos Visuais ---

    titulo_dialog = ft.Text("Adicionar Nova Chapa", weight="bold", size=20)
    
    dialog_form = ft.AlertDialog(
        title=titulo_dialog,
        content=ft.Column([
            txt_nome,
            ft.Row([txt_metros, txt_qtd, txt_valor], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), # Campo Valor aqui
            ft.Divider(),
            ft.Row([
                ft.ElevatedButton("Escolher Foto", icon=ft.Icons.CAMERA_ALT, on_click=lambda _: file_picker.pick_files()),
                txt_foto_status
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ], tight=True, width=450), # Aumentei um pouco a largura
        actions=[
            ft.TextButton("Cancelar", on_click=fechar_popup),
            ft.ElevatedButton("Salvar", on_click=salvar_chapa, bgcolor=COLOR_PRIMARY, color=COLOR_WHITE),
        ],
    )

    grid_produtos = ft.GridView(
        expand=True,
        runs_count=5,
        max_extent=250,
        child_aspect_ratio=0.75, # Ajustei a altura do card para caber o preço
        spacing=20,
        run_spacing=20,
    )

    def atualizar_grid():
        grid_produtos.controls.clear()
        
        if not lista_chapas:
            grid_produtos.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, size=60, color=ft.Colors.GREY_300),
                        ft.Text("Estoque vazio.", color=ft.Colors.GREY_400)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    alignment=ft.alignment.center
                )
            )
        else:
            for item in lista_chapas:
                imagem_bg = item.get('foto') if item.get('foto') else "https://via.placeholder.com/150"
                valor_formatado = f"R$ {float(item.get('valor_m2', 0)):.2f}" if item.get('valor_m2') else "R$ 0.00"

                card = ft.Container(
                    bgcolor=COLOR_WHITE,
                    border_radius=15,
                    padding=10,
                    shadow=ft.BoxShadow(blur_radius=10, color="#00000010"),
                    content=ft.Column([
                        # Foto
                        ft.Container(
                            height=100,
                            border_radius=10,
                            bgcolor=ft.Colors.GREY_100,
                            alignment=ft.alignment.center,
                            content=ft.Icon(ft.Icons.IMAGE, size=40, color=ft.Colors.GREY_300) if not item.get('foto') else ft.Image(src=item['foto'], fit=ft.ImageFit.COVER, border_radius=10)
                        ),
                        # Texto Principal
                        ft.Text(item.get('nome', 'Sem nome'), weight="bold", size=16, color=COLOR_TEXT, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        
                        # Preço (Destaque)
                        ft.Text(f"{valor_formatado} /m²", weight="bold", size=14, color=COLOR_PRIMARY),

                        # Detalhes
                        ft.Row([
                            ft.Icon(ft.Icons.SQUARE_FOOT, size=14, color=COLOR_SECONDARY),
                            ft.Text(f"{item.get('metros', 0)} m²", size=12, color=ft.Colors.GREY_700),
                            ft.Container(width=10),
                            ft.Icon(ft.Icons.LAYERS, size=14, color=COLOR_SECONDARY),
                            ft.Text(f"{item.get('quantidade', 0)} unid.", size=12, color=ft.Colors.GREY_700),
                        ], spacing=0),
                        
                        ft.Divider(height=5, color="transparent"),
                        
                        # Botões
                        ft.Row([
                            ft.IconButton(ft.Icons.EDIT, icon_color=ft.Colors.BLUE, tooltip="Editar", on_click=lambda e, i=item: abrir_popup(e, i)),
                            ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED, tooltip="Excluir", on_click=lambda e, id=item['id']: confirmar_exclusao(id)),
                        ], alignment=ft.MainAxisAlignment.END)
                    ])
                )
                grid_produtos.controls.append(card)
        page.update()

    btn_adicionar = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        bgcolor=COLOR_PRIMARY,
        on_click=abrir_popup,
        tooltip="Adicionar Chapa"
    )

    carregar_dados()

    return ft.View(
        route="/estoque",
        padding=0,
        floating_action_button=btn_adicionar,
        controls=[
            ft.Row([
                Sidebar(page),
                ft.Container(
                    expand=True,
                    bgcolor=COLOR_BACKGROUND,
                    padding=30,
                    content=ft.Column([
                        ft.Text("Controle de Estoque", size=28, weight="bold", color=COLOR_PRIMARY),
                        ft.Divider(),
                        ft.Container(content=grid_produtos, expand=True)
                    ])
                )
            ], expand=True)
        ]
    )