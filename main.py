import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler
import random
from enum import auto, Enum
from textwrap import dedent
from typing import Iterable, Optional

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


class GameStatus(Enum):
    PLAYING = auto()
    LOSE = auto()
    WIN = auto()


class MineBoard:
    status: GameStatus = GameStatus.PLAYING
    w: int
    h: int
    board: list[list[int]]
    cells_to_open: int

    def __init__(self, w: int, h: int, k: int) -> None:
        self.w = w
        self.h = h
        self.board = [[0 for _ in range(w)] for _ in range(h)]
        self.allocate_mines(w, h, k)
        self.cells_to_open = w * h - k

    def allocate_mines(self, w: int, h: int, num_of_mines: int) -> None:
        alloc_indexes = self.get_random_pos(w * h, num_of_mines)
        for i in alloc_indexes:
            self.set_mine(int(i / w), i % h)
            self.set_adjacent_mines(int(i / w), i % h)

    def prnt(self):
        return "\n".join(
            [
                " " * 7 + "".join(map(lambda x: "{:^7d}".format(x + 1), range(self.w))),
                " " * 7 + "-" * (self.w * 7),
                "\n".join(
                    (
                            "{:^7d}".format(i + 1)
                            + "|"
                            + " |".join(
                        list(map(lambda x: "{:^5s}".format(self.display(x)), row))
                    )
                            + " | "
                    )
                    + "\n"
                    + (" " * 7 + "-" * (self.w * 7))
                    for (i, row) in enumerate(self.board)
                ),
            ]
        )

    def click(self, row: int, col: int) -> None:
        value = self.reveal(row, col)
        if value:
            self.cells_to_open -= 1
            if self.cells_to_open == 0:
                self.status = GameStatus.WIN
            if self.has_mine(row, col):
                self.status = GameStatus.LOSE
            elif self.is_blank(row, col):
                for dr in range(row - 1, row + 2):
                    for dc in range(col - 1, col + 2):
                        self.click(dr, dc)

    def flag(self, row: int, col: int) -> None:
        if self.is_valid_cell(row, col) and self.is_hidden(row, col):
            self.toggle_flag(row, col)

    def is_valid_cell(self, row: int, col: int) -> bool:
        return 0 <= row < self.h and 0 <= col < self.w

    def get_random_pos(self, n: int, k: int) -> Iterable[int]:
        res: list[int] = []
        remains = list(range(n))
        while k > 0:
            r = random.randint(0, len(remains) - 1)
            res.append(r)
            del remains[r]
            k -= 1
        return res

    def set_mine(self, row: int, col: int) -> None:
        self.board[row][col] = -1

    def set_adjacent_mines(self, row: int, col: int) -> None:
        for dr in range(row - 1, row + 2):
            for dc in range(col - 1, col + 2):
                if self.is_valid_cell(dr, dc) and not self.has_mine(dr, dc):
                    self.board[dr][dc] += 1

    def toggle_flag(self, row: int, col: int) -> None:
        if self.is_flagged(row, col):
            self.board[row][col] -= 100
        else:
            self.board[row][col] += 100

    def reveal(self, row: int, col: int) -> Optional[int]:
        if not self.is_valid_cell(row, col) or not self.is_hidden(row, col):
            return None
        if self.is_flagged(row, col):
            self.toggle_flag(row, col)
        self.board[row][col] += 10
        return self.board[row][col]

    def is_hidden(self, row: int, col: int) -> bool:
        return self.board[row][col] < 9

    def has_mine(self, row: int, col: int) -> bool:
        return self.board[row][col] % 10 == 9

    def is_blank(self, row: int, col: int) -> bool:
        return self.board[row][col] % 10 == 0

    def is_over(self) -> bool:
        return self.win_game() or self.lose_game()

    def lose_game(self) -> bool:
        return self.status == GameStatus.LOSE

    def win_game(self) -> bool:
        return self.status == GameStatus.WIN

    def is_flagged(self, row: int, col: int) -> bool:
        return self.board[row][col] > 90

    def reveal_all(self) -> None:
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                self.reveal(i, j)

    def display(self, ip: int) -> str:
        if ip > 90:
            return "F"
        if ip == 9:
            return "*"
        if ip == 10:
            return "."
        if ip > 10:
            return str(ip - 10)
        return ""


game = MineBoard(0, 0, 0)



async def echo(update, context):
    global game
    if (len(update.message.text.split()) == 3 and update.message.text.split()[2] != "F"):
        w = update.message.text.split()[0]
        h = update.message.text.split()[1]
        m = update.message.text.split()[2]
        game = MineBoard(int(w), int(h), int(m))
        await update.message.reply_text(game.prnt())
        instruction = dedent(
            """\
                Команды :
                <номер строки> <номер столбца> : открыть клетку
                <номер строки> <номер столбца> F : поставить флаг
            """
        )
        await update.message.reply_text(instruction)
    else:
        if game.lose_game() or game.win_game():
            return
        splits = update.message.text.split()
        row = int(splits[0]) - 1
        col = int(splits[1]) - 1
        if len(splits) == 3:
            game.flag(row, col)
        else:
            game.click(row, col)
        await update.message.reply_text(game.prnt())
        if game.lose_game():
            await update.message.reply_text("Вы проиграли. Чтобы начать заново напишите /start")
        elif game.win_game():
            await update.message.reply_text("Вы выйграли! Чтобы начать заново напишите /start")


async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я сапер-бот. Давай сыграем.",
    )
    await update.message.reply_html(
        rf"Напиши через пробел ширину, высоту поля, а так же количество мин.",
    )


def main():
    application = Application.builder().token('7198355333:AAFr3otTLwGM-OOmZ5K_Vs1Y4SH5aTToWXk').build()
    application.add_handler(CommandHandler("start", start))
    text_handler = MessageHandler(filters.TEXT, echo)
    application.add_handler(text_handler)
    application.run_polling()

if __name__ == "__main__":
    main()