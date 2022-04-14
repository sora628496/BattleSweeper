import random
from src.Screen import Screen, Log

# ====================================================================================================================
CLOSE = 0
OPEN = 1
LOCK = 2
EXPLODED = -1

ROW = 10  # 32以上だと対応する記号が無くなります
COLUMN = 10

BOMB_COUNT = round(ROW * COLUMN * 0.2)

LEFT = 0
RIGHT = 1

EXPLODE_PENALTY = 30
MISS_PENALTY = 5


def out_of_field(x, y):
    return x < 0 or ROW <= x or y < 0 or COLUMN <= y


# ====================================================================================================================

class Cell:
    x: int
    y: int
    state: int
    bomb: bool
    count: int
    player_num: int

    field: list

    def __init__(self, x, y, field):
        self.x = x
        self.y = y
        self.state = CLOSE
        self.bomb = False
        self.count = 0
        self.player_num = 0

        self.field = field

    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state

    def set_player_num(self, player_num):
        self.player_num = player_num

    def is_bomb(self):
        return self.bomb

    def set_bomb(self):
        self.bomb = True

    def set_count(self, count):
        self.count = count

    def left_click(self, player_num):
        score = 0
        if self.state == CLOSE:
            if self.bomb:
                self.state = EXPLODED
                self.player_num = player_num
                self.draw()
                main.explode()
            else:
                score = self.open(player_num)
                # print(score)
        elif self.state == OPEN:
            score = self.number_open(player_num)
            if score == -1:
                return
        else:
            return
        main.calc_score(score, player_num)
        main.change_turn()

    def right_click(self, player_num):
        self.lock(player_num)

    # マス開け関数(閉じたマスに対して呼ばれる前提)
    def open(self, player_num):
        self.state = OPEN
        self.player_num = player_num
        self.draw()
        score = 1
        # 0開け
        if self.count == 0:
            for b in range(-1, 2):
                for a in range(-1, 2):
                    if out_of_field(self.x + a, self.y + b): continue
                    if self.field[self.y + b][self.x + a].get_state() == CLOSE:
                        score += self.field[self.y + b][self.x + a].open(player_num)
        return score

    # 数字開け
    def number_open(self, player_num):
        score = 0
        lock_count = 0
        for b in range(-1, 2):
            for a in range(-1, 2):
                if out_of_field(self.x + a, self.y + b): continue
                state = self.field[self.y + b][self.x + a].get_state()
                if state == LOCK or state == EXPLODED:
                    lock_count += 1
        if self.count != lock_count:
            return -1
        for b in range(-1, 2):
            for a in range(-1, 2):
                if out_of_field(self.x + a, self.y + b): continue
                if self.field[self.y + b][self.x + a].get_state() == CLOSE:
                    cell = self.field[self.y + b][self.x + a]
                    if cell.is_bomb():
                        cell.set_state(EXPLODED)
                        cell.set_player_num(player_num)
                        cell.draw()
                        main.explode()
                    else:
                        score += cell.open(player_num)
        return score

    # ロック関数
    def lock(self, player_num):
        if self.state == CLOSE:
            self.state = LOCK
            self.player_num = player_num
            self.draw()
            main.lock()
            main.calc_score(1, player_num)
        elif self.state == LOCK:
            if self.player_num == player_num:
                self.state = CLOSE
                self.draw()
                main.unlock()
                main.calc_score(-1, player_num)
        elif self.state == OPEN:
            self.number_lock(player_num)

    # 数字ロック
    def number_lock(self, player_num):
        close_count = 0
        for b in range(-1, 2):
            for a in range(-1, 2):
                if out_of_field(self.x + a, self.y + b): continue
                state = self.field[self.y + b][self.x + a].get_state()
                if state == CLOSE or state == LOCK or state == EXPLODED:
                    close_count += 1
        if self.count != close_count: return
        for b in range(-1, 2):
            for a in range(-1, 2):
                if out_of_field(self.x + a, self.y + b): continue
                if self.field[self.y + b][self.x + a].get_state() == CLOSE:
                    self.field[self.y + b][self.x + a].lock(player_num)

    def check_lock_miss(self):
        return self.state == LOCK and not self.bomb

    def draw(self):
        if self.state == OPEN:
            screen.draw_open(self.x, self.y, self.count, self.player_num)
        elif self.state == CLOSE:
            screen.draw_close(self.x, self.y)
        elif self.state == LOCK:
            screen.draw_lock(self.x, self.y, self.player_num)
        elif self.state == EXPLODED:
            screen.draw_bomb(self.x, self.y, self.player_num)


class Main:
    def __init__(self):
        self.field = []
        self.turn = 1
        self.remain_bomb = 0
        self.point1 = 0
        self.point2 = 0
        self.is_first = True
        self.pass_count = 0

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
                line.append(Cell(x, y, self.field))
            self.field.append(line)
        self.draw()

    def change_turn(self, pass_turn=False):
        self.miss_check()
        if not pass_turn:
            self.check_clear()
            self.pass_count = 0
        if self.turn == 1:
            self.turn = 2
        elif self.turn == 2:
            self.turn = 1
        screen.draw_turn(self.turn)

    def calc_score(self, score, player_num):
        if player_num == 1:
            self.point1 += score
            screen.draw_score(self.turn, self.point1)
        elif player_num == 2:
            self.point2 += score
            screen.draw_score(self.turn, self.point2)

    def set_bombs(self, x0, y0):
        # 爆弾の位置決め
        lis = []
        for y in range(COLUMN):
            for x in range(ROW):
                if x0 - 1 <= x <= x0 + 1 and y0 - 1 <= y <= y0 + 1:
                    # if x == x0 and y == y0:
                    continue
                lis.append([x, y])
        random.shuffle(lis)
        for i in range(BOMB_COUNT):
            pos = lis.pop()
            self.field[pos[1]][pos[0]].set_bomb()

        # 各マス周囲の爆弾の数を数える
        for y in range(COLUMN):
            for x in range(ROW):
                count = 0
                for b in range(-1, 2):
                    for a in range(-1, 2):
                        if a == 0 and b == 0: continue
                        if out_of_field(x + a, y + b): continue
                        if self.field[y + b][x + a].is_bomb():
                            count += 1
                self.field[y][x].set_count(count)

    def miss_check(self):
        for y in range(len(self.field)):
            for x in range(len(self.field[0])):
                if self.field[y][x].check_lock_miss():
                    if self.turn == 1:
                        self.point1 -= MISS_PENALTY
                        screen.draw_score(self.turn, self.point1)
                    if self.turn == 2:
                        self.point2 -= MISS_PENALTY
                        screen.draw_score(self.turn, self.point2)
                    screen.draw_text(Log.MISS_LOCK, self.turn, MISS_PENALTY, x, y)
                    self.field[y][x].lock(self.turn)
                    self.field[y][x].open(0)

    def check_clear(self):
        is_clear = True
        for line in self.field:
            for cell in line:
                if (cell.get_state() == CLOSE or cell.get_state() == LOCK) and not cell.is_bomb():
                    is_clear = False
        if not is_clear:
            return
        if self.point1 > self.point2:
            screen.draw_text(Log.WIN, 1)
        elif self.point1 < self.point2:
            screen.draw_text(Log.WIN, 2)
        elif self.point1 == self.point2:
            screen.draw_text(Log.DRAW, 0)

    def lock(self):
        self.remain_bomb -= 1
        screen.draw_bomb_count(self.remain_bomb)

    def unlock(self):
        self.remain_bomb += 1
        screen.draw_bomb_count(self.remain_bomb)

    def explode(self):
        self.lock()
        if self.turn == 1:
            self.point1 -= EXPLODE_PENALTY
        if self.turn == 2:
            self.point2 -= EXPLODE_PENALTY
        screen.draw_text(Log.EXPLODE, self.turn, EXPLODE_PENALTY)

    def pass_turn(self):
        self.pass_count += 1
        screen.draw_text(Log.PASS, self.turn)
        if self.pass_count < 2 or self.is_first:
            self.change_turn(True)
            return
        screen.draw_text(Log.AUTO_OPEN)
        self.pass_count = 0
        lis = []
        for y in range(COLUMN):
            for x in range(ROW):
                if self.field[y][x].get_state() == CLOSE and not self.field[y][x].is_bomb():
                    is_edge = False
                    for b in range(-1, 2):
                        for a in range(-1, 2):
                            if a == 0 and b == 0: continue
                            if out_of_field(x + a, y + b): continue
                            if self.field[y + b][x + a].get_state() == OPEN:
                                is_edge = True
                                lis.append([x, y])
                                break
                        if is_edge:
                            break
        if not lis:
            for y in range(COLUMN):
                for x in range(ROW):
                    if self.field[y][x].get_state() == CLOSE and not self.field[y][x].is_bomb():
                        lis.append([x, y])
        random.shuffle(lis)
        pos = lis.pop()
        self.field[pos[1]][pos[0]].left_click(0)

    def retry(self):
        self.initialize()

    def draw(self):
        for line in self.field:
            for cell in line:
                cell.draw()

    def clicked(self, x, y, type):
        if type == LEFT:
            if self.is_first:
                self.is_first = False
                self.set_bombs(x, y)
                self.field[y][x].left_click(0)
            self.field[y][x].left_click(self.turn)
        elif type == RIGHT:
            self.field[y][x].right_click(self.turn)


screen = Screen(ROW, COLUMN, BOMB_COUNT)

main = Main()

screen.set_main(main)

main.initialize()

screen.mainloop()
