import random
import tkinter as tk
from datetime import datetime

SETS = 5
NUMBERS_PER_SET = 6
MAX_NUMBER = 45

# 번호 구간별 색상 (동행복권 공 색상 기준)
COLOR_RANGES = [
    (10, "#fbc400"),  # 1~10 노랑
    (20, "#69c8f2"),  # 11~20 파랑
    (30, "#ff7272"),  # 21~30 빨강
    (40, "#aaaaaa"),  # 31~40 회색
    (45, "#b0d840"),  # 41~45 초록
]


def ball_color(number):
    for limit, color in COLOR_RANGES:
        if number <= limit:
            return color
    return "#aaaaaa"


def draw_sets():
    return [
        sorted(random.sample(range(1, MAX_NUMBER + 1), NUMBERS_PER_SET))
        for _ in range(SETS)
    ]


class LottoApp:
    def __init__(self, root):
        self.root = root
        root.title("로또 번호 생성기")
        root.resizable(False, False)

        self.date_label = tk.Label(root, font=("맑은 고딕", 11))
        self.date_label.pack(pady=(12, 4))

        self.board = tk.Frame(root)
        self.board.pack(padx=20, pady=8)

        tk.Button(
            root,
            text="번호 생성",
            font=("맑은 고딕", 12, "bold"),
            command=self.generate,
        ).pack(pady=(4, 14))

        self.generate()

    def generate(self):
        self.date_label.config(
            text=datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S")
        )

        for child in self.board.winfo_children():
            child.destroy()

        for row, numbers in enumerate(draw_sets()):
            tk.Label(
                self.board, text=f"{chr(65 + row)}", font=("맑은 고딕", 11, "bold")
            ).grid(row=row, column=0, padx=(0, 10), pady=4)
            for col, number in enumerate(numbers, start=1):
                tk.Label(
                    self.board,
                    text=str(number),
                    width=3,
                    font=("맑은 고딕", 12, "bold"),
                    bg=ball_color(number),
                    fg="white",
                ).grid(row=row, column=col, padx=3, pady=4)


if __name__ == "__main__":
    root = tk.Tk()
    LottoApp(root)
    root.mainloop()
