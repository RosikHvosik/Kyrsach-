# massive.py
# Функции для загрузки данных из файлов в массивы и заполнения соответствующих структур данных

from Patient import Patient
from Appointment import Appointment
from DateNew import DateNew
from hash_table import HashTable
from avl_tree import AVLTree
from List import MyList # Импорт MyList, который теперь правильно добавляет в начало
from parser import parse # Используем ваш парсер

def patients_to_array(filename: str, patient_ht: HashTable, patient_arr, first_empty_index: int) -> int:
    """
    Загружает пациентов из файла в массив patient_arr и заполняет patient_ht.
    Возвращает обновлённый индекс first_empty_patient.
    """
    current_index = first_empty_index
    with open(filename, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1): # Нумеруем строки для отладки
            line = line.strip()
            if not line:
                print(f"[DEBUG massive] Skipping empty line {line_num}") # Лог 1
                continue # Пропускаем пустые строки

            print(f"[DEBUG massive] Processing line {line_num}: '{line}'") # Лог 2
            # Парсим строку
            parts_list = parse(line, sep=';') # MyList[str]
            print(f"[DEBUG massive] parts_list from parser: {parts_list}") # Лог 3
            if len(parts_list) != 3:
                print(f"Warning: Skipping invalid patient line {line_num}: '{line}'. Expected 3 parts, got {len(parts_list)}.")
                continue

            try:
                oms_str = parts_list[0]
                full_name = parts_list[1]
                birth_date_str = parts_list[2]

                print(f"[DEBUG massive] oms_str: '{oms_str}', full_name: '{full_name}', birth_date_str: '{birth_date_str}'") # Лог 4

                oms_policy = int(oms_str) # <-- Преобразуем строку OMS в int
                print(f"[DEBUG massive] oms_policy: {oms_policy}") # Лог 5
                birth_date = DateNew(birth_date_str) # <-- Создаём объект DateNew из строки даты
                print(f"[DEBUG massive] birth_date: {birth_date}") # Лог 6

                # Создаём объект Patient, передавая ему объект DateNew
                patient = Patient(oms_policy=oms_policy, full_name=full_name, birth_date=birth_date)
                print(f"[DEBUG massive] Created Patient: {patient}") # Лог 7

                # Проверяем, помещается ли новый пациент
                if current_index >= len(patient_arr):
                     print(f"Error: Patient array is full. Cannot load more patients from {filename}.")
                     break # Прерываем загрузку, если массив полон

                # Попытка вставить в ХТ. Возвращает индекс вставки или -1 при дубликате.
                inserted_idx = patient_ht.insert(patient.oms_policy, current_index)
                if inserted_idx == -1:
                    print(f"Warning: Duplicate OMS Policy {oms_policy} found in file {filename}, skipping patient '{full_name}'.")
                    continue # Пропускаем дубликат

                # Запись в массив
                patient_arr[current_index] = patient
                print(f"[DEBUG massive] Patient inserted at index {current_index}") # Лог 8
                current_index += 1

            except (ValueError, TypeError) as e:
                # Ловим ошибки при int(oms_str) или DateNew(birth_date_str) или Patient(...)
                # Сообщение об ошибке будет содержать информацию о том, что именно вызвало исключение
                print(f"Warning: Skipping invalid patient line {line_num}: '{line}'. Error: {e}")
                continue

    return current_index


def appointments_to_array(
    filename: str,
    appointment_tree: AVLTree[int], # AVLTree для OMS
    patient_ht: HashTable, # Для проверки существования пациента
    appointment_arr,
    first_empty_index: int,
    appointment_date_tree: AVLTree[DateNew] # AVLTree для даты
) -> int:
    """
    Загружает приёмы из файла в массив appointment_arr и заполняет appointment_tree и appointment_date_tree.
    Возвращает обновлённый индекс first_empty_appointment.
    """
    current_index = first_empty_index
    with open(filename, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1): # Нумеруем строки для отладки
            line = line.strip()
            if not line:
                print(f"[DEBUG massive] Appointment: Skipping empty line {line_num}") # Лог 1
                continue # Пропускаем пустые строки

            print(f"[DEBUG massive] Appointment: Processing line {line_num}: '{line}'") # Лог 2
            # Парсим строку
            parts_list = parse(line, sep=';') # MyList[str]
            print(f"[DEBUG massive] Appointment: parts_list from parser: {parts_list}") # Лог 3
            if len(parts_list) != 4:
                print(f"Warning: Skipping invalid appointment line {line_num}: '{line}'. Expected 4 parts, got {len(parts_list)}.")
                continue

            try:
                oms_str = parts_list[0]
                diagnosis = parts_list[1]
                doctor = parts_list[2]
                appointment_date_str = parts_list[3]

                print(f"[DEBUG massive] Appointment: oms_str: '{oms_str}', diagnosis: '{diagnosis}', doctor: '{doctor}', appointment_date_str: '{appointment_date_str}'") # Лог 4

                oms_policy = int(oms_str)
                print(f"[DEBUG massive] Appointment: oms_policy: {oms_policy}") # Лог 5
                appointment_date = DateNew(appointment_date_str)
                print(f"[DEBUG massive] Appointment: appointment_date: {appointment_date}") # Лог 6

                # Проверяем существование пациента
                patient_search_result = patient_ht.search(oms_policy)
                if patient_search_result[0] is None:
                    print(f"Warning: Appointment for OMS Policy {oms_policy} found in {filename}, but patient does not exist. Skipping appointment.")
                    continue

                appointment = Appointment(oms_policy=oms_policy, diagnosis=diagnosis, doctor=doctor, appointment_date=appointment_date)
                print(f"[DEBUG massive] Appointment: Created Appointment: {appointment}") # Лог 7

                # Проверяем, помещается ли новый приём
                if current_index >= len(appointment_arr):
                     print(f"Error: Appointment array is full. Cannot load more appointments from {filename}.")
                     break # Прерываем загрузку, если массив полон

                # Вставка в деревья
                appointment_tree.insert(appointment.oms_policy, current_index)
                appointment_date_tree.insert(appointment.appointment_date, current_index)

                # Запись в массив
                appointment_arr[current_index] = appointment
                print(f"[DEBUG massive] Appointment: Appointment inserted at index {current_index}") # Лог 8
                current_index += 1

            except (ValueError, TypeError) as e:
                print(f"Warning: Skipping invalid appointment line {line_num}: '{line}'. Error: {e}")
                continue

    return current_index

# --- Тестирование (опционально) ---
# if __name__ == "__main__":
#     # Пример использования (требует созданных экземпляров СД и массивов)
#     # ht = HashTable()
#     # avl_oms = AVLTree[int]()
#     # avl_date = AVLTree[DateNew]()
#     # PatientArrayType = ctypes.py_object * MAX_SIZE
#     # AppointmentArrayType = ctypes.py_object * MAX_SIZE
#     # p_arr = PatientArrayType()
#     # a_arr = AppointmentArrayType()
#     # for i in range(MAX_SIZE):
#     #     p_arr[i] = None
#     #     a_arr[i] = None
#     # first_p = patients_to_array("patients.txt", ht, p_arr, 0)
#     # first_a = appointments_to_array("appointments.txt", avl_oms, ht, a_arr, 0, avl_date)
#     pass
