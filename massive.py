# massive.py - ИСПРАВЛЕННАЯ ВЕРСИЯ

from Patient import Patient
from Appointment import Appointment
from DateNew import DateNew
from hash_table import HashTable
from avl_tree import AVLTree
from List import MyList
from parser import parse

def patients_to_array(filename: str, patient_ht: HashTable, patient_arr, first_empty_index: int) -> int:
    """
    Загружает пациентов из файла в массив patient_arr и заполняет patient_ht.
    Возвращает обновлённый индекс first_empty_patient.
    """
    current_index = first_empty_index
    with open(filename, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                print(f"[DEBUG massive] Skipping empty line {line_num}")
                continue

            print(f"[DEBUG massive] Processing line {line_num}: '{line}'")
            parts_list = parse(line, sep=';')
            print(f"[DEBUG massive] parts_list from parser: {parts_list}")
            if len(parts_list) != 3:
                print(f"Warning: Skipping invalid patient line {line_num}: '{line}'. Expected 3 parts, got {len(parts_list)}.")
                continue

            try:
                # ИСПРАВЛЕНИЕ: parts_list добавляет в начало, поэтому порядок обратный
                # Было: [0]=oms, [1]=name, [2]=date
                # Стало: [0]=date, [1]=name, [2]=oms (из-за append в начало)
                # Поэтому берём с конца:
                oms_str = parts_list[2]        # Последний элемент = первый добавленный
                full_name = parts_list[1]      # Средний остаётся средним
                birth_date_str = parts_list[0] # Первый элемент = последний добавленный

                print(f"[DEBUG massive] oms_str: '{oms_str}', full_name: '{full_name}', birth_date_str: '{birth_date_str}'")

                oms_policy = int(oms_str)
                print(f"[DEBUG massive] oms_policy: {oms_policy}")
                birth_date = DateNew(birth_date_str)
                print(f"[DEBUG massive] birth_date: {birth_date}")

                patient = Patient(oms_policy=oms_policy, full_name=full_name, birth_date=birth_date)
                print(f"[DEBUG massive] Created Patient: {patient}")

                if current_index >= len(patient_arr):
                     print(f"Error: Patient array is full. Cannot load more patients from {filename}.")
                     break

                inserted_idx = patient_ht.insert(patient.oms_policy, current_index)
                if inserted_idx == -1:
                    print(f"Warning: Duplicate OMS Policy {oms_policy} found in file {filename}, skipping patient '{full_name}'.")
                    continue

                patient_arr[current_index] = patient
                print(f"[DEBUG massive] Patient inserted at index {current_index}")
                current_index += 1

            except (ValueError, TypeError) as e:
                print(f"Warning: Skipping invalid patient line {line_num}: '{line}'. Error: {e}")
                continue

    return current_index


def appointments_to_array(
    filename: str,
    appointment_tree: AVLTree[int],
    patient_ht: HashTable,
    appointment_arr,
    first_empty_index: int,
    appointment_date_tree: AVLTree[DateNew]
) -> int:
    """
    Загружает приёмы из файла в массив appointment_arr и заполняет деревья.
    Возвращает обновлённый индекс first_empty_appointment.
    """
    current_index = first_empty_index
    with open(filename, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                print(f"[DEBUG massive] Appointment: Skipping empty line {line_num}")
                continue

            print(f"[DEBUG massive] Appointment: Processing line {line_num}: '{line}'")
            parts_list = parse(line, sep=';')
            print(f"[DEBUG massive] Appointment: parts_list from parser: {parts_list}")
            if len(parts_list) != 4:
                print(f"Warning: Skipping invalid appointment line {line_num}: '{line}'. Expected 4 parts, got {len(parts_list)}.")
                continue

            try:
                # ИСПРАВЛЕНИЕ: обратный порядок из-за append в начало
                # Формат файла: oms;diagnosis;doctor;date
                # После parse: [3]=oms, [2]=diagnosis, [1]=doctor, [0]=date
                oms_str = parts_list[3]
                diagnosis = parts_list[2]
                doctor = parts_list[1]
                appointment_date_str = parts_list[0]

                print(f"[DEBUG massive] Appointment: oms_str: '{oms_str}', diagnosis: '{diagnosis}', doctor: '{doctor}', appointment_date_str: '{appointment_date_str}'")

                oms_policy = int(oms_str)
                print(f"[DEBUG massive] Appointment: oms_policy: {oms_policy}")
                appointment_date = DateNew(appointment_date_str)
                print(f"[DEBUG massive] Appointment: appointment_date: {appointment_date}")

                patient_search_result = patient_ht.search(oms_policy)
                if patient_search_result[0] is None:
                    print(f"Warning: Appointment for OMS Policy {oms_policy} found in {filename}, but patient does not exist. Skipping appointment.")
                    continue

                appointment = Appointment(oms_policy=oms_policy, diagnosis=diagnosis, doctor=doctor, appointment_date=appointment_date)
                print(f"[DEBUG massive] Appointment: Created Appointment: {appointment}")

                if current_index >= len(appointment_arr):
                     print(f"Error: Appointment array is full. Cannot load more appointments from {filename}.")
                     break

                appointment_tree.insert(appointment.oms_policy, current_index)
                appointment_date_tree.insert(appointment.appointment_date, current_index)

                appointment_arr[current_index] = appointment
                print(f"[DEBUG massive] Appointment: Appointment inserted at index {current_index}")
                current_index += 1

            except (ValueError, TypeError) as e:
                print(f"Warning: Skipping invalid appointment line {line_num}: '{line}'. Error: {e}")
                continue

    return current_index