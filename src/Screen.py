from tkinter import *
import tkinter
from enum import Enum, auto

# ====================================================================================================================
WIDTH = 800
HEIGHT = 600
FIELD_WIDTH = 400
FIELD_HEIGHT = 400
# 盤面左上角の座標
FIELD_X = 40
FIELD_Y = 40

LEFT = 0
RIGHT = 1

# ====================================================================================================================

tk = Tk()
canvas = Canvas(tk, width=WIDTH, height=HEIGHT, bg="lightgreen")
canvas.pack()


class Log(Enum):
    DELETE = auto()
    EXPLODE = auto()
    MISS_LOCK = auto()
    WIN = auto()
    DRAW = auto()
    PASS = auto()
    AUTO_OPEN = auto()


# 描画用のクラス
class Screen:
    turn_label: tkinter.Label
    bomb_label: tkinter.Label
    player1_label: tkinter.Label
    player2_label: tkinter.Label

    pass_button: tkinter.Button
    retry_button: tkinter.Button
    exit_button: tkinter.Button
    log_frame: tkinter.Frame
    log_text: tkinter.Text
    log_bar: tkinter.Scrollbar

    def __init__(self, row, column, bomb_count):
        self.row = row
        self.column = column
        self.max_bomb = bomb_count
        self.cell_size = min(FIELD_WIDTH // row, FIELD_HEIGHT // column)

        for i in range(self.row):
            canvas.create_text(40+self.cell_size*0.5 + self.cell_size * i, 20, text=chr(ord('a') + i), font=('Times', round(self.cell_size*3/5)))
        for i in range(self.column):
            canvas.create_text(20, 40+self.cell_size*0.5 + self.cell_size * i, text=i + 1, font=('Times', round(self.cell_size*3/5)))

        canvas.create_rectangle(20, 460, 440, 580, fill="white")
        canvas.create_rectangle(460, 20, 780, 440, fill="white")
        canvas.create_rectangle(460, 460, 780, 580, fill="white")
        canvas.create_text(626, 44, text="バトルスイーパー", font=('Times', 28))
        canvas.create_text(515, 110, text="現在：", font=('Times', 20))
        self.turn_label = tkinter.Label(text="Player1", font=('Times', 20), bg="white", fg="red")
        self.turn_label.place(x=555, y=90)
        canvas.create_text(515, 185, text="爆弾：", font=('Times', 20))
        self.bomb_label = tkinter.Label(text=f"{self.max_bomb}/{self.max_bomb}", font=('Times', 20), bg="white")
        self.bomb_label.place(x=555, y=165)
        canvas.create_text(120, 500, text="Player1", font=('Times', 20), fill="red")
        self.player1_label = tkinter.Label(text="0", font=('Times', 20), bg="white")
        self.player1_label.place(x=100, y=520)
        canvas.create_text(320, 500, text="Player2", font=('Times', 20), fill="blue")
        self.player2_label = tkinter.Label(text="0", font=('Times', 20), bg="white")
        self.player2_label.place(x=300, y=520)
        canvas.create_rectangle(60, 480, 180, 560)

        self.log_frame = tkinter.Frame(tk)
        self.log_frame.place(x=480, y=210)
        self.log_text = tkinter.Text(self.log_frame, width=19, height=4, font=('Times', 20), relief=tkinter.SOLID)
        self.log_text.grid(row=0, column=0)
        self.log_bar = tkinter.Scrollbar(self.log_frame, orient=tkinter.VERTICAL)
        self.log_bar.grid(row=0, column=1, sticky=tkinter.N + tkinter.S)
        self.log_bar.config(command=self.log_text.yview)
        self.log_text.config(yscrollcommand=self.log_bar.set)

    def reset(self):
        self.draw_turn(1)
        self.bomb_label["text"] = f"{self.max_bomb}/{self.max_bomb}"
        self.player1_label["text"] = "0"
        self.player2_label["text"] = "0"
        self.log_text.delete("1.0", "end")

    def set_main(self, main):
        self.main = main
        self.pass_button = tkinter.Button(text="パス", font=('Times', 20), width=10, height=2,
                                          command=self.main.pass_turn)
        self.pass_button.place(x=545, y=350)
        self.retry_button = tkinter.Button(text="やり直す", font=('Times', 20), width=8, height=1, command=self.main.retry)
        self.retry_button.place(x=480, y=500)
        self.exit_button = tkinter.Button(text="終了", font=('Times', 20), width=8, height=1, command=tk.destroy)
        self.exit_button.place(x=630, y=500)

    def draw_turn(self, player_num):
        if player_num == 1:
            canvas.create_rectangle(60, 480, 180, 560)
            canvas.create_rectangle(260, 480, 380, 560, outline="white")
            self.turn_label["fg"] = "red"
        elif player_num == 2:
            canvas.create_rectangle(60, 480, 180, 560, outline="white")
            canvas.create_rectangle(260, 480, 380, 560)
            self.turn_label["fg"] = "blue"
        self.turn_label["text"] = f"Player{player_num}"

    def draw_bomb_count(self, count):
        self.bomb_label["text"] = f"{count}/{self.max_bomb}"

    def draw_text(self, kind, player_num=-1, penalty=-1, x=-1, y=-1):
        if kind == Log.EXPLODE:
            self.log_text.insert("end", f"爆発！\nPlayer{player_num} -{penalty}P!\n")
        elif kind == Log.MISS_LOCK:
            pos = str(y + 1) + chr(ord('a') + x)
            self.log_text.insert("end", f"ミスロック！\nPlayer{player_num} -{penalty}P!\n場所：{pos}\n")
        elif kind == Log.WIN:
            self.log_text.insert("end", f"Player{player_num}の勝利！\n")
        elif kind == Log.DRAW:
            self.log_text.insert("end", f"引き分け！\n")
        elif kind == Log.PASS:
            self.log_text.insert("end", f"Player{player_num}がパス\n")
        elif kind == Log.AUTO_OPEN:
            self.log_text.insert("end", f"2連続パス\n1マス開けます\n")
        self.log_text.yview_moveto(1.0)

    def draw_score(self, player_num, score):
        if player_num == 1:
            self.player1_label["text"] = score
        if player_num == 2:
            self.player2_label["text"] = score

    def draw_close(self, x, y):
        canvas.create_rectangle(FIELD_X + x * self.cell_size, FIELD_Y + y * self.cell_size,
                                FIELD_X + (x + 1) * self.cell_size, FIELD_Y + (y + 1) * self.cell_size,
                                fill="green")

    def draw_lock(self, x, y, player_num):
        if player_num == 1:
            color = "red"
        else:
            color = "blue"
        canvas.create_rectangle(FIELD_X + x * self.cell_size, FIELD_Y + y * self.cell_size,
                                FIELD_X + (x + 1) * self.cell_size, FIELD_Y + (y + 1) * self.cell_size,
                                fill="green")
        canvas.create_polygon(FIELD_X + (x + 0.4) * self.cell_size, FIELD_Y + (y + 0.2) * self.cell_size,
                              FIELD_X + (x + 0.8) * self.cell_size, FIELD_Y + (y + 0.4) * self.cell_size,
                              FIELD_X + (x + 0.4) * self.cell_size, FIELD_Y + (y + 0.6) * self.cell_size,
                              fill=color)
        canvas.create_line(FIELD_X + (x + 0.4) * self.cell_size, FIELD_Y + (y + 0.2) * self.cell_size,
                           FIELD_X + (x + 0.4) * self.cell_size, FIELD_Y + (y + 0.9) * self.cell_size,
                           width=2)

    def draw_miss(self, x, y):
        canvas.create_line(FIELD_X + x * self.cell_size, FIELD_Y + y * self.cell_size,
                           FIELD_X + (x + 1) * self.cell_size, FIELD_Y + (y + 1) * self.cell_size)
        canvas.create_line(FIELD_X + x * self.cell_size, FIELD_Y + (y + 1) * self.cell_size,
                           FIELD_X + (x + 1) * self.cell_size, FIELD_Y + y * self.cell_size)

    def draw_open(self, x, y, count, player_num):
        if player_num == 1:
            color = "mistyrose"
        elif player_num == 2:
            color = "lightcyan"
        else:
            color = "white"
        canvas.create_rectangle(FIELD_X + x * self.cell_size, FIELD_Y + y * self.cell_size,
                                FIELD_X + (x + 1) * self.cell_size, FIELD_Y + (y + 1) * self.cell_size,
                                fill=color)
        canvas.create_text(FIELD_X + (x + 0.5) * self.cell_size, FIELD_Y + (y + 0.5) * self.cell_size,
                           text=f"{count}", font=('Times', self.cell_size))

    def draw_bomb(self, x, y, player_num):
        if player_num == 1:
            color = "mistyrose"
        else:
            color = "lightcyan"
        canvas.create_rectangle(FIELD_X + x * self.cell_size, FIELD_Y + y * self.cell_size,
                                FIELD_X + (x + 1) * self.cell_size, FIELD_Y + (y + 1) * self.cell_size,
                                fill=color)
        canvas.create_oval(FIELD_X + (x + 0.2) * self.cell_size, FIELD_Y + (y + 0.2) * self.cell_size,
                           FIELD_X + (x + 0.8) * self.cell_size, FIELD_Y + (y + 0.8) * self.cell_size,
                           fill="black")
        canvas.create_line(FIELD_X + (x + 0.2) * self.cell_size, FIELD_Y + (y + 0.2) * self.cell_size,
                           FIELD_X + (x + 0.8) * self.cell_size, FIELD_Y + (y + 0.8) * self.cell_size, width=3)
        canvas.create_line(FIELD_X + (x + 0.2) * self.cell_size, FIELD_Y + (y + 0.8) * self.cell_size,
                           FIELD_X + (x + 0.8) * self.cell_size, FIELD_Y + (y + 0.2) * self.cell_size, width=3)
        canvas.create_line(FIELD_X + (x + 0.5) * self.cell_size, FIELD_Y + (y + 0.1) * self.cell_size,
                           FIELD_X + (x + 0.5) * self.cell_size, FIELD_Y + (y + 0.9) * self.cell_size, width=3)
        canvas.create_line(FIELD_X + (x + 0.1) * self.cell_size, FIELD_Y + (y + 0.5) * self.cell_size,
                           FIELD_X + (x + 0.9) * self.cell_size, FIELD_Y + (y + 0.5) * self.cell_size, width=3)

    def set_bind(self):
        canvas.bind("<Button-1>", self.left_clicked)
        canvas.bind("<Button-3>", self.right_clicked)

    def left_clicked(self, event):
        x = (event.x - FIELD_X) // self.cell_size
        y = (event.y - FIELD_Y) // self.cell_size
        if x < 0 or self.row <= x or y < 0 or self.column <= y:
            return
        self.main.clicked(x, y, LEFT)

    def right_clicked(self, event):
        x = (event.x - FIELD_X) // self.cell_size
        y = (event.y - FIELD_Y) // self.cell_size
        if x < 0 or self.row <= x or y < 0 or self.column <= y:
            return
        self.main.clicked(x, y, RIGHT)

    def mainloop(self):
        tk.mainloop()
