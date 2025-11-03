

import tkinter as tk
from tkinter import messagebox, scrolledtext
import numpy as np
import matplotlib.pyplot as plt


UNICODE = {
    'r': '\u265C', 'n': '\u265E', 'b': '\u265D', 'q': '\u265B', 'k': '\u265A', 'p': '\u265F',
    'R': '\u2656', 'N': '\u2658', 'B': '\u2657', 'Q': '\u2655', 'K': '\u2654', 'P': '\u2659'
}


START_BOARD = np.array([
    list('rnbqkbnr'),
    list('pppppppp'),
    list('........'),
    list('........'),
    list('........'),
    list('........'),
    list('PPPPPPPP'),
    list('RNBQKBNR')
])

class ChessGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess - Minor Project (NumPy + Matplotlib)")
        self.board = START_BOARD.copy()
        self.turn = 'white'
        self.selected = None
        self.buttons = [[None]*8 for _ in range(8)]
        self.move_history = []
        self.white_captures = 0
        self.black_captures = 0

        self._build_ui()
        self._draw_board()

    def _build_ui(self):
        board_frame = tk.Frame(self.root)
        board_frame.grid(row=0, column=0)

        for r in range(8):
            for c in range(8):
                b = tk.Button(board_frame, text='', font=('Helvetica', 28), width=2, height=1,
                              command=lambda rr=r, cc=c: self.on_click(rr, cc))
                b.grid(row=r, column=c)
                self.buttons[r][c] = b

        right_frame = tk.Frame(self.root)
        right_frame.grid(row=0, column=1, sticky='n')

        tk.Label(right_frame, text='Turn:', font=('Arial', 12, 'bold')).pack(anchor='w')
        self.turn_label = tk.Label(right_frame, text=self.turn.capitalize())
        self.turn_label.pack(anchor='w')

        tk.Button(right_frame, text='Reset Game', command=self.reset_board).pack(fill='x', pady=(8, 2))
        tk.Button(right_frame, text='Show Statistics', command=self.show_statistics).pack(fill='x')

        tk.Label(right_frame, text='Move History:', font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 0))
        self.history_box = scrolledtext.ScrolledText(right_frame, width=30, height=20, state='disabled')
        self.history_box.pack()

    def _draw_board(self):
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                text = UNICODE.get(piece, '') if piece != '.' else ''
                color = '#EEEED2' if (r+c) % 2 == 0 else '#769656'
                self.buttons[r][c].config(text=text, bg=color, activebackground=color)

        self.turn_label.config(text=self.turn.capitalize())

    def on_click(self, r, c):
        piece = self.board[r][c]
        if self.selected is None:
            if piece == '.' or self._piece_color(piece) != self.turn:
                return
            self.selected = (r, c)
            self._highlight_moves(r, c)
        else:
            from_r, from_c = self.selected
            if (r, c) == self.selected:
                self.selected = None
                self._draw_board()
                return
            moves = self.legal_moves(from_r, from_c)
            if (r, c) in moves:
                self._make_move((from_r, from_c), (r, c))
                self.selected = None
                self._draw_board()
            else:
                self.selected = None
                self._draw_board()

    def _highlight_moves(self, r, c):
        self._draw_board()
        moves = self.legal_moves(r, c)
        for (mr, mc) in moves:
            self.buttons[mr][mc].config(bg='#BACA2B')
        self.buttons[r][c].config(bg='#F6F669')

    def _make_move(self, frm, to):
        fr, fc = frm
        tr, tc = to
        piece = self.board[fr][fc]
        captured = self.board[tr][tc]

        if captured != '.':
            if self.turn == 'white':
                self.white_captures += 1
            else:
                self.black_captures += 1

        
        self.board[tr][tc] = piece
        self.board[fr][fc] = '.'

        
        if piece == 'P' and tr == 0:
            self.board[tr][tc] = 'Q'
        elif piece == 'p' and tr == 7:
            self.board[tr][tc] = 'q'

        move_str = f"{self._piece_symbol(piece)} {chr(fc+97)}{8-fr}->{chr(tc+97)}{8-tr}"
        self.move_history.append(move_str)
        self._append_history(move_str)

        
        self.turn = 'black' if self.turn == 'white' else 'white'

    def show_statistics(self):
        white_moves = sum(1 for m in self.move_history if m[0].isupper())
        black_moves = len(self.move_history) - white_moves
        labels = ['White Moves', 'Black Moves', 'White Captures', 'Black Captures']
        values = [white_moves, black_moves, self.white_captures, self.black_captures]
        colors = ['#EEEED2', '#769656', '#D18B47', '#B58863']

        plt.figure(figsize=(7, 5))
        plt.bar(labels, values, color=colors)
        plt.title('Chess Game Statistics')
        plt.ylabel('Count')
        plt.show()

    def reset_board(self):
        self.board = START_BOARD.copy()
        self.turn = 'white'
        self.selected = None
        self.move_history.clear()
        self.white_captures = 0
        self.black_captures = 0
        self.history_box.config(state='normal')
        self.history_box.delete('1.0', 'end')
        self.history_box.config(state='disabled')
        self._draw_board()

    def _append_history(self, text):
        self.history_box.config(state='normal')
        self.history_box.insert('end', text + '\n')
        self.history_box.see('end')
        self.history_box.config(state='disabled')

    def _piece_color(self, piece):
        if piece == '.':
            return None
        return 'white' if piece.isupper() else 'black'

    def _piece_symbol(self, piece):
        return piece.upper() if piece.isalpha() else '?'

    def legal_moves(self, r, c):
        piece = self.board[r][c]
        if piece == '.':
            return []
        color = self._piece_color(piece)
        moves = []
        on_board = lambda rr, cc: 0 <= rr < 8 and 0 <= cc < 8

        def add_move(rr, cc):
            if not on_board(rr, cc):
                return
            target = self.board[rr][cc]
            if target == '.' or self._piece_color(target) != color:
                moves.append((rr, cc))

        p = piece.lower()
        if p == 'p':  
            dir = -1 if color == 'white' else 1
            if on_board(r+dir, c) and self.board[r+dir][c] == '.':
                moves.append((r+dir, c))
                start = 6 if color == 'white' else 1
                if r == start and self.board[r+2*dir][c] == '.':
                    moves.append((r+2*dir, c))
            for dc in (-1, 1):
                rr, cc = r+dir, c+dc
                if on_board(rr, cc) and self.board[rr][cc] != '.' and self._piece_color(self.board[rr][cc]) != color:
                    moves.append((rr, cc))

        elif p == 'r':
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                rr, cc = r+dr, c+dc
                while on_board(rr, cc):
                    if self.board[rr][cc] == '.':
                        moves.append((rr, cc))
                    else:
                        if self._piece_color(self.board[rr][cc]) != color:
                            moves.append((rr, cc))
                        break
                    rr += dr; cc += dc

        elif p == 'n':
            for dr, dc in ((2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)):
                add_move(r+dr, c+dc)

        elif p == 'b':
            for dr, dc in ((1,1),(1,-1),(-1,1),(-1,-1)):
                rr, cc = r+dr, c+dc
                while on_board(rr, cc):
                    if self.board[rr][cc] == '.':
                        moves.append((rr, cc))
                    else:
                        if self._piece_color(self.board[rr][cc]) != color:
                            moves.append((rr, cc))
                        break
                    rr += dr; cc += dc

        elif p == 'q':
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                rr, cc = r+dr, c+dc
                while on_board(rr, cc):
                    if self.board[rr][cc] == '.':
                        moves.append((rr, cc))
                    else:
                        if self._piece_color(self.board[rr][cc]) != color:
                            moves.append((rr, cc))
                        break
                    rr += dr; cc += dc

        elif p == 'k':
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr == 0 and dc == 0:
                        continue
                    add_move(r+dr, c+dc)

        return moves


if __name__ == '__main__':
    root = tk.Tk()
    game = ChessGame(root)
    root.mainloop()
