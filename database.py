

import ctypes
from Patient import Patient
from Appointment import Appointment
from DateNew import DateNew
from hash_table import HashTable
from avl_tree import AVLTree
from List import MyList
# --- ИМПОРТ ИЗ MASSIVE.PY ---
from massive import patients_to_array, appointments_to_array
# ----------------------------


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
        self.patient_ht = HashTable() # Использует статическую ХТ с серединой квадрата
        # AVL-дерево для приёмов по OMS Policy пациента (ключ - int)
        self.appointment_tree = AVLTree[int]()
        # AVL-дерево для приёмов по дате приёма (ключ - DateNew)
        self.appointment_date_tree = AVLTree[DateNew]()

        # Счётчики первых пустых ячеек в массивах
        self.first_empty_patient = 0
        self.first_empty_appointment = 0

    # --- Загрузка из файлов ---
    def load_patients(self, filename: str):
        # Используем адаптированный модуль загрузки
        # from massive import patients_to_array # <-- Импорт уже добавлен в начало файла
        self.first_empty_patient = patients_to_array(filename, self.patient_ht, self.patient_arr, self.first_empty_patient)
        # Убираем print заглушку
        # print(f"Loading patients from {filename} - requires 'massive.py' implementation.")

    def load_appointments(self, filename: str):
        # Используем адаптированный модуль загрузки
        # from massive import appointments_to_array # <-- Импорт уже добавлен в начало файла
        self.first_empty_appointment = appointments_to_array(
            filename, self.appointment_tree, self.patient_ht, self.appointment_arr,
            self.first_empty_appointment, self.appointment_date_tree
        )
        # Убираем print заглушку
        # print(f"Loading appointments from {filename} - requires 'massive.py' implementation.")

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

        # Попытка вставить в ХТ. Возвращает индекс вставки или -1 при дубликате.
        inserted_idx = self.patient_ht.insert(patient.oms_policy, self.first_empty_patient)
        if inserted_idx == -1:
            print(f"Patient with OMS Policy {oms_policy} already exists.")
            return False

        # Запись в массив
        self.patient_arr[self.first_empty_patient] = patient
        self.first_empty_patient += 1
        return True

    def add_appointment(self, oms_policy: int, diagnosis: str, doctor: str, appointment_date_str: str) -> bool:
        if self.first_empty_appointment >= MAX_SIZE:
            print("Maximum size of appointment array has been reached")
            return False

        # Проверка существования пациента
        if self.patient_ht.search(oms_policy)[0] is None:
            print(f"Cannot add appointment: Patient with OMS Policy {oms_policy} does not exist.")
            return False

        try:
            appointment_date = DateNew(appointment_date_str)
            appointment = Appointment(oms_policy=oms_policy, diagnosis=diagnosis, doctor=doctor, appointment_date=appointment_date)
        except (ValueError, TypeError) as e:
            print(f"Failed to add appointment: {e}")
            return False

        # Вставка в деревья
        # self.appointment_tree.insert(oms_policy, self.first_empty_appointment) # Устаревший вызов
        self.appointment_tree.insert(appointment.oms_policy, self.first_empty_appointment) # Правильный ключ
        self.appointment_date_tree.insert(appointment.appointment_date, self.first_empty_appointment)

        # Запись в массив
        self.appointment_arr[self.first_empty_appointment] = appointment
        self.first_empty_appointment += 1
        return True

    # --- Удаление ---
    def delete_patient(self, oms_policy: int) -> bool:
        # Поиск пациента в ХТ
        search_result = self.patient_ht.search(oms_policy)
        item = search_result[0]
        if item is None:
            print(f"Patient with OMS Policy {oms_policy} not found.")
            return False

        patient_index = item.value
        patient_to_delete = self.patient_arr[patient_index]

        # Удаление пациента из ХТ
        self.patient_ht.delete(oms_policy)

        # Обновление массива пациента (перемещение последнего элемента на место удалённого)
        self.first_empty_patient -= 1
        moved_patient = self.patient_arr[self.first_empty_patient]
        self.patient_arr[self.first_empty_patient] = None

        if patient_index != self.first_empty_patient:
            self.patient_arr[patient_index] = moved_patient
            if moved_patient is not None:
                # Обновление индекса в ХТ для перемещённого пациента
                # Нужно удалить старый индекс и вставить новый для moved_patient
                # self.patient_ht.delete(moved_patient.oms_policy) # Удаляем старый индекс
                # self.patient_ht.insert(moved_patient.oms_policy, patient_index) # Вставляем новый
                # Текущая ХТ не поддерживает изменение индекса напрямую.
                # Правильный способ - пересоздать запись.
                # Удаляем старую запись (она уже удалена выше)
                # Вставляем с новым индексом
                self.patient_ht.insert(moved_patient.oms_policy, patient_index)
        else:
            self.patient_arr[patient_index] = None

        # Каскадное удаление приёмов этого пациента
        # Находим узел в дереве по OMS Policy
        node = self.appointment_tree.find(oms_policy)
        if node:
            # Создаём копию цепочки индексов, так как она будет меняться при удалении
            indices_to_remove = list(node.values)
            for app_index in indices_to_remove:
                self._remove_appointment_index(app_index) # Используем вспомогательный метод
            # Удаляем сам узел (так как все его значения удалены)
            self.appointment_tree.delete_node(oms_policy)

        print(f"Patient with OMS Policy {oms_policy} and associated appointments deleted.")
        return True

    def _remove_appointment_index(self, index: int):
        """Вспомогательный метод для удаления приёма по индексу с обновлением деревьев."""
        if index >= self.first_empty_appointment or self.appointment_arr[index] is None:
            return

        # Уменьшаем счётчик и получаем последний элемент
        self.first_empty_appointment -= 1
        moved_appointment = self.appointment_arr[self.first_empty_appointment]
        # Очищаем старое место последнего элемента
        self.appointment_arr[self.first_empty_appointment] = None

        # Удаляем старый индекс из всех деревьев
        # Нужно найти, какие ключи использовались для этого индекса
        app_to_remove = self.appointment_arr[index]
        if app_to_remove:
            # Удаляем index из цепочек в деревьях
            # Это делается через delete_value (ключ, значение)
            # Удаляем по старому ключу и старому индексу
            self.appointment_tree.delete_value(app_to_remove.oms_policy, index)
            self.appointment_date_tree.delete_value(app_to_remove.appointment_date, index)

        # Если удаляемый индекс не был последним, перемещаем последний элемент на его место
        if index != self.first_empty_appointment:
            self.appointment_arr[index] = moved_appointment
            if moved_appointment is not None:
                # Обновляем индекс в деревьях для перемещённого приёма
                # Удаляем старый индекс (self.first_empty_appointment)
                self.appointment_tree.delete_value(moved_appointment.oms_policy, self.first_empty_appointment)
                self.appointment_date_tree.delete_value(moved_appointment.appointment_date, self.first_empty_appointment)
                # Вставляем новый индекс (index)
                self.appointment_tree.insert(moved_appointment.oms_policy, index)
                self.appointment_date_tree.insert(moved_appointment.appointment_date, index)
        else:
            # Если удаляемый был последним, просто очищаем его ячейку в массиве (уже сделано)
            self.appointment_arr[index] = None


    def delete_appointment(self, target_oms: int, target_diagnosis: str, target_doctor: str, target_date_str: str) -> bool:
        # Парсим дату
        try:
            target_date = DateNew(target_date_str)
        except (ValueError, TypeError) as e:
            print(f"Invalid date format for deletion: {e}")
            return False

        # Ищем в массиве приёмов (можно было бы искать через деревья, но для точного совпадения проще перебрать)
        # Однако, мы можем сначала сузить поиск, используя дерево по OMS Policy
        node = self.appointment_tree.find(target_oms)
        if not node:
             print(f"No appointments found for OMS Policy {target_oms} to match for deletion.")
             return False

        found_index = -1
        # Перебираем индексы из цепочки для этого OMS Policy
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

        # Нашли индекс, теперь удаляем
        # Удаляем индекс из деревьев
        self.appointment_tree.delete_value(target_oms, found_index)
        self.appointment_date_tree.delete_value(target_date, found_index)

        # Вызываем вспомогательный метод для обновления массива и индексов
        self._remove_appointment_index(found_index)
        print(f"Appointment deleted.")
        return True


    # --- Поиск (возвращает количество шагов) ---
    def find_patient_steps(self, oms_policy: int) -> tuple:
        """Возвращает (найденный_пациент, количество_шагов) или (None, шаги)."""
        result = self.patient_ht.search(oms_policy)
        item = result[0]
        steps = result[1]
        patient = self.patient_arr[item.value] if item else None
        return patient, steps

    def find_appointments_by_oms_steps(self, oms_policy: int) -> tuple:
        """Возвращает (список_приёмов, количество_шагов_поиска_в_AVL) или (None, шаги)."""
        # AVLTree.find не возвращает количество шагов, нужно вручную
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

    def filter_appointments_by_date(self, date: DateNew) -> MyList[Appointment]:
        """Фильтр для Справочника_2.Поле_4 (Appointment Date)."""
        result = MyList[Appointment]()
        node = self.appointment_date_tree.find(date)
        if node:
            for index in node.values:
                appointment = self.appointment_arr[index]
                if appointment:
                    result.append(appointment)
        return result

    # --- Формирование отчёта (связующая задача) ---
    def generate_report(self) -> MyList[str]:
        """Формирует отчёт, объединяя Patient и Appointment по OMS Policy."""
        # Собираем строки отчёта в обычный Python-список
        # Это гарантирует порядок обхода массива приёмов (от 0 до first_empty_appointment-1)
        report_lines_internal = []
        for i in range(self.first_empty_appointment):
            appointment = self.appointment_arr[i]
            if appointment is None:
                continue

            # Поиск пациента по OMS Policy через ХТ (без перебора)
            patient_search_result = self.patient_ht.search(appointment.oms_policy)
            patient_item = patient_search_result[0]
            if patient_item is None:
                # Пациент был удалён, но приём остался - логическая ошибка, но пропускаем
                print(f"Warning: Appointment for OMS {appointment.oms_policy} has no matching patient.")
                continue

            patient = self.patient_arr[patient_item.value]
            line = (f"{patient.oms_policy};{patient.full_name};{patient.birth_date};"
                    f"{appointment.diagnosis};{appointment.doctor};{appointment.appointment_date}")
            report_lines_internal.append(line)

        # Создаём MyList и добавляем элементы в обратном порядке
        # Это компенсирует добавление в начало, и итоговый порядок в MyList
        # будет соответствовать порядку обхода массива (0, 1, 2, ...)
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

    # --- Устаревшие методы из старой версии ---
    # def set_size_hash_table(self, capacity: int):
    #     # Устарело, так как ХТ статическая
    #     pass # Или вызвать ошибку

    # def _update_index_in_tree(self, tree, key, old_index, new_index):
    #     # Не используется напрямую в текущей реализации перемещения
    #     pass

