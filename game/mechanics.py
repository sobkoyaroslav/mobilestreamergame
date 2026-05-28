# -*- coding: utf-8 -*-
# Игровые расчёты: доход за стрим, пассивный доход, вирусные моменты.

import random

from . import upgrades

# Во сколько раз вирусный момент увеличивает доход со стрима.
CRIT_MULTIPLIER = 5

# Максимальный шанс вирусного момента, чтобы игра не ломалась на больших уровнях.
MAX_CRIT_CHANCE = 0.75


# Общий множитель всего дохода (улучшение «Рекламная кампания»).
def global_multiplier(state):
    return 1.0 + 0.25 * upgrades.level(state, "multiplier")


# Доход за один обычный стрим с учётом множителя.
def click_power(state):
    base = 1 + upgrades.level(state, "click")
    return base * global_multiplier(state)


# Пассивный доход в секунду от нарезок клипов.
def auto_income(state):
    return upgrades.level(state, "auto") * global_multiplier(state)


# Шанс вирусного момента (ограничен сверху значением MAX_CRIT_CHANCE).
def crit_chance(state):
    return min(0.05 * upgrades.level(state, "crit"), MAX_CRIT_CHANCE)


# Обрабатывает один стрим игрока.
# Меняет состояние и возвращает кортеж (доход, был_ли_вирусный_момент).
def do_click(state):
    gain = click_power(state)
    is_crit = random.random() < crit_chance(state)
    if is_crit:
        gain *= CRIT_MULTIPLIER
    state.coins += gain
    state.total_earned += gain
    state.total_clicks += 1
    return gain, is_crit


# Начисляет пассивный доход за одну секунду. Возвращает начисленный доход.
def do_auto_tick(state):
    gain = auto_income(state)
    if gain:
        state.coins += gain
        state.total_earned += gain
    return gain
