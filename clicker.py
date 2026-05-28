# -*- coding: utf-8 -*-
# Точка входа в игру «Поднятие стримера в одиночку».
#
# Запуск:  python clicker.py
#
# Вся игровая логика вынесена в пакет game/:
#   game/state.py        — состояние игры, сохранение и загрузка
#   game/upgrades.py     — улучшения и их покупка
#   game/mechanics.py    — расчёт дохода, вирусные моменты, пассивный доход
#   game/achievements.py — достижения и проверка их выполнения
#   game/sound.py        — синтез и воспроизведение звуков
#   game/theme.py        — палитра и шрифты тёмной темы
#   game/text.py         — склонение русских слов по числам
#   game/ui.py           — графический интерфейс на Tkinter

import tkinter as tk

from game.ui import ClickerUI


# Создаёт главное окно и запускает игровой цикл.
def main():
    root = tk.Tk()
    ClickerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
