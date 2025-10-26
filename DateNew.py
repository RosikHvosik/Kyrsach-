# DateNew.py

import ctypes
from typing import Optional

# Словарь для сопоставления названий месяцев и их номеров (ключи в нижнем регистре)
MONTHS_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12
}

# Обратное сопоставление для __repr__ (ключи - номера, значения - в верхнем регистре)
MONTHS_NAMES = {v: k.capitalize() for k, v in MONTHS_MAP.items()}

class DateNew:
    # Используем ctypes для массива дней в месяце (индекс 0 не используется)
    DAYS_IN_MONTH = (ctypes.c_int * 13)(0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

    def __init__(self, date_str: str) -> None:
        if not isinstance(date_str, str):
            raise TypeError(f"date_str must be str, not {type(date_str).__name__}")

        parts = date_str.strip().split(' ')
        if len(parts) != 3:
            raise ValueError(f"Date must be in format 'DD MMM YYYY', got '{date_str}'")

        day_str, month_str, year_str = parts

        # Валидация года
        self._check_valid_year(year_str)
        year = int(year_str)

        # Валидация месяца (по названию)
        self._check_valid_month_name(month_str) # <-- Проверка на нижний регистр
        month = MONTHS_MAP[month_str.lower()] # <-- Извлечение по нижнему регистру

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
            raise ValueError(f"Invalid year format: {s!r}")
        if not (1 <= year <= 9999):
            raise ValueError(f"Year must be between 1 and 9999, got {year}")

    @staticmethod
    def _check_valid_month_name(s: str) -> None:
        if s.lower() not in MONTHS_MAP: # <-- Проверка на нижний регистр
            valid_months = ", ".join(MONTHS_MAP.keys()) # <-- Вывод допустимых месяцев в нижнем регистре
            raise ValueError(f"Invalid month name: {s!r}. Valid names are: {valid_months}")

    @classmethod
    def _check_valid_day_for_month(cls, day_str: str, month: int, year: int) -> None:
        try:
            day = int(day_str)
        except ValueError:
            raise ValueError(f"Invalid day format: {day_str!r}")
        # Определение максимального дня в месяце
        max_day = cls.DAYS_IN_MONTH[month]
        if month == 2 and cls._is_leap_year(year):
            max_day = 29

        if not (1 <= day <= max_day):
            raise ValueError(f"Day {day} is out of range for month {MONTHS_NAMES[month]} and year {year}")

    @staticmethod
    def _is_leap_year(year: int) -> bool:
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

# --- Тестирование ---
if __name__ == "__main__":
    try:
        d1 = DateNew("01 Jan 2020")
        d2 = DateNew("29 Feb 2024") # Високосный
        # d3 = DateNew("31 Apr 2023") # Неверный день
        print("DateNew objects created successfully.")
    except ValueError as e:
        print(f"ValueError: {e}")
    except TypeError as e:
        print(f"TypeError: {e}")

    print(d1) # 01 Jan 2020
    print(d2) # 29 Feb 2024
    print(d1 < d2) # True
    print(d1 == DateNew("01 Jan 2020")) # True
    # print(DateNew("32 Jan 2023")) # ValueError
    # print(DateNew("01 Xxx 2023")) # ValueError
    # print(DateNew(123)) # TypeError
