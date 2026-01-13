import flet as ft
from src.views.components.budget_composition import BancadaPiece, CompositionManager

SNAP_DISTANCE = 15


class DraggablePiece(ft.GestureDetector):
    def __init__(self, piece: BancadaPiece, scale: float = 100):
        self.piece = piece
        self.scale = scale

        self.width_px = piece.largura * scale
        self.depth_px = piece.profundidade * scale

        self.x = 50
        self.y = 50

        super().__init__(
            on_pan_update=self.on_drag,
            on_pan_end=self.on_release,
            content=self._build_piece()
        )

    def _build_piece(self):
        return ft.Container(
            width=self.width_px,
            height=self.depth_px,
            bgcolor=ft.colors.GREY_300,
            border=ft.border.all(2, ft.colors.BLACK),
            alignment=ft.alignment.center,
            content=ft.Text(self.piece.nome, size=12)
        )

    def on_drag(self, e: ft.DragUpdateEvent):
        self.x += e.delta_x
        self.y += e.delta_y
        self.update_position()

    def on_release(self, e):
        # Snap será tratado externamente
        pass

    def update_position(self):
        # Garantir que o Positioned seja atualizado corretamente
        if isinstance(self.parent, ft.Positioned):
            self.parent.left = self.x
            self.parent.top = self.y
            self.parent.update()


class BudgetInteractiveCanvas(ft.UserControl):
    def __init__(self, composition: CompositionManager):
        super().__init__()
        self.composition = composition
        self.scale = 100
        self.pieces_ui: list[DraggablePiece] = []

    def build(self):
        self.stack = ft.Stack(
            width=700,
            height=400,
            controls=[]
        )

        for p in self.composition.pecas:
            draggable = DraggablePiece(p, self.scale)
            self.pieces_ui.append(draggable)

            self.stack.controls.append(
                ft.Positioned(
                    left=draggable.x,
                    top=draggable.y,
                    content=draggable
                )
            )

        return ft.Container(
            border=ft.border.all(1, ft.colors.GREY_400),
            content=self.stack
        )

    # =========================
    # SNAP LOGIC
    # =========================
    def apply_snap(self):
        for a in self.pieces_ui:
            for b in self.pieces_ui:
                if a == b:
                    continue

                # Snap horizontal: direita e esquerda
                if abs((a.x + a.width_px) - b.x) < SNAP_DISTANCE:
                    a.x = b.x - a.width_px
                elif abs(a.x - (b.x + b.width_px)) < SNAP_DISTANCE:
                    a.x = b.x + b.width_px

                # Snap vertical: cima e baixo
                if abs((a.y + a.depth_px) - b.y) < SNAP_DISTANCE:
                    a.y = b.y - a.depth_px
                elif abs(a.y - (b.y + b.depth_px)) < SNAP_DISTANCE:
                    a.y = b.y + b.depth_px

                a.update_position()
