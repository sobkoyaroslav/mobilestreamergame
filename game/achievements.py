# -*- coding: utf-8 -*-
# Достижения и проверка их выполнения.

from dataclasses import dataclass
from typing import Callable

from . import mechanics, upgrades


# Достижение: разблокируется, когда condition от состояния вернёт True.
@dataclass(frozen=True)
class Achievement:
    id: str
    title: str
    description: str
    condition: Callable


# Список всех достижений. Порядок важен: «Топовый стример» проверяется
# последним, поэтому к моменту его проверки остальные уже разблокированы.
ACHIEVEMENTS = [
    Achievement("first_click", "Первый стрим",
                "Провести первый стрим",
                lambda s: s.total_clicks >= 1),
    Achievement("clicks_100", "Регулярный стример",
                "Провести 100 стримов",
                lambda s: s.total_clicks >= 100),
    Achievement("clicks_1000", "Ветеран эфира",
                "Провести 1000 стримов",
                lambda s: s.total_clicks >= 1000),
    Achievement("rich", "Первая тысяча",
                "Набрать 1 000 фолловеров за всё время",
                lambda s: s.total_earned >= 1_000),
    Achievement("very_rich", "Знаменитость",
                "Набрать 100 000 фолловеров за всё время",
                lambda s: s.total_earned >= 100_000),
    Achievement("hoarder", "Армия фанатов",
                "Иметь 10 000 фолловеров одновременно",
                lambda s: s.coins >= 10_000),
    Achievement("auto_on", "Первый клип",
                "Купить «Нарезки клипов»",
                lambda s: upgrades.level(s, "auto") >= 1),
    Achievement("auto_10", "Контент-машина",
                "Прокачать «Нарезки клипов» до 10 уровня",
                lambda s: upgrades.level(s, "auto") >= 10),
    Achievement("click_10", "Мастер харизмы",
                "Прокачать «Харизму» до 10 уровня",
                lambda s: upgrades.level(s, "click") >= 10),
    Achievement("crit_master", "Король хайпа",
                "Поднять шанс вирусного момента до 25%",
                lambda s: mechanics.crit_chance(s) >= 0.25),
    Achievement("multi", "Маркетолог",
                "Купить «Рекламную кампанию»",
                lambda s: upgrades.level(s, "multiplier") >= 1),
    Achievement("collector", "Топовый стример",
                "Получить все остальные достижения",
                lambda s: all(a.id in s.unlocked
                              for a in ACHIEVEMENTS if a.id != "collector")),
]


# Общее количество достижений в игре.
def total():
    return len(ACHIEVEMENTS)


# Проверяет условия и разблокирует выполненные достижения.
# Возвращает список достижений, полученных именно сейчас.
def check(state):
    newly = []
    for ach in ACHIEVEMENTS:
        if ach.id not in state.unlocked and ach.condition(state):
            state.unlocked.append(ach.id)
            newly.append(ach)
    return newly
