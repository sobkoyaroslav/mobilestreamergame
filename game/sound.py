# -*- coding: utf-8 -*-
# Генерация и воспроизведение звуков без сторонних библиотек.
#
# WAV-файлы синтезируются при первом запуске и сохраняются рядом с этим
# модулем. На Windows воспроизводятся через стандартный модуль winsound.
# На других ОС звук просто отключается (winsound недоступен).

import math
import os
import struct
import wave

from .paths import data_dir

# Звуковые файлы кладём в ту же папку, что и сохранение (для .exe — рядом
# с .exe, при обычном запуске — в корень проекта).
_SOUND_DIR = data_dir()
_RATE = 44100  # частота дискретизации, Гц

# Описание звуков: имя -> список тонов вида (частота_Гц, длительность_сек).
_SOUNDS = {
    "click": [(880, 0.05)],                     # короткий звук стрима
    "crit": [(1200, 0.13)],                     # звонкий звук вирусного момента
    "achievement": [(660, 0.10), (990, 0.20)],  # двухнотный «джингл» достижения
}

try:
    import winsound
    _HAS_WINSOUND = True
except ImportError:
    _HAS_WINSOUND = False


# Путь к WAV-файлу звука с данным именем.
def _path(name):
    return os.path.join(_SOUND_DIR, f"snd_{name}.wav")


# Синтезирует WAV-файл из набора тонов (чистые синусоиды с огибающей).
def _synth(path, tones, volume=0.45):
    frames = bytearray()
    for freq, duration in tones:
        count = int(_RATE * duration)
        for i in range(count):
            # Огибающая: быстрая атака и плавный спад — получается «щелчок».
            attack = min(1.0, i / (count * 0.1 + 1))
            decay = 1.0 - i / count
            envelope = attack * decay
            value = volume * envelope * math.sin(2 * math.pi * freq * i / _RATE)
            frames += struct.pack("<h", int(value * 32767))
    with wave.open(path, "w") as wav:
        wav.setnchannels(1)      # моно
        wav.setsampwidth(2)      # 16 бит на отсчёт
        wav.setframerate(_RATE)
        wav.writeframes(bytes(frames))


# Создаёт недостающие звуковые файлы (один раз при первом запуске).
def ensure_sounds():
    for name, tones in _SOUNDS.items():
        path = _path(name)
        if not os.path.exists(path):
            _synth(path, tones)


# Проигрывает игровые звуки и умеет полностью выключаться.
class SoundPlayer:

    def __init__(self, muted=False):
        self.muted = muted
        ensure_sounds()

    # Асинхронно проигрывает звук, если звук включён и доступен winsound.
    def _play(self, name):
        if self.muted or not _HAS_WINSOUND:
            return
        try:
            winsound.PlaySound(_path(name),
                               winsound.SND_FILENAME | winsound.SND_ASYNC)
        except RuntimeError:
            pass  # звук не критичен для игры — молча игнорируем сбой

    # Звук обычного стрима.
    def click(self):
        self._play("click")

    # Звук вирусного момента.
    def crit(self):
        self._play("crit")

    # Звук получения достижения.
    def achievement(self):
        self._play("achievement")
