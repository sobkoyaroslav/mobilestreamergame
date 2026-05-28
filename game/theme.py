# -*- coding: utf-8 -*-
# Палитра и шрифты интерфейса.
#
# Тёмная тема с фиолетовым акцентом — в общей стилистике стриминговых
# сервисов. Это намеренно дженерик-оформление: здесь нет ничьих логотипов,
# названий и точных брендовых цветов, поэтому к авторским правам вопросов нет.

# --- Фоны ---
BG_DARK = "#1b1b22"      # фон главного окна
BG_PANEL = "#26262e"     # фон панелей и блоков
BG_ELEVATED = "#30303a"  # фон кнопок и приподнятых элементов
BG_AFFORD = "#3d3357"    # фон кнопки улучшения, когда покупку можно позволить

# --- Акцент (фиолетовый) ---
ACCENT = "#8b5cf6"        # основной акцентный цвет
ACCENT_HOVER = "#a78bfa"  # подсветка при наведении/нажатии
ACCENT_DARK = "#6d3fd6"   # затемнённый акцент

# --- Текст ---
TEXT = "#efeff1"      # основной текст
TEXT_DIM = "#adadb8"  # приглушённый, второстепенный текст

# --- Смысловые цвета ---
GOOD = "#3ba55d"      # успех, «получено», обычный доход
CRIT = "#f0b232"      # вирусный момент (критический удар)
LIVE = "#eb0400"      # индикатор «в эфире»
TOAST_BG = "#3a3a44"  # фон всплывающего уведомления

# --- Шрифт ---
FONT = "Segoe UI"


# Приводит обычную tk.Button к тёмному стилю темы.
# При accent=True кнопка делается фиолетовой (для главных действий).
def style_button(btn, accent=False):
    if accent:
        btn.configure(bg=ACCENT, fg=TEXT, activebackground=ACCENT_HOVER,
                      activeforeground=TEXT, relief="flat", borderwidth=0,
                      cursor="hand2")
    else:
        btn.configure(bg=BG_ELEVATED, fg=TEXT, activebackground=ACCENT_DARK,
                      activeforeground=TEXT, relief="flat", borderwidth=0,
                      cursor="hand2")
