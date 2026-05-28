# -*- coding: utf-8 -*-
# Определение путей к файлам: данные и встроенные ресурсы.
#
# Это важно для сборки через PyInstaller: при запуске собранного --onefile
# .exe код распаковывается во временную папку, которая удаляется при выходе.
# Поэтому изменяемые файлы (сохранение, звуки) нужно класть рядом с .exe,
# а встроенные ресурсы (иконка) — искать в распакованной временной папке.

import os
import sys


# Папка, в которую игра кладёт сохранение и звуковые файлы.
# Для собранного .exe (PyInstaller выставляет sys.frozen) — папка с .exe,
# чтобы данные не терялись между запусками. При обычном запуске из исходников
# — корень проекта (на уровень выше пакета game).
def data_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Путь к встроенному ресурсу (например, к иконке окна).
# Для собранного .exe PyInstaller распаковывает ресурсы во временную папку
# и кладёт её путь в sys._MEIPASS. При обычном запуске ресурс ищется в
# корне проекта.
def resource_path(name):
    if getattr(sys, "frozen", False):
        return os.path.join(getattr(sys, "_MEIPASS", ""), name)
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), name)
