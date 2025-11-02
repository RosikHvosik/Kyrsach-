import ctypes
from Patient import Patient
from Appointment import Appointment
from DateNew import DateNew
from hash_table import HashTable
from avl_tree import AVLTree
from List import MyList
from massive import patients_to_array, appointments_to_array


MAX_SIZE = 1000
PatientArrayType = ctypes.py_object * MAX_SIZE
AppointmentArrayType = ctypes.py_object * MAX_SIZE


class RelationalDatabase:
    def __init__(self):
        # Массивы для хранения объектов
        self.patient_arr = PatientArrayType()
        self.appointment_arr = AppointmentArrayType()
        for i in range(MAX_SIZE):
            self.patient_arr[i] = None
            self.appointment_arr[i] = None

        # Структуры данных для ускорения поиска
        # Хеш-таблица для пациентов по OMS Policy (ключ - int)
        self.patient_ht = HashTable()
        # AVL-дерево для приёмов по OMS Policy пациента (ключ - int)
        self.appointment_tree = AVLTree[int]()
        # AVL-дерево для приёмов по дате приёма (ключ - DateNew)
        self.appointment_date_tree = AVLTree[DateNew]()

        # Счётчики первых пустых ячеек в массивах
        self.first_empty_patient = 0
        self.first_empty_appointment = 0

    # --- Загрузка из файлов ---
    def load_patients(self, filename: str):
        self.first_empty_patient = patients_to_array(filename, self.patient_ht, self.patient_arr, self.first_empty_patient)

    def load_appointments(self, filename: str):
        self.first_empty_appointment = appointments_to_array(
            filename, self.appointment_tree, self.patient_ht, self.appointment_arr,
            self.first_empty_appointment, self.appointment_date_tree
        )

    # --- Добавление ---
    def add_patient(self, oms_policy: int, full_name: str, birth_date_str: str) -> bool:
        if self.first_empty_patient >= MAX_SIZE:
            print("Maximum size of patient array has been reached")
            return False

        try:
            birth_date = DateNew(birth_date_str)
            patient = Patient(oms_policy=oms_policy, full_name=full_name, birth_date=birth_date)
        except (ValueError, TypeError) as e:
            print(f"Failed to add patient: {e}")
            return False

        inserted_idx = self.patient_ht.insert(patient.oms_policy, self.first_empty_patient)
        if inserted_idx == -1:
            print(f"Patient with OMS Policy {oms_policy} already exists.")
            return False

        self.patient_arr[self.first_empty_patient] = patient
        self.first_empty_patient += 1
        return True

    def add_appointment(self, oms_policy: int, diagnosis: str, doctor: str, appointment_date_str: str) -> bool:
        if self.first_empty_appointment >= MAX_SIZE:
            print("Maximum size of appointment array has been reached")
            return False

        if self.patient_ht.search(oms_policy)[0] is None:
            print(f"Cannot add appointment: Patient with OMS Policy {oms_policy} does not exist.")
            return False

        try:
            appointment_date = DateNew(appointment_date_str)
            appointment = Appointment(oms_policy=oms_policy, diagnosis=diagnosis, doctor=doctor, appointment_date=appointment_date)
        except (ValueError, TypeError) as e:
            print(f"Failed to add appointment: {e}")
            return False

        self.appointment_tree.insert(appointment.oms_policy, self.first_empty_appointment)
        self.appointment_date_tree.insert(appointment.appointment_date, self.first_empty_appointment)

        self.appointment_arr[self.first_empty_appointment] = appointment
        self.first_empty_appointment += 1
        return True

    # --- Удаление ---
    def delete_patient(self, oms_policy: int) -> bool:
        search_result = self.patient_ht.search(oms_policy)
        item = search_result[0]
        if item is None:
            print(f"Patient with OMS Policy {oms_policy} not found.")
            return False

        patient_index = item.value
        patient_to_delete = self.patient_arr[patient_index]

        self.patient_ht.delete(oms_policy)

        self.first_empty_patient -= 1
        moved_patient = self.patient_arr[self.first_empty_patient]
        self.patient_arr[self.first_empty_patient] = None

        if patient_index != self.first_empty_patient:
            self.patient_arr[patient_index] = moved_patient
            if moved_patient is not None:
                self.patient_ht.insert(moved_patient.oms_policy, patient_index)
        else:
            self.patient_arr[patient_index] = None

        node = self.appointment_tree.find(oms_policy)
        if node:
            indices_to_remove = list(node.values)
            for app_index in indices_to_remove:
                self._remove_appointment_index(app_index)
            self.appointment_tree.delete_node(oms_policy)

        print(f"Patient with OMS Policy {oms_policy} and associated appointments deleted.")
        return True

    def _remove_appointment_index(self, index: int):
        if index >= self.first_empty_appointment or self.appointment_arr[index] is None:
            return

        self.first_empty_appointment -= 1
        moved_appointment = self.appointment_arr[self.first_empty_appointment]
        self.appointment_arr[self.first_empty_appointment] = None

        app_to_remove = self.appointment_arr[index]
        if app_to_remove:
            self.appointment_tree.delete_value(app_to_remove.oms_policy, index)
            self.appointment_date_tree.delete_value(app_to_remove.appointment_date, index)

        if index != self.first_empty_appointment:
            self.appointment_arr[index] = moved_appointment
            if moved_appointment is not None:
                self.appointment_tree.delete_value(moved_appointment.oms_policy, self.first_empty_appointment)
                self.appointment_date_tree.delete_value(moved_appointment.appointment_date, self.first_empty_appointment)
                self.appointment_tree.insert(moved_appointment.oms_policy, index)
                self.appointment_date_tree.insert(moved_appointment.appointment_date, index)
        else:
            self.appointment_arr[index] = None

    def delete_appointment(self, target_oms: int, target_diagnosis: str, target_doctor: str, target_date_str: str) -> bool:
        try:
            target_date = DateNew(target_date_str)
        except (ValueError, TypeError) as e:
            print(f"Invalid date format for deletion: {e}")
            return False

        node = self.appointment_tree.find(target_oms)
        if not node:
             print(f"No appointments found for OMS Policy {target_oms} to match for deletion.")
             return False

        found_index = -1
        for idx in node.values:
            app = self.appointment_arr[idx]
            if (app and
                app.oms_policy == target_oms and
                app.diagnosis == target_diagnosis and
                app.doctor == target_doctor and
                app.appointment_date == target_date):
                found_index = idx
                break

        if found_index == -1:
            print("Appointment not found for deletion.")
            return False

        self.appointment_tree.delete_value(target_oms, found_index)
        self.appointment_date_tree.delete_value(target_date, found_index)

        self._remove_appointment_index(found_index)
        print(f"Appointment deleted.")
        return True

    # --- Поиск (возвращает количество шагов) ---
    def find_patient_steps(self, oms_policy: int) -> tuple:
        result = self.patient_ht.search(oms_policy)
        item = result[0]
        steps = result[1]
        patient = self.patient_arr[item.value] if item else None
        return patient, steps

    def find_appointments_by_oms_steps(self, oms_policy: int) -> tuple:
        node = self.appointment_tree.root
        steps = 0
        found_node = None
        while node:
            steps += 1
            if oms_policy < node.key:
                node = node.left
            elif oms_policy > node.key:
                node = node.right
            else:
                found_node = node
                break

        appointments = MyList[Appointment]()
        if found_node:
            for idx in found_node.values:
                app = self.appointment_arr[idx]
                if app:
                    appointments.append(app)
        return appointments, steps

    # --- Фильтрация (просмотр) ---
    def filter_patients_by_name(self, target_name: str) -> MyList[Patient]:
        """Фильтр для Справочника_1.Поле_2 (Full Name)."""
        result = MyList[Patient]()
        for i in range(self.first_empty_patient):
            patient = self.patient_arr[i]
            if patient is not None and patient.full_name == target_name:
                result.append(patient)
        return result

    def filter_appointments_by_doctor(self, target_doctor: str) -> MyList[Appointment]:
        """Фильтр для Справочника_2.Поле_3 (Doctor) - ИСПРАВЛЕНО."""
        result = MyList[Appointment]()
        for i in range(self.first_empty_appointment):
            appointment = self.appointment_arr[i]
            if appointment is not None and appointment.doctor == target_doctor:
                result.append(appointment)
        return result

    def find_appointments_by_date_steps(self, date: DateNew) -> tuple:
        """Поиск приёмов по дате с подсчётом количества шагов в AVL-дереве."""
        node = self.appointment_date_tree.root
        steps = 0
        found_node = None
        
        while node:
            steps += 1
            if date < node.key:
                node = node.left
            elif date > node.key:
                node = node.right
            else:
                found_node = node
                break

        appointments = MyList[Appointment]()
        if found_node:
            for idx in found_node.values:
                app = self.appointment_arr[idx]
                if app:
                    appointments.append(app)
        
        return appointments, steps

    # --- Формирование отчёта (связующая задача) ---
    def generate_report(self, filter_name: str = "", filter_doctor: str = "", filter_date: DateNew = None) -> MyList[str]:
        """
        Формирует отчёт с фильтрацией.
        
        Args:
            filter_name: фильтр по ФИО пациента (Справочник_1.Поле_2)
            filter_doctor: фильтр по врачу (Справочник_2.Поле_3)
            filter_date: фильтр по дате приёма (Справочник_2.Поле_4)
        """
        report_lines_internal = []
        for i in range(self.first_empty_appointment):
            appointment = self.appointment_arr[i]
            if appointment is None:
                continue

            # Применяем фильтры на приёме
            if filter_doctor and appointment.doctor != filter_doctor:
                continue
            if filter_date and appointment.appointment_date != filter_date:
                continue

            # Поиск пациента по OMS Policy через ХТ
            patient_search_result = self.patient_ht.search(appointment.oms_policy)
            patient_item = patient_search_result[0]
            if patient_item is None:
                print(f"Warning: Appointment for OMS {appointment.oms_policy} has no matching patient.")
                continue

            patient = self.patient_arr[patient_item.value]
            
            # Применяем фильтр по ФИО пациента
            if filter_name and patient.full_name != filter_name:
                continue

            line = (f"{patient.oms_policy};{patient.full_name};{patient.birth_date};"
                    f"{appointment.diagnosis};{appointment.doctor};{appointment.appointment_date}")
            report_lines_internal.append(line)

        result = MyList[str]()
        for line in reversed(report_lines_internal):
            result.append(line)

        return result

    # --- Отладка ---
    def get_patient_ht_debug(self):
        return str(self.patient_ht)

    def get_appointment_tree_debug(self):
        return repr(self.appointment_tree)

    def get_appointment_date_tree_debug(self):
        return repr(self.appointment_date_tree)