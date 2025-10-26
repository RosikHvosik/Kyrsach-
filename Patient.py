# Patient.py

from DateNew import DateNew # Импортируем наш новый класс даты

class Patient:
    # Убрано значение по умолчанию = None для birth_date
    def __init__(self, oms_policy: int, full_name: str, birth_date: DateNew):
        self.validate_oms_policy(oms_policy)
        self.validate_full_name(full_name)
        # Проверка на None теперь бессмысленна, если birth_date всегда передаётся
        # if birth_date is None:
        #     # Можно установить значение по умолчанию или требовать указание
        #     # Для примера, пусть будет ошибка
        #     raise ValueError("Birth date is required for Patient.")
        if not isinstance(birth_date, DateNew):
             raise TypeError(f"birth_date must be an instance of DateNew, got {type(birth_date).__name__}")
        self.oms_policy = oms_policy
        self.full_name = full_name
        self.birth_date = birth_date

    def __repr__(self):
        return f"Patient(OMS_Policy={self.oms_policy}, Full_Name='{self.full_name}', Birth_Date={self.birth_date})"

    @staticmethod
    def validate_oms_policy(oms_policy: int) -> None:
        if not isinstance(oms_policy, int):
            raise TypeError(f"The OMS Policy must be an integer, received {type(oms_policy).__name__}")
        if oms_policy <= 0:
            raise ValueError("The OMS Policy must be a positive number")
        # Можно добавить проверку на длину, если нужно, например, 16 цифр
        # str_oms = str(oms_policy)
        # if len(str_oms) != 16: # Пример длины
        #     raise ValueError("The OMS Policy must be 16 digits long")

    @staticmethod
    def validate_full_name(full_name: str) -> None:
        if not isinstance(full_name, str):
            raise TypeError(f"The full name must be a string, received {type(full_name).__name__}")
        if full_name is None or full_name.strip() == "":
            raise ValueError("The full name cannot be empty")

    # Методы сравнения, если понадобятся в будущем (например, для сортировки списка пациентов)
    # В текущем контексте (ключ ХТ) они не используются.
    def __eq__(self, other):
        if not isinstance(other, Patient):
            return NotImplemented
        return self.oms_policy == other.oms_policy and self.full_name == other.full_name and self.birth_date == other.birth_date

    def __lt__(self, other):
        if not isinstance(other, Patient):
            return NotImplemented
        # Сравниваем по OMS Policy, затем по ФИО, затем по дате рождения
        if self.oms_policy != other.oms_policy:
            return self.oms_policy < other.oms_policy
        if self.full_name != other.full_name:
            return self.full_name < other.full_name
        return self.birth_date < other.birth_date

# --- Тестирование ---
if __name__ == "__main__":
    try:
        d = DateNew("15 Dec 1985")
        p1 = Patient(oms_policy=1234567890123456, full_name="Иванов Иван Иванович", birth_date=d)
        print(p1)
        # p2 = Patient(oms_policy="not_a_number", full_name="Test", birth_date=d) # Ошибка
        # p3 = Patient(oms_policy=123, full_name="", birth_date=d) # Ошибка
        # p4 = Patient(oms_policy=123, full_name="Test", birth_date="not_a_date") # Ошибка
    except (ValueError, TypeError) as e:
        print(f"Error creating Patient: {e}")
