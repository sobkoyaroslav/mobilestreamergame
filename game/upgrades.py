# -*- coding: utf-8 -*-
# Описание улучшений и логика их покупки.

from dataclasses import dataclass


# Одно улучшение: стоимость растёт в `growth` раз за каждый уровень.
@dataclass(frozen=True)
class Upgrade:
    key: str            # внутренний идентификатор
    title: str          # название для игрока
    description: str    # что даёт улучшение
    base_cost: int      # стоимость первого уровня
    growth: float       # во сколько раз дорожает следующий уровень


# Полный список улучшений (тематика — раскрутка канала стримера).
UPGRADES = [
    Upgrade("click", "Харизма",
            "+1 фолловер за каждый стрим", 25, 1.5),
    Upgrade("auto", "Нарезки клипов",
            "+1 фолловер в секунду автоматически", 120, 1.6),
    Upgrade("multiplier", "Рекламная кампания",
            "+25% ко всем фолловерам", 600, 2.0),
    Upgrade("crit", "Вирусный момент",
            "+5% к шансу собрать x5 фолловеров за стрим", 300, 1.8),
]

# Быстрый доступ к улучшению по его ключу.
_BY_KEY = {u.key: u for u in UPGRADES}


# Возвращает объект улучшения по ключу.
def get(key):
    return _BY_KEY[key]


# Текущий уровень улучшения у игрока (0, если ещё не куплено).
def level(state, key):
    return state.upgrade_levels.get(key, 0)


# Стоимость покупки следующего уровня улучшения.
def cost(state, key):
    up = _BY_KEY[key]
    return int(up.base_cost * (up.growth ** level(state, key)))


# Хватает ли у игрока фолловеров на следующий уровень.
def can_afford(state, key):
    return state.coins >= cost(state, key)


# Покупает следующий уровень улучшения. Возвращает True при успехе.
def buy(state, key):
    price = cost(state, key)
    if state.coins < price:
        return False
    state.coins -= price
    state.upgrade_levels[key] = level(state, key) + 1
    return True
