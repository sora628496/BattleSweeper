"""
バトルスイーパー(2人対戦型マインスイーパー)

"""

import random
from src.Screen import Screen, Log
from src.Cell import Cell, State, Command

# ====================================================================================================================
ROW = 30  # 32以上だと対応する記号が無くなります
COLUMN = 30

BOMB_COUNT = round(ROW * COLUMN * 0.2)

EXPLODE_PENALTY = 30
MISS_PENALTY = 5


# 範囲外判定
def out_of_field(x, y):
    return x < 0 or ROW <= x or y < 0 or COLUMN <= y


# ====================================================================================================================


class Main:
    def __init__(self):
        self.field = []
        self.turn = 1
        self.remain_bomb = 0
        self.point1 = 0
        self.point2 = 0
        self.is_first = True
        self.pass_count = 0

    # 初期化関数
    def initialize(self):
        screen.reset()
        screen.set_bind()
        self.turn = 1
        self.remain_bomb = BOMB_COUNT
        self.point1 = 0
        self.point2 = 0
        self.is_first = True
        self.pass_count = 0

        self.field = []
        for y in range(COLUMN):
            line = []
            for x in range(ROW):
                line.append(Cell(x, y, screen))
            self.field.append(line)
        self.draw()

    # 手番交代処理
    def change_turn(self, pass_turn=False):
        # ミスロックのチェック
        for y in range(COLUMN):
            for x in range(ROW):
                if self.field[y][x].check_lock_miss():
                    self.miss_lock(x, y, self.turn)
        if not pass_turn:
            self.check_clear()
            self.pass_count = 0
        if self.turn == 1:
            self.turn = 2
        elif self.turn == 2:
            self.turn = 1
        screen.draw_turn(self.turn)

    # スコア処理
    def gain_score(self, player_num, score):
        if player_num == 1:
            self.point1 += score
            screen.draw_score(player_num, self.point1)
        elif player_num == 2:
            self.point2 += score
            screen.draw_score(player_num, self.point2)

    # 地雷の位置を決めて設置
    def set_bombs(self, x0, y0):
        # 爆弾の位置決め
        lis = []
        for y in range(COLUMN):
            for x in range(ROW):
                # if x == x0 and y == y0:# 最初にクリックした位置だけ地雷無しにしたいとき
                if x0 - 1 <= x <= x0 + 1 and y0 - 1 <= y <= y0 + 1:
                    continue
                lis.append([x, y])
        random.shuffle(lis)
        for i in range(BOMB_COUNT):
            pos = lis.pop()
            self.field[pos[1]][pos[0]].set_bomb()
        self.set_counts()

    # 各マス周囲の爆弾の数を数えて設定
    def set_counts(self):
        for y in range(COLUMN):
            for x in range(ROW):
                if self.field[y][x].is_bomb():
                    self.field[y][x].set_count(-1)
                    continue
                count = 0
                for b in range(-1, 2):
                    for a in range(-1, 2):
                        if a == 0 and b == 0:
                            continue
                        if out_of_field(x + a, y + b):
                            continue
                        if self.field[y + b][x + a].is_bomb():
                            count += 1
                self.field[y][x].set_count(count)

    # クリア(地雷が無いマスが全て開いているか)チェック
    def check_clear(self):
        is_clear = True
        for y in range(COLUMN):
            for x in range(ROW):
                if self.field[y][x].is_not_confirm():
                    is_clear = False
        if not is_clear:
            return
        if self.point1 > self.point2:
            screen.draw_text(Log.WIN, 1)
        elif self.point1 < self.point2:
            screen.draw_text(Log.WIN, 2)
        elif self.point1 == self.point2:
            screen.draw_text(Log.DRAW, 0)

    # 地雷爆発時の処理
    def explode(self, player_num):
        self.remain_bomb -= 1
        screen.draw_bomb_count(self.remain_bomb)
        self.gain_score(player_num, -EXPLODE_PENALTY)
        screen.draw_text(Log.EXPLODE, player_num, EXPLODE_PENALTY)

    # ミスロック処理
    def miss_lock(self, x, y, player_num):
        self.gain_score(player_num, -MISS_PENALTY)
        screen.draw_text(Log.MISS_LOCK, player_num, MISS_PENALTY, x, y)
        self.cell_lock(x, y, player_num)
        self.command_open(x, y, player_num)

    # パスの処理
    def pass_turn(self):
        self.pass_count += 1
        screen.draw_text(Log.PASS, self.turn)
        if self.pass_count < 2 or self.is_first:
            self.change_turn(True)
        else:
            self.auto_open()

    # 2連パス時の自動開けの処理
    def auto_open(self):
        screen.draw_text(Log.AUTO_OPEN)
        self.pass_count = 0
        lis = []
        for y in range(COLUMN):
            for x in range(ROW):
                if self.field[y][x].get_state() == State.CLOSE and not self.field[y][x].is_bomb():
                    # 開いてるマスに隣接したマスをlisに集める
                    is_edge = False
                    for b in range(-1, 2):
                        for a in range(-1, 2):
                            if a == 0 and b == 0:
                                continue
                            if out_of_field(x + a, y + b):
                                continue
                            if self.field[y + b][x + a].get_state() == State.OPEN:
                                is_edge = True
                                break
                        if is_edge:
                            break
                    if is_edge:
                        lis.append([x, y])
        # 開いてるマスに隣接するマスが全て地雷入りなら地雷が入っていないマスを全てlisに集める
        if not lis:
            for y in range(COLUMN):
                for x in range(ROW):
                    if self.field[y][x].get_state() == State.CLOSE and not self.field[y][x].is_bomb():
                        lis.append([x, y])
        # 地雷が無いマスが全て開いているとき(決着後)
        if not lis:
            return
        random.shuffle(lis)
        pos = lis.pop()
        self.command_open(pos[0], pos[1], 0)

    def draw(self):
        for line in self.field:
            for cell in line:
                cell.draw()

    # やり直しボタンで呼ばれる
    def retry(self):
        self.initialize()

    # 画面クリックで呼ばれる(x, yはクリックされたマスの座標)
    def left_clicked(self, x, y):
        player_num = self.turn
        if self.is_first:
            self.is_first = False
            self.set_bombs(x, y)
            player_num = 0
        cell_opened = self.command_open(x, y, player_num)
        if cell_opened:
            self.change_turn()

    # 画面右クリックで呼ばれる(x, yはクリックされたマスの座標)
    def right_clicked(self, x, y):
        command = self.field[y][x].check_lock_command(self.turn)
        if command == Command.NUMBER_LOCK:
            self.number_lock(x, y, self.turn)
        elif command == Command.OPPONENT_LOCK:
            pass
        elif command == Command.NORMAL:
            self.cell_lock(x, y, self.turn)

    # 特殊開け処理
    def command_open(self, x, y, player_num):
        command = self.field[y][x].check_open_command()
        if command == Command.ZERO_OPEN:
            self.zero_open(x, y, player_num)
            return True
        elif command == Command.NUMBER_OPEN:
            cell_opened = self.number_open(x, y)
            return cell_opened
        elif command == Command.NORMAL:
            self.cell_open(x, y, player_num)
            return True
        else:
            return False

    # 通常のマス開け
    def cell_open(self, x, y, player_num):
        explode = self.field[y][x].open(player_num)
        if explode:
            self.explode(player_num)
        else:
            self.gain_score(player_num, 1)

    # 範囲開け
    def number_open(self, x, y):
        cell_opened = False
        lock_count = 0
        for b in range(-1, 2):
            for a in range(-1, 2):
                if out_of_field(x + a, y + b):
                    continue
                state = self.field[y + b][x + a].get_state()
                if state == State.LOCK or state == State.EXPLODED:
                    lock_count += 1
        if self.field[y][x].get_count() != lock_count:
            return False
        for b in range(-1, 2):
            for a in range(-1, 2):
                if out_of_field(x + a, y + b):
                    continue
                if self.field[y + b][x + a].get_state() == State.CLOSE:
                    self.command_open(x + a, y + b, self.turn)
                    cell_opened = True
        return cell_opened

    # 0開け
    def zero_open(self, x, y, player_num):
        for b in range(-1, 2):
            for a in range(-1, 2):
                if out_of_field(x + a, y + b):
                    continue
                if self.field[y + b][x + a].get_state() == State.CLOSE:
                    command = self.field[y + b][x + a].check_open_command()
                    self.cell_open(x + a, y + b, player_num)
                    if command == Command.ZERO_OPEN:
                        self.zero_open(x + a, y + b, player_num)

    # 通常のロック
    def cell_lock(self, x, y, player_num):
        locked = self.field[y][x].lock(player_num)
        if locked:
            self.remain_bomb -= 1
            screen.draw_bomb_count(self.remain_bomb)
            self.gain_score(player_num, 1)
        else:
            self.remain_bomb += 1
            screen.draw_bomb_count(self.remain_bomb)
            self.gain_score(player_num, -1)

    # 範囲ロック
    def number_lock(self, x, y, player_num):
        close_count = 0
        for b in range(-1, 2):
            for a in range(-1, 2):
                if out_of_field(x + a, y + b):
                    continue
                state = self.field[y + b][x + a].get_state()
                if state == State.CLOSE or state == State.LOCK or state == State.EXPLODED:
                    close_count += 1
        if self.field[y][x].get_count() != close_count:
            return
        for b in range(-1, 2):
            for a in range(-1, 2):
                if out_of_field(x + a, y + b):
                    continue
                if self.field[y + b][x + a].get_state() == State.CLOSE:
                    self.cell_lock(x + a, y + b, player_num)


screen = Screen(ROW, COLUMN, BOMB_COUNT)

main = Main()

screen.set_main(main)

main.initialize()

screen.mainloop()
