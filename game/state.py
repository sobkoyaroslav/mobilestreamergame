# -*- coding: utf-8 -*-
# Состояние игры и его сохранение/загрузка в JSON-файл.

import json
import os
from dataclasses import asdict, dataclass, field

from .paths import data_dir

# Путь к файлу сохранения. Папку выбирает data_dir(): корень проекта при
# обычном запуске или папка рядом с .exe для собранной версии.
SAVE_FILE = os.path.join(data_dir(), "clicker_save.json")


# Всё, что нужно знать об игре, чтобы продолжить её после перезапуска.
@dataclass
class GameState:
    coins: float = 0.0            # текущие фолловеры
    total_earned: float = 0.0     # сколько фолловеров набрано за всё время
    total_clicks: int = 0         # сколько стримов проведено за всё время
    upgrade_levels: dict = field(default_factory=dict)  # ключ улучшения -> уровень
    unlocked: list = field(default_factory=list)        # id полученных достижений
    muted: bool = False           # выключен ли звук


# Записывает состояние игры в JSON-файл.
def save(state):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(asdict(state), f, ensure_ascii=False, indent=2)


# Читает состояние из файла. Если файла нет или он повреждён — новая игра.
def load():
    if not os.path.exists(SAVE_FILE):
        return GameState()
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return GameState(
            coins=float(data.get("coins", 0.0)),
            total_earned=float(data.get("total_earned", 0.0)),
            total_clicks=int(data.get("total_clicks", 0)),
            upgrade_levels={str(k): int(v)
                            for k, v in data.get("upgrade_levels", {}).items()},
            unlocked=list(data.get("unlocked", [])),
            muted=bool(data.get("muted", False)),
        )
    except (json.JSONDecodeError, ValueError, TypeError, OSError):
        # Файл повреждён — не падаем, а начинаем заново.
        return GameState()


# Удаляет файл сохранения (используется при сбросе прогресса).
def delete_save():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
