"""
マスを表すクラス
マスの処理はここでしている
"""

from enum import Enum, auto
from src.Screen import Screen


# 各マスの状態を表す
class State(Enum):
    CLOSE = auto()
    OPEN = auto()
    LOCK = auto()
    EXPLODED = auto()


# マス開け/ロックの種類を表す
class Command(Enum):
    ZERO_OPEN = auto()
    NUMBER_OPEN = auto()
    NUMBER_LOCK = auto()
    OPPONENT_LOCK = auto()
    NORMAL = auto()
    NONE = auto()


class Cell:
    x: int
    y: int
    state: State
    bomb: bool
    count: int
    player_num: int
    screen: Screen

    def __init__(self, x, y, screen):
        self.x = x
        self.y = y
        self.state = State.CLOSE
        self.bomb = False
        self.count = 0
        self.player_num = 0
        self.screen = screen

    def get_state(self):
        return self.state

    def get_count(self):
        return self.count

    def is_bomb(self):
        return self.bomb

    def set_bomb(self):
        self.bomb = True

    def set_count(self, count):
        self.count = count

    def is_not_confirm(self):
        return (self.state == State.CLOSE or self.state == State.LOCK) and not self.bomb

    # マス開けの種類判定
    def check_open_command(self):
        if self.state == State.OPEN:
            return Command.NUMBER_OPEN
        elif self.state == State.CLOSE and self.count == 0:
            return Command.ZERO_OPEN
        elif self.state == State.CLOSE:
            return Command.NORMAL
        else:
            return Command.NONE

    # ロックの種類判定
    def check_lock_command(self, player_num):
        if self.state == State.OPEN:
            return Command.NUMBER_LOCK
        elif self.state == State.LOCK and self.player_num != player_num:
            return Command.OPPONENT_LOCK
        elif self.state == State.LOCK or self.state == State.CLOSE:
            return Command.NORMAL
        else:
            return Command.NONE

    # マス開け関数
    def open(self, player_num):
        exploded = False
        if self.bomb:
            self.state = State.EXPLODED
            exploded = True
        else:
            self.state = State.OPEN
        self.player_num = player_num
        self.draw()
        return exploded

    # ロック関数
    def lock(self, player_num):
        locked = True
        if self.state == State.CLOSE:
            self.state = State.LOCK
            self.player_num = player_num
            self.draw()
            locked = True
        elif self.state == State.LOCK:
            self.state = State.CLOSE
            self.draw()
            locked = False
        else:
            print(self.state)
        return locked

    # ミスロックしているか否か
    def check_lock_miss(self):
        return self.state == State.LOCK and not self.bomb

    # マスの描画関数
    def draw(self):
        if self.state == State.OPEN:
            self.screen.draw_open(self.x, self.y, self.count, self.player_num)
        elif self.state == State.CLOSE:
            self.screen.draw_close(self.x, self.y)
        elif self.state == State.LOCK:
            self.screen.draw_lock(self.x, self.y, self.player_num)
        elif self.state == State.EXPLODED:
            self.screen.draw_bomb(self.x, self.y, self.player_num)
