# Appointment.py

from DateNew import DateNew

class Appointment:
    def __init__(self, oms_policy: int, diagnosis: str, doctor: str, appointment_date: DateNew):
        self.validate_oms_policy(oms_policy)
        self.validate_diagnosis(diagnosis)
        self.validate_doctor(doctor)
        if not isinstance(appointment_date, DateNew):
             raise TypeError(f"appointment_date must be an instance of DateNew, got {type(appointment_date).__name__}")

        self.oms_policy = oms_policy
        self.diagnosis = diagnosis
        self.doctor = doctor
        self.appointment_date = appointment_date

    def __repr__(self):
        return (f"Appointment(OMS_Policy={self.oms_policy}, Diagnosis='{self.diagnosis}', "
                f"Doctor='{self.doctor}', Appointment_Date={self.appointment_date})")

    @staticmethod
    def validate_oms_policy(oms_policy: int) -> None:
        if not isinstance(oms_policy, int):
            raise TypeError(f"The OMS Policy must be an integer, received {type(oms_policy).__name__}")
        if oms_policy <= 0:
            raise ValueError("The OMS Policy must be a positive number")

    @staticmethod
    def validate_diagnosis(diagnosis: str) -> None:
        if not isinstance(diagnosis, str):
            raise TypeError(f"The diagnosis must be a string, received {type(diagnosis).__name__}")
        if diagnosis is None or diagnosis.strip() == "":
            raise ValueError("The diagnosis cannot be empty")

    @staticmethod
    def validate_doctor(doctor: str) -> None:
        if not isinstance(doctor, str):
            raise TypeError(f"The doctor's name must be a string, received {type(doctor).__name__}")
        if doctor is None or doctor.strip() == "":
            raise ValueError("The doctor's name cannot be empty")

    # Методы сравнения, если понадобятся
    def __eq__(self, other):
        if not isinstance(other, Appointment):
            return NotImplemented
        return (self.oms_policy == other.oms_policy and
                self.diagnosis == other.diagnosis and
                self.doctor == other.doctor and
                self.appointment_date == other.appointment_date)

    def __lt__(self, other):
        if not isinstance(other, Appointment):
            return NotImplemented
        # Пример: сортировка по дате приёма, затем по фамилии врача
        if self.appointment_date != other.appointment_date:
            return self.appointment_date < other.appointment_date
        return self.doctor < other.doctor

# --- Тестирование ---
if __name__ == "__main__":
    try:
        d = DateNew("20 Nov 2023")
        a1 = Appointment(oms_policy=1234567890123456, diagnosis="Грипп", doctor="Петров П.П.", appointment_date=d)
        print(a1)
        # a2 = Appointment(oms_policy="not_a_number", diagnosis="Test", doctor="Doc", appointment_date=d) # Ошибка
        # a3 = Appointment(oms_policy=123, diagnosis="", doctor="Doc", appointment_date=d) # Ошибка
        # a4 = Appointment(oms_policy=123, diagnosis="Test", doctor="", appointment_date=d) # Ошибка
        # a5 = Appointment(oms_policy=123, diagnosis="Test", doctor="Doc", appointment_date="not_a_date") # Ошибка
    except (ValueError, TypeError) as e:
        print(f"Error creating Appointment: {e}")
