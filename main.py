import tkinter as tk
from tkinter import simpledialog, messagebox
import random

LIGHT_SQ = "#F0D9B5"    
DARK_SQ  = "#B58863"
QUEEN_BG = "#FFD166"
GRID_CLR = "#444444"

class QueenGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Juego de Reina: un paso por movimiento (con bloqueo)")
        self.n = None              
        self.square = None        
        self.canvas = None
        self.queen_pos = None     
        self.blocked_pos = None   
        self.move_count = 0
        self.ui_built = False
        self._build_ui()
        self.ask_board_size(initial=True)

    def _build_ui(self):
        top = tk.Frame(self.root, padx=8, pady=8)
        top.pack(side=tk.TOP, fill=tk.X)

        self.size_lbl = tk.Label(top, text="Tablero: -", font=("Segoe UI", 10, "bold"))
        self.size_lbl.pack(side=tk.LEFT)

        tk.Button(top, text="Cambiar tamaño", command=self.ask_board_size).pack(side=tk.LEFT, padx=(12, 0))
        tk.Button(top, text="Reiniciar", command=self.reset_game).pack(side=tk.LEFT, padx=6)
        tk.Button(top, text="Aleatorio reina", command=self.randomize_queen).pack(side=tk.LEFT, padx=6)
        tk.Button(top, text="Nuevo bloqueo", command=self.randomize_block).pack(side=tk.LEFT, padx=6)

        self.moves_lbl = tk.Label(top, text="Movimientos: 0")
        self.moves_lbl.pack(side=tk.RIGHT)
        self.canvas_frame = tk.Frame(self.root, padx=8, pady=8)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

    def _ensure_canvas(self):
        max_canvas = 720
        min_square = 36
        max_square = 90

        self.square = max(min_square, min(max_square, max_canvas // self.n))
 
        canvas_size = self.square * self.n + 1

        if self.canvas is not None:
            self.canvas.destroy()
        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=canvas_size,
            height=canvas_size,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)


    def ask_board_size(self, initial=False):

        while True:
            try:
                n = simpledialog.askinteger(
                    "Tamaño del tablero",
                    "Elige el tamaño N para un tablero NxN (mín. 2, máx. 20):",
                    minvalue=2,
                    maxvalue=20,
                    parent=self.root
                )
                if n is None:
                    if initial:
                        n = 8
                    else:
                        return
                self.n = n
                break
            except Exception:
                messagebox.showerror("Error", "Ingresa un valor válido.")
        self.size_lbl.config(text=f"Tablero: {self.n} x {self.n}")
        self._ensure_canvas()
        self.new_game()

    def new_game(self):
        self.queen_pos = (self.n // 2, self.n // 2)
        self.randomize_block(avoid_current=True)
        self.move_count = 0
        self.update_moves_label()
        self.draw_board()

    def reset_game(self):
        if self.n is None:
            return
        self.new_game()

    def randomize_queen(self):
        if self.n is None:
            return

        while True:
            pos = (random.randrange(self.n), random.randrange(self.n))
            if pos != self.blocked_pos:
                self.queen_pos = pos
                break
        self.move_count = 0
        self.update_moves_label()
        self.draw_board()

    def randomize_block(self, avoid_current=False):
        if self.n is None:
            return

        while True:
            pos = (random.randrange(self.n), random.randrange(self.n))
            if pos != self.queen_pos:
                self.blocked_pos = pos
                break
        if not avoid_current:
            self.draw_board()

    def update_moves_label(self):
        self.moves_lbl.config(text=f"Movimientos: {self.move_count}")

#DIBUJO -------------------------------------------------
    def draw_board(self):
        self.canvas.delete("all")

        canvas_w = int(self.canvas.cget("width"))
        canvas_h = int(self.canvas.cget("height"))

        for r in range(self.n):
            for c in range(self.n):
                x0 = c * self.square
                y0 = r * self.square
                x1 = min(x0 + self.square, canvas_w - 1)
                y1 = min(y0 + self.square, canvas_h - 1)
                color = LIGHT_SQ if (r + c) % 2 == 0 else DARK_SQ
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=GRID_CLR)

        if self.blocked_pos is not None:
            br, bc = self.blocked_pos
            bx0, by0 = bc * self.square, br * self.square
            cx = bx0 + self.square // 2
            cy = by0 + self.square // 2
            radius = max(6, self.square // 6)
            self.canvas.create_oval(
                cx - radius, cy - radius, cx + radius, cy + radius,
                fill="#D90429", outline="black", width=1
            )

        qr, qc = self.queen_pos
        qx0, qy0 = qc * self.square, qr * self.square
        qx1 = min(qx0 + self.square, canvas_w - 1)
        qy1 = min(qy0 + self.square, canvas_h - 1)
        self.canvas.create_rectangle(qx0, qy0, qx1, qy1, fill=QUEEN_BG, outline=GRID_CLR, width=2)

        font_main = ("Segoe UI Symbol", max(18, self.square // 2), "bold")
        cx = qx0 + self.square // 2
        cy = qy0 + self.square // 2
        try:
            self.canvas.create_text(cx, cy, text="♛", font=font_main)
        except tk.TclError:
            self.canvas.create_text(cx, cy, text="Q", font=font_main)

        for (rr, cc) in self.legal_moves_from(self.queen_pos):
            if (rr, cc) == self.blocked_pos:
                continue
            hx0, hy0 = cc * self.square, rr * self.square
            hx1 = min(hx0 + self.square, canvas_w - 1)
            hy1 = min(hy0 + self.square, canvas_h - 1)
            self.canvas.create_rectangle(hx0+4, hy0+4, hx1-4, hy1-4, outline="#2B6CB0", width=3)

    def legal_moves_from(self, pos):
        r, c = pos
        moves = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr, cc = r + dr, c + dc
                if 0 <= rr < self.n and 0 <= cc < self.n:
                    if (rr, cc) != self.blocked_pos:  # no se puede mover a la bloqueada
                        moves.append((rr, cc))
        return moves

#INTERACCION -----------------------------------------
    def pixel_to_square(self, x, y):
        c = x // self.square
        r = y // self.square
        if 0 <= r < self.n and 0 <= c < self.n:
            return int(r), int(c)
        return None

    def on_click(self, event):
        clicked = self.pixel_to_square(event.x, event.y)
        if not clicked:
            return
        if clicked in self.legal_moves_from(self.queen_pos):
            self.queen_pos = clicked
            self.move_count += 1
            self.update_moves_label()
            self.draw_board()
        else:
            pass


def main():
    root = tk.Tk()
    app = QueenGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()