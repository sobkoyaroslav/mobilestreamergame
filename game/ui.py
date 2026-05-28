# -*- coding: utf-8 -*-
# Графический интерфейс игры на Tkinter.
#
# Класс ClickerUI связывает воедино состояние, механику, достижения и звук:
# строит окно, обрабатывает стримы и покупки, запускает таймер пассивного дохода.

import tkinter as tk
from tkinter import messagebox

from . import achievements, mechanics, paths, state, theme, upgrades
from .sound import SoundPlayer
from .text import followers

# Интервал начисления пассивного дохода, миллисекунды.
AUTO_TICK_MS = 1000


# Главное окно игры.
class ClickerUI:

    def __init__(self, root):
        self.root = root
        self.state = state.load()
        self.sound = SoundPlayer(muted=self.state.muted)

        self.root.title("Поднятие стримера в одиночку")
        self.root.geometry("460x720")
        self.root.resizable(False, False)
        self.root.configure(bg=theme.BG_DARK)

        # Иконка окна (если файл icon.ico доступен — рядом с игрой или внутри .exe).
        try:
            self.root.iconbitmap(paths.resource_path("icon.ico"))
        except tk.TclError:
            pass  # иконки нет — окно останется с иконкой по умолчанию

        self._upgrade_buttons = {}  # ключ улучшения -> кнопка покупки
        self._toast = None          # текущее всплывающее уведомление

        self._build_ui()
        self.refresh()

        # Сохранять прогресс при закрытии окна и запустить пассивный доход.
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(AUTO_TICK_MS, self._auto_loop)

    # ------------------------------------------------------------------
    # Построение интерфейса
    # ------------------------------------------------------------------

    # Создаёт все виджеты окна.
    def _build_ui(self):
        # --- Шапка: индикатор «в эфире» и название игры ---
        header = tk.Frame(self.root, bg=theme.BG_DARK)
        header.pack(pady=(14, 0))
        tk.Label(header, text="●", fg=theme.LIVE, bg=theme.BG_DARK,
                 font=(theme.FONT, 10)).pack(side="left")
        tk.Label(header, text=" В ЭФИРЕ", fg=theme.TEXT_DIM, bg=theme.BG_DARK,
                 font=(theme.FONT, 9, "bold")).pack(side="left")

        tk.Label(self.root, text="ПОДНЯТИЕ СТРИМЕРА В ОДИНОЧКУ",
                 fg=theme.ACCENT, bg=theme.BG_DARK,
                 font=(theme.FONT, 12, "bold")).pack(pady=(2, 8))

        # --- Счётчик фолловеров и показатели ---
        self.coins_label = tk.Label(self.root, font=(theme.FONT, 24, "bold"),
                                    fg=theme.TEXT, bg=theme.BG_DARK)
        self.coins_label.pack()

        self.rate_label = tk.Label(self.root, font=(theme.FONT, 8),
                                   fg=theme.TEXT_DIM, bg=theme.BG_DARK)
        self.rate_label.pack(pady=(2, 0))

        # --- Зона стрима (отдельный Frame нужен для всплывающих «+N») ---
        self.click_area = tk.Frame(self.root, width=420, height=110,
                                   bg=theme.BG_DARK)
        self.click_area.pack(pady=6)
        self.click_area.pack_propagate(False)  # не сжиматься под кнопку
        self.click_button = tk.Button(
            self.click_area, text="ВЫЙТИ В ЭФИР", font=(theme.FONT, 17, "bold"),
            width=16, height=2, command=self.on_click)
        theme.style_button(self.click_button, accent=True)
        self.click_button.place(relx=0.5, rely=0.62, anchor="center")

        # --- Строка статуса (вирусный момент, нехватка фолловеров и т.п.) ---
        self.status_label = tk.Label(self.root, font=(theme.FONT, 10),
                                     fg=theme.ACCENT_HOVER, bg=theme.BG_DARK)
        self.status_label.pack()

        # --- Блок улучшений (кнопки строятся из списка UPGRADES) ---
        box = tk.LabelFrame(self.root, text=" Прокачка канала ",
                            fg=theme.ACCENT, bg=theme.BG_PANEL,
                            font=(theme.FONT, 10, "bold"),
                            relief="flat", padx=8, pady=8)
        box.pack(fill="x", padx=16, pady=8)
        for up in upgrades.UPGRADES:
            btn = tk.Button(box, font=(theme.FONT, 9), anchor="w",
                            justify="left", relief="flat", borderwidth=0,
                            cursor="hand2",
                            command=lambda k=up.key: self.on_buy(k))
            btn.pack(fill="x", pady=3)
            self._upgrade_buttons[up.key] = btn

        # --- Статистика ---
        self.stats_label = tk.Label(self.root, font=(theme.FONT, 9),
                                    fg=theme.TEXT_DIM, bg=theme.BG_DARK,
                                    justify="left")
        self.stats_label.pack(pady=4)

        # --- Нижняя панель управления ---
        bottom = tk.Frame(self.root, bg=theme.BG_DARK)
        bottom.pack(side="bottom", pady=14)
        self._make_tool_button(bottom, "Достижения", self.show_achievements)
        self.mute_var = tk.IntVar(value=1 if self.state.muted else 0)
        tk.Checkbutton(bottom, text="Без звука", variable=self.mute_var,
                       command=self.on_mute, bg=theme.BG_DARK, fg=theme.TEXT_DIM,
                       activebackground=theme.BG_DARK, activeforeground=theme.TEXT,
                       selectcolor=theme.BG_ELEVATED,
                       font=(theme.FONT, 9)).pack(side="left", padx=4)
        self._make_tool_button(bottom, "Сохранить", self.on_save)
        self._make_tool_button(bottom, "Сбросить", self.on_reset)

    # Создаёт небольшую кнопку в тёмном стиле и кладёт её в контейнер.
    def _make_tool_button(self, parent, text, command):
        btn = tk.Button(parent, text=text, command=command,
                        font=(theme.FONT, 9), padx=8, pady=2)
        theme.style_button(btn)
        btn.pack(side="left", padx=4)
        return btn

    # ------------------------------------------------------------------
    # Обработчики действий игрока
    # ------------------------------------------------------------------

    # Нажатие на главную кнопку — игрок выходит в эфир.
    def on_click(self):
        gain, is_crit = mechanics.do_click(self.state)
        if is_crit:
            self.sound.crit()
            self.status_label.config(text=f"Вирусный момент!  +{int(gain)}")
        else:
            self.sound.click()
            self.status_label.config(text="")
        self._show_popup(gain, is_crit)
        self._after_change()

    # Покупка улучшения по ключу.
    def on_buy(self, key):
        if upgrades.buy(self.state, key):
            self.status_label.config(text=f"Куплено: {upgrades.get(key).title}")
            self._after_change()
        else:
            self.status_label.config(text="Не хватает фолловеров")

    # Переключение звука.
    def on_mute(self):
        self.state.muted = bool(self.mute_var.get())
        self.sound.muted = self.state.muted

    # Ручное сохранение прогресса.
    def on_save(self):
        state.save(self.state)
        messagebox.showinfo("Поднятие стримера", "Прогресс сохранён.")

    # Сброс всего прогресса после подтверждения.
    def on_reset(self):
        if not messagebox.askyesno("Поднятие стримера", "Сбросить весь прогресс?"):
            return
        state.delete_save()
        self.state = state.GameState()
        self.mute_var.set(0)
        self.sound.muted = False
        self.status_label.config(text="")
        self.refresh()

    # Сохранение прогресса и закрытие окна.
    def on_close(self):
        state.save(self.state)
        self.root.destroy()

    # ------------------------------------------------------------------
    # Игровой цикл
    # ------------------------------------------------------------------

    # Раз в секунду начисляет пассивный доход и планирует следующий тик.
    def _auto_loop(self):
        mechanics.do_auto_tick(self.state)
        self._after_change()
        self.root.after(AUTO_TICK_MS, self._auto_loop)

    # Вызывается после любого изменения состояния игры.
    def _after_change(self):
        for ach in achievements.check(self.state):
            self.sound.achievement()
            self._show_toast(ach)
        self.refresh()

    # ------------------------------------------------------------------
    # Обновление интерфейса
    # ------------------------------------------------------------------

    # Перерисовывает все надписи и кнопки по текущему состоянию.
    def refresh(self):
        s = self.state
        self.coins_label.config(text=followers(s.coins))
        self.rate_label.config(text=(
            f"за стрим: +{mechanics.click_power(s):.0f}      "
            f"в секунду: +{mechanics.auto_income(s):.0f}      "
            f"множитель: x{mechanics.global_multiplier(s):.2f}      "
            f"вирусный момент: {mechanics.crit_chance(s) * 100:.0f}%"
        ))
        for up in upgrades.UPGRADES:
            lvl = upgrades.level(s, up.key)
            price = upgrades.cost(s, up.key)
            btn = self._upgrade_buttons[up.key]
            btn.config(text=f"{up.title}  (уровень {lvl})\n"
                            f"{up.description}\n"
                            f"Цена: {followers(price)}")
            # Доступную покупку подсвечиваем фиолетовым, недоступную — гасим.
            if upgrades.can_afford(s, up.key):
                btn.config(bg=theme.BG_AFFORD, fg=theme.TEXT,
                           activebackground=theme.ACCENT_DARK)
            else:
                btn.config(bg=theme.BG_ELEVATED, fg=theme.TEXT_DIM,
                           activebackground=theme.BG_ELEVATED)
        self.stats_label.config(text=(
            f"Стримов проведено: {s.total_clicks}        "
            f"Собрано всего: {followers(s.total_earned)}\n"
            f"Достижений получено: {len(s.unlocked)} / {achievements.total()}"
        ))

    # Показывает всплывающее «+N» над кнопкой стрима с анимацией.
    def _show_popup(self, gain, is_crit):
        color = theme.CRIT if is_crit else theme.GOOD
        popup = tk.Label(self.click_area, text=f"+{int(gain)}", bg=theme.BG_DARK,
                         fg=color, font=(theme.FONT, 15, "bold"))
        popup.place(relx=0.5, rely=0.28, anchor="center")
        self._animate_popup(popup, 0)

    # Плавно поднимает всплывающую надпись вверх и затем убирает её.
    def _animate_popup(self, popup, step):
        if step >= 12:
            popup.destroy()
            return
        popup.place_configure(rely=0.28 - step * 0.018)
        self.root.after(40, lambda: self._animate_popup(popup, step + 1))

    # Показывает уведомление о новом достижении на 3 секунды.
    def _show_toast(self, ach):
        if self._toast is not None:
            self._toast.destroy()
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)         # окно без рамки
        toast.configure(bg=theme.TOAST_BG)
        tk.Label(toast, bg=theme.TOAST_BG, fg=theme.TEXT, justify="left",
                 font=(theme.FONT, 9),
                 text=f"Достижение получено!\n{ach.title} — {ach.description}"
                 ).pack(padx=12, pady=8)
        self.root.update_idletasks()
        x = self.root.winfo_x() + 30
        y = self.root.winfo_y() + 90
        toast.geometry(f"+{x}+{y}")
        self._toast = toast
        self.root.after(3000, toast.destroy)

    # Открывает прокручиваемое окно со списком всех достижений.
    def show_achievements(self):
        win = tk.Toplevel(self.root)
        win.title("Достижения")
        win.geometry("420x460")
        win.resizable(False, False)
        win.configure(bg=theme.BG_DARK)

        # Прокрутка: Canvas с вложенным Frame и полосой Scrollbar.
        canvas = tk.Canvas(win, bg=theme.BG_DARK, highlightthickness=0)
        scroll = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=theme.BG_DARK)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        for ach in achievements.ACHIEVEMENTS:
            done = ach.id in self.state.unlocked
            mark = "[+]" if done else "[ ]"
            fg = theme.GOOD if done else theme.TEXT_DIM
            tk.Label(inner, justify="left", anchor="w", bg=theme.BG_DARK, fg=fg,
                     width=48, font=(theme.FONT, 10),
                     text=f"{mark}  {ach.title}\n        {ach.description}"
                     ).pack(fill="x", padx=12, pady=5)
