# DateNew.py

import ctypes
from typing import Optional

# Словарь для сопоставления РУССКИХ названий месяцев и их номеров (ключи в нижнем регистре)
MONTHS_MAP = {
    "янв": 1, "фев": 2, "мар": 3, "апр": 4,
    "май": 5, "июн": 6, "июл": 7, "авг": 8,
    "сен": 9, "окт": 10, "ноя": 11, "дек": 12
}

# Обратное сопоставление для __repr__ (ключи - номера, значения - в нужном регистре)
MONTHS_NAMES = {
    1: "янв", 2: "фев", 3: "мар", 4: "апр",
    5: "май", 6: "июн", 7: "июл", 8: "авг",
    9: "сен", 10: "окт", 11: "ноя", 12: "дек"
}

class DateNew:
    # Используем ctypes для массива дней в месяце (индекс 0 не используется)
    DAYS_IN_MONTH = (ctypes.c_int * 13)(0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

    def __init__(self, date_str: str) -> None:
        if not isinstance(date_str, str):
            raise TypeError(f"date_str must be str, not {type(date_str).__name__}")

        parts = date_str.strip().split(' ')
        if len(parts) != 3:
            raise ValueError(f"Дата должна быть в формате 'ДД МММ ГГГГ' (например: 15 янв 1980), получено: '{date_str}'")

        day_str, month_str, year_str = parts

        # Валидация года
        self._check_valid_year(year_str)
        year = int(year_str)

        # Валидация месяца (по названию)
        self._check_valid_month_name(month_str)
        month = MONTHS_MAP[month_str.lower()]

        # Валидация дня
        self._check_valid_day_for_month(day_str, month, year)
        day = int(day_str)

        self.day = day
        self.month = month
        self.year = year

    def __repr__(self) -> str:
        # Формат dd mmm yyyy
        month_name = MONTHS_NAMES[self.month]
        return f"{self.day:02d} {month_name} {self.year}"

    def __eq__(self, other: "DateNew") -> bool:
        if not isinstance(other, DateNew):
            return NotImplemented
        return (
            self.day == other.day
            and self.month == other.month
            and self.year == other.year
        )

    def __lt__(self, other: "DateNew") -> bool:
        if not isinstance(other, DateNew):
            return NotImplemented

        if self.year != other.year:
            return self.year < other.year
        if self.month != other.month:
            return self.month < other.month
        return self.day < other.day

    @staticmethod
    def _check_valid_year(s: str) -> None:
        try:
            year = int(s)
        except ValueError:
            raise ValueError(f"Неверный формат года: {s!r}")
        if not (1 <= year <= 9999):
            raise ValueError(f"Год должен быть от 1 до 9999, получено {year}")

    @staticmethod
    def _check_valid_month_name(s: str) -> None:
        if s.lower() not in MONTHS_MAP:
            valid_months = ", ".join(MONTHS_MAP.keys())
            raise ValueError(f"Неверное название месяца: {s!r}. Допустимые: {valid_months}")

    @classmethod
    def _check_valid_day_for_month(cls, day_str: str, month: int, year: int) -> None:
        try:
            day = int(day_str)
        except ValueError:
            raise ValueError(f"Неверный формат дня: {day_str!r}")
        # Определение максимального дня в месяце
        max_day = cls.DAYS_IN_MONTH[month]
        if month == 2 and cls._is_leap_year(year):
            max_day = 29

        if not (1 <= day <= max_day):
            raise ValueError(f"День {day} вне диапазона для месяца {MONTHS_NAMES[month]} и года {year}")

    @staticmethod
    def _is_leap_year(year: int) -> bool:
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

# --- Тестирование ---
if __name__ == "__main__":
    try:
        d1 = DateNew("01 янв 2020")
        d2 = DateNew("29 фев 2024")  # Високосный
        d3 = DateNew("15 мар 2023")
        print("DateNew objects created successfully.")
        print(d1)  # 01 янв 2020
        print(d2)  # 29 фев 2024
        print(d3)  # 15 мар 2023
        print(d1 < d2)  # True
        print(d1 == DateNew("01 янв 2020"))  # True
    except ValueError as e:
        print(f"ValueError: {e}")
    except TypeError as e:
        print(f"TypeError: {e}")