import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from database import RelationalDatabase
from DateNew import DateNew


db = RelationalDatabase()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Система учёта пациентов и приёмов")
        self.geometry("1200x700")

        self.patient_name_filter = ""
        self.appointment_doctor_filter = ""

        self.found_patients = None
        self.found_appointments = None

        # Меню
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Загрузить пациентов", command=self.load_patients)
        file_menu.add_command(label="Загрузить приёмы", command=self.load_appointments)
        file_menu.add_separator()
        file_menu.add_command(label="Сохранить пациентов", command=self.save_patients)
        file_menu.add_command(label="Сохранить приёмы", command=self.save_appointments)
        menubar.add_cascade(label="Файл", menu=file_menu)

        patient_menu = tk.Menu(menubar, tearoff=0)
        patient_menu.add_command(label="Добавить пациента", command=self.add_patient)
        patient_menu.add_command(label="Удалить пациента", command=self.delete_patient)
        patient_menu.add_command(label="Найти пациента", command=self.search_patient)
        menubar.add_cascade(label="Пациент", menu=patient_menu)

        appointment_menu = tk.Menu(menubar, tearoff=0)
        appointment_menu.add_command(label="Добавить приём", command=self.add_appointment)
        appointment_menu.add_command(label="Удалить приём", command=self.delete_appointment)
        appointment_menu.add_command(label="Найти приём", command=self.search_appointment)
        menubar.add_cascade(label="Приём", menu=appointment_menu)

        report_menu = tk.Menu(menubar, tearoff=0)
        report_menu.add_command(label="Сформировать отчёт", command=self.show_report_window)
        menubar.add_cascade(label="Отчёт", menu=report_menu)

        debug_menu = tk.Menu(menubar, tearoff=0)
        debug_menu.add_command(label="Отладка (текст)", command=self.show_debug_window)
        debug_menu.add_command(label="Визуализация СД", command=self.show_visualization_window)
        menubar.add_cascade(label="Отладка", menu=debug_menu)

        about_menu = tk.Menu(menubar, tearoff=0)
        about_menu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="О программе", menu=about_menu)

        self.config(menu=menubar)

        # Вкладки
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ============ ВКЛАДКА ПАЦИЕНТОВ ============
        self.patient_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.patient_frame, text="Пациенты")

        patient_toolbar = tk.Frame(self.patient_frame, relief=tk.RAISED, borderwidth=1)
        patient_toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        tk.Button(patient_toolbar, text="Добавить", command=self.add_patient).pack(side=tk.LEFT, padx=2)
        tk.Button(patient_toolbar, text="Удалить", command=self.delete_patient).pack(side=tk.LEFT, padx=2)
        tk.Button(patient_toolbar, text="Найти", command=self.search_patient).pack(side=tk.LEFT, padx=2)
        tk.Button(patient_toolbar, text="Загрузить", command=self.load_patients).pack(side=tk.LEFT, padx=2)
        tk.Button(patient_toolbar, text="Сохранить", command=self.save_patients).pack(side=tk.LEFT, padx=2)

        self.patient_table = ttk.Treeview(self.patient_frame, columns=("OMS_Policy", "Full_Name", "Birth_Date"), show="headings")
        for col in ("OMS_Policy", "Full_Name", "Birth_Date"):
            self.patient_table.heading(col, text=col)
            self.patient_table.column(col, anchor="center", width=250)
        self.patient_table.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Фильтр по ФИО (Поле 2)
        patient_filter_frame = tk.Frame(self.patient_frame)
        patient_filter_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
        tk.Label(patient_filter_frame, text="Фильтр по ФИО (Поле 2):").pack(side=tk.LEFT)
        self.patient_name_filter_entry = tk.Entry(patient_filter_frame, width=30)
        self.patient_name_filter_entry.pack(side=tk.LEFT, padx=3)
        tk.Button(patient_filter_frame, text="Применить", command=self.apply_patient_filter).pack(side=tk.LEFT, padx=3)
        tk.Button(patient_filter_frame, text="Сброс", command=self.clear_patient_filter).pack(side=tk.LEFT, padx=3)
        tk.Button(patient_filter_frame, text="Сброс всех фильтров", command=self.clear_search).pack(side=tk.LEFT, padx=3)

        # ============ ВКЛАДКА ПРИЁМОВ ============
        self.appointment_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.appointment_frame, text="Приёмы")

        appointment_toolbar = tk.Frame(self.appointment_frame, relief=tk.RAISED, borderwidth=1)
        appointment_toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        tk.Button(appointment_toolbar, text="Добавить", command=self.add_appointment).pack(side=tk.LEFT, padx=2)
        tk.Button(appointment_toolbar, text="Удалить", command=self.delete_appointment).pack(side=tk.LEFT, padx=2)
        tk.Button(appointment_toolbar, text="Найти", command=self.search_appointment).pack(side=tk.LEFT, padx=2)
        tk.Button(appointment_toolbar, text="Загрузить", command=self.load_appointments).pack(side=tk.LEFT, padx=2)
        tk.Button(appointment_toolbar, text="Сохранить", command=self.save_appointments).pack(side=tk.LEFT, padx=2)

        self.appointment_table = ttk.Treeview(self.appointment_frame, columns=("OMS_Policy", "Diagnosis", "Doctor", "Appointment_Date"), show="headings")
        for col in ("OMS_Policy", "Diagnosis", "Doctor", "Appointment_Date"):
            self.appointment_table.heading(col, text=col)
            self.appointment_table.column(col, anchor="center", width=200)
        self.appointment_table.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ИСПРАВЛЕНО: Фильтр по врачу (Поле 3)
        appointment_filter_frame = tk.Frame(self.appointment_frame)
        appointment_filter_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
        tk.Label(appointment_filter_frame, text="Фильтр по врачу (Поле 3):").pack(side=tk.LEFT)
        self.appointment_doctor_filter_entry = tk.Entry(appointment_filter_frame, width=30)
        self.appointment_doctor_filter_entry.pack(side=tk.LEFT, padx=3)
        tk.Button(appointment_filter_frame, text="Применить", command=self.apply_appointment_filter).pack(side=tk.LEFT, padx=3)
        tk.Button(appointment_filter_frame, text="Сброс", command=self.clear_appointment_filter).pack(side=tk.LEFT, padx=3)
        tk.Button(appointment_filter_frame, text="Сброс всех фильтров", command=self.clear_search).pack(side=tk.LEFT, padx=3)

        self.refresh_tables()

    def refresh_tables(self):
        for row in self.patient_table.get_children():
            self.patient_table.delete(row)

        if self.found_patients is None:
            patients_to_show = []
            for i in range(db.first_empty_patient):
                patient = db.patient_arr[i]
                if patient is not None:
                    patients_to_show.append(patient)
        else:
            patients_to_show = list(self.found_patients)

        for patient in patients_to_show:
            self.patient_table.insert("", tk.END, values=(patient.oms_policy, patient.full_name, str(patient.birth_date)))

        for row in self.appointment_table.get_children():
            self.appointment_table.delete(row)

        if self.found_appointments is None:
            appointments_to_show = []
            for i in range(db.first_empty_appointment):
                appointment = db.appointment_arr[i]
                if appointment is not None:
                    appointments_to_show.append(appointment)
        else:
            appointments_to_show = list(self.found_appointments)

        for appointment in appointments_to_show:
            self.appointment_table.insert("", tk.END, values=(appointment.oms_policy, appointment.diagnosis, appointment.doctor, str(appointment.appointment_date)))

    def load_patients(self):
        path = filedialog.askopenfilename(title="Файл с пациентами", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            try:
                db.load_patients(path)
                self.clear_search()
                self.refresh_tables()
                messagebox.showinfo("Успех", f"Пациенты загружены из {path}\nЗагружено: {db.first_empty_patient} записей")
            except Exception as e:
                messagebox.showerror("Ошибка загрузки пациентов", str(e))

    def load_appointments(self):
        path = filedialog.askopenfilename(title="Файл с приёмами", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            try:
                db.load_appointments(path)
                self.clear_search()
                self.refresh_tables()
                messagebox.showinfo("Успех", f"Приёмы загружены из {path}\nЗагружено: {db.first_empty_appointment} записей")
            except Exception as e:
                messagebox.showerror("Ошибка загрузки приёмов", str(e))

    def save_patients(self):
        path = filedialog.asksaveasfilename(title="Сохранить пациентов", defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    for i in range(db.first_empty_patient):
                        patient = db.patient_arr[i]
                        if patient:
                            f.write(f"{patient.oms_policy};{patient.full_name};{patient.birth_date}\n")
                messagebox.showinfo("Успех", f"Пациенты сохранены в {path}\nСохранено: {db.first_empty_patient} записей")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def save_appointments(self):
        path = filedialog.asksaveasfilename(title="Сохранить приёмы", defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    for i in range(db.first_empty_appointment):
                        appointment = db.appointment_arr[i]
                        if appointment:
                            f.write(f"{appointment.oms_policy};{appointment.diagnosis};{appointment.doctor};{appointment.appointment_date}\n")
                messagebox.showinfo("Успех", f"Приёмы сохранены в {path}\nСохранено: {db.first_empty_appointment} записей")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def add_patient(self):
        try:
            oms_str = simpledialog.askstring("Добавить пациента", "Полис ОМС (16-значное целое число):")
            if not oms_str:
                return
            oms = int(oms_str)
            full_name = simpledialog.askstring("Добавить пациента", "ФИО:")
            if not full_name:
                return
            birth_date_str = simpledialog.askstring("Добавить пациента", "Дата рождения (dd mmm yyyy, например: 15 Jan 1980):")
            if not birth_date_str:
                return

            success = db.add_patient(oms_policy=oms, full_name=full_name, birth_date_str=birth_date_str)
            if success:
                self.found_patients = None
                self.refresh_tables()
                messagebox.showinfo("Успех", "Пациент добавлен")
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить пациента (дубликат OMS или массив полон)")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def add_appointment(self):
        try:
            oms_str = simpledialog.askstring("Добавить приём", "Полис ОМС пациента:")
            if not oms_str:
                return
            oms = int(oms_str)
            diagnosis = simpledialog.askstring("Добавить приём", "Диагноз:")
            if not diagnosis:
                return
            doctor = simpledialog.askstring("Добавить приём", "Врач (ФИО):")
            if not doctor:
                return
            date_str = simpledialog.askstring("Добавить приём", "Дата приёма (dd mmm yyyy, например: 20 Nov 2024):")
            if not date_str:
                return

            success = db.add_appointment(oms_policy=oms, diagnosis=diagnosis, doctor=doctor, appointment_date_str=date_str)
            if success:
                self.found_appointments = None
                self.refresh_tables()
                messagebox.showinfo("Успех", "Приём добавлен")
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить приём (пациент не найден или массив полон)")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def delete_patient(self):
        sel = self.patient_table.focus()
        if not sel:
            messagebox.showerror("Ошибка", "Выберите пациента для удаления")
            return
        values = self.patient_table.item(sel)["values"]
        oms_policy = int(values[0])
        
        confirm = messagebox.askyesno("Подтверждение", 
            f"Удалить пациента с OMS {oms_policy}?\nВсе связанные приёмы также будут удалены!")
        if not confirm:
            return
            
        success = db.delete_patient(oms_policy)
        if success:
            self.clear_search()
            self.refresh_tables()
            messagebox.showinfo("Успех", f"Пациент с OMS {oms_policy} и связанные приёмы удалены")
        else:
            messagebox.showerror("Ошибка", f"Пациент с OMS {oms_policy} не найден")

    def delete_appointment(self):
        sel = self.appointment_table.focus()
        if not sel:
            messagebox.showerror("Ошибка", "Выберите приём для удаления")
            return
        values = self.appointment_table.item(sel)["values"]
        oms_policy = int(values[0])
        diagnosis = values[1]
        doctor = values[2]
        date_str = values[3]

        confirm = messagebox.askyesno("Подтверждение", 
            f"Удалить приём:\nOMS: {oms_policy}\nДиагноз: {diagnosis}\nВрач: {doctor}\nДата: {date_str}")
        if not confirm:
            return

        success = db.delete_appointment(target_oms=oms_policy, target_diagnosis=diagnosis, target_doctor=doctor, target_date_str=date_str)
        if success:
            self.found_appointments = None
            self.refresh_tables()
            messagebox.showinfo("Успех", "Приём удалён")
        else:
            messagebox.showerror("Ошибка", "Приём не найден")

    # ========== ПОИСК В СПРАВОЧНИКАХ ==========
    
    def search_patient(self):
        """Поиск пациента по всем полям"""
        try:
            oms_str = simpledialog.askstring("Найти пациента", "Полис ОМС:")
            if not oms_str:
                return
            oms = int(oms_str)
            
            full_name = simpledialog.askstring("Найти пациента", "ФИО:")
            if full_name is None:
                return
            
            birth_date_str = simpledialog.askstring("Найти пациента", "Дата рождения (dd mmm yyyy, например: 15 Jan 1980):")
            if not birth_date_str:
                return

            patient, steps = db.find_patient_by_all_fields_steps(oms, full_name, birth_date_str)
            
            if patient:
                messagebox.showinfo("Результат поиска", 
                    f"Пациент найден!\n\n"
                    f"OMS Policy: {patient.oms_policy}\n"
                    f"ФИО: {patient.full_name}\n"
                    f"Дата рождения: {patient.birth_date}\n\n"
                    f"Количество шагов поиска в ХТ: {steps}")
            else:
                messagebox.showinfo("Результат поиска", 
                    f"Пациент не найден\n\n"
                    f"Количество шагов поиска в ХТ: {steps}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def search_appointment(self):
        """Поиск приёма по всем полям"""
        try:
            oms_str = simpledialog.askstring("Найти приём", "Полис ОМС пациента:")
            if not oms_str:
                return
            oms = int(oms_str)
            
            diagnosis = simpledialog.askstring("Найти приём", "Диагноз:")
            if diagnosis is None:
                return
            
            doctor = simpledialog.askstring("Найти приём", "Врач (ФИО):")
            if doctor is None:
                return
            
            date_str = simpledialog.askstring("Найти приём", "Дата приёма (dd mmm yyyy, например: 20 Nov 2024):")
            if not date_str:
                return

            appointment, steps = db.find_appointment_by_all_fields_steps(oms, diagnosis, doctor, date_str)
            
            if appointment:
                messagebox.showinfo("Результат поиска", 
                    f"Приём найден!\n\n"
                    f"OMS Policy: {appointment.oms_policy}\n"
                    f"Диагноз: {appointment.diagnosis}\n"
                    f"Врач: {appointment.doctor}\n"
                    f"Дата приёма: {appointment.appointment_date}\n\n"
                    f"Количество шагов поиска в AVL-дереве: {steps}")
            else:
                messagebox.showinfo("Результат поиска", 
                    f"Приём не найден\n\n"
                    f"Количество шагов поиска в AVL-дереве: {steps}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    # ========== ФИЛЬТРЫ СПРАВОЧНИКОВ ==========
    
    def apply_patient_filter(self):
        """Фильтр пациентов по ФИО (Поле 2) с выводом количества шагов"""
        self.patient_name_filter = self.patient_name_filter_entry.get().strip()
        if self.patient_name_filter:
            self.found_patients = db.filter_patients_by_name(self.patient_name_filter)
            steps = db.first_empty_patient
            messagebox.showinfo("Результат поиска", 
                f"Найдено пациентов: {len(self.found_patients)}\n"
                f"Шагов поиска (перебор массива): до {steps}")
        else:
            self.found_patients = None
        self.refresh_tables()

    def clear_patient_filter(self):
        self.patient_name_filter = ""
        self.patient_name_filter_entry.delete(0, tk.END)
        self.found_patients = None
        self.refresh_tables()

    def apply_appointment_filter(self):
        """Фильтр приёмов по врачу (Поле 3) с выводом количества шагов"""
        self.appointment_doctor_filter = self.appointment_doctor_filter_entry.get().strip()
        if self.appointment_doctor_filter:
            self.found_appointments = db.filter_appointments_by_doctor(self.appointment_doctor_filter)
            steps = db.first_empty_appointment
            messagebox.showinfo("Результат поиска", 
                f"Найдено приёмов: {len(self.found_appointments)}\n"
                f"Шагов поиска (перебор массива): до {steps}")
        else:
            self.found_appointments = None
        self.refresh_tables()

    def clear_appointment_filter(self):
        self.appointment_doctor_filter = ""
        self.appointment_doctor_filter_entry.delete(0, tk.END)
        self.found_appointments = None
        self.refresh_tables()

    def clear_search(self):
        """Сброс всех фильтров"""
        self.found_patients = None
        self.found_appointments = None
        self.patient_name_filter_entry.delete(0, tk.END)
        self.appointment_doctor_filter_entry.delete(0, tk.END)
        self.refresh_tables()

    # ========== ОТЧЁТ С ФИЛЬТРАМИ ==========
    
    def show_report_window(self):
        """Окно отчёта с фильтрами"""
        win = tk.Toplevel(self)
        win.title("Отчёт: Пациенты и Приёмы")
        win.geometry("1200x650")

        # Заголовок
        info_frame = tk.Frame(win, bg="#e8f4f8", height=40)
        info_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        info_frame.pack_propagate(False)
        tk.Label(info_frame, text="Связующая задача: объединение данных из двух справочников по OMS Policy", 
                 font=("Arial", 10, "bold"), bg="#e8f4f8").pack(pady=10)

        # Панель фильтров
        filter_frame = tk.LabelFrame(win, text="Фильтры отчёта", font=("Arial", 10, "bold"), padx=10, pady=10)
        filter_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Фильтр по ФИО (Справочник 1, Поле 2)
        row1 = tk.Frame(filter_frame)
        row1.pack(fill=tk.X, pady=3)
        tk.Label(row1, text="ФИО пациента (Справ.1, Поле 2):", width=28, anchor="w").pack(side=tk.LEFT)
        filter_name_entry = tk.Entry(row1, width=30)
        filter_name_entry.pack(side=tk.LEFT, padx=5)

        # Фильтр по Врачу (Справочник 2, Поле 3)
        row2 = tk.Frame(filter_frame)
        row2.pack(fill=tk.X, pady=3)
        tk.Label(row2, text="Врач (Справ.2, Поле 3):", width=28, anchor="w").pack(side=tk.LEFT)
        filter_doctor_entry = tk.Entry(row2, width=30)
        filter_doctor_entry.pack(side=tk.LEFT, padx=5)

        # Фильтр по Дате приёма (Справочник 2, Поле 4)
        row3 = tk.Frame(filter_frame)
        row3.pack(fill=tk.X, pady=3)
        tk.Label(row3, text="Дата приёма (Справ.2, Поле 4):", width=28, anchor="w").pack(side=tk.LEFT)
        filter_date_entry = tk.Entry(row3, width=30)
        filter_date_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(row3, text="(формат: dd mmm yyyy, например: 20 Nov 2024)", font=("Arial", 8), fg="gray").pack(side=tk.LEFT, padx=5)

        # Кнопки управления фильтрами
        button_row = tk.Frame(filter_frame)
        button_row.pack(fill=tk.X, pady=5)
        tk.Button(button_row, text="Применить фильтры", command=lambda: self.apply_report_filters(
            win, filter_name_entry, filter_doctor_entry, filter_date_entry, report_table, stats_label
        ), bg="#4CAF50", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(button_row, text="Сбросить фильтры", command=lambda: self.reset_report_filters(
            win, filter_name_entry, filter_doctor_entry, filter_date_entry, report_table, stats_label
        )).pack(side=tk.LEFT, padx=5)

        # Таблица отчёта
        report_table = ttk.Treeview(
            win,
            columns=("OMS_Policy", "Full_Name", "Birth_Date", "Diagnosis", "Doctor", "Appointment_Date"),
            show="headings"
        )
        for col in ("OMS_Policy", "Full_Name", "Birth_Date", "Diagnosis", "Doctor", "Appointment_Date"):
            report_table.heading(col, text=col)
            report_table.column(col, anchor="center", width=150)
        report_table.pack(fill="both", expand=True, padx=10, pady=5)

        # Нижняя панель со статистикой
        stats_label = tk.Label(win, text="", font=("Arial", 9))
        stats_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        button_frame = tk.Frame(win)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        tk.Button(button_frame, text="Сохранить отчёт", command=lambda: self.save_current_report(report_table)).pack(side=tk.RIGHT, padx=5)

        # Изначально показываем все данные без фильтров
        self.load_report_data(report_table, stats_label, "", "", None)

    def apply_report_filters(self, win, name_entry, doctor_entry, date_entry, report_table, stats_label):
        """Применяет фильтры к отчёту"""
        filter_name = name_entry.get().strip()
        filter_doctor = doctor_entry.get().strip()
        date_text = date_entry.get().strip()
        
        filter_date = None
        if date_text:
            try:
                filter_date = DateNew(date_text)
            except (ValueError, TypeError) as e:
                messagebox.showerror("Ошибка", f"Некорректный формат даты: {e}\nИспользуйте: dd mmm yyyy")
                return

        self.load_report_data(report_table, stats_label, filter_name, filter_doctor, filter_date)

    def reset_report_filters(self, win, name_entry, doctor_entry, date_entry, report_table, stats_label):
        """Сбрасывает фильтры отчёта"""
        name_entry.delete(0, tk.END)
        doctor_entry.delete(0, tk.END)
        date_entry.delete(0, tk.END)
        self.load_report_data(report_table, stats_label, "", "", None)

    def load_report_data(self, report_table, stats_label, filter_name, filter_doctor, filter_date):
        """Загружает данные в отчёт с учётом фильтров"""
        # Очищаем таблицу
        for row in report_table.get_children():
            report_table.delete(row)

        # Генерируем отчёт с фильтрами
        report_lines = db.generate_report(filter_name, filter_doctor, filter_date)
        
        # Подсчёт шагов поиска
        total_steps = 0
        for line in report_lines:
            parts = line.split(';')
            if len(parts) >= 6:
                oms = int(parts[0])
                _, steps = db.find_patient_steps(oms)
                total_steps += steps
                
                row = (parts[0], parts[1], parts[2], parts[3], parts[4], parts[5])
                report_table.insert("", tk.END, values=row)

        # Обновляем статистику
        filter_info = []
        if filter_name:
            filter_info.append(f"ФИО='{filter_name}'")
        if filter_doctor:
            filter_info.append(f"Врач='{filter_doctor}'")
        if filter_date:
            filter_info.append(f"Дата={filter_date}")
        
        filter_text = f" (фильтры: {', '.join(filter_info)})" if filter_info else ""
        stats_text = f"Записей в отчёте: {len(report_lines)}{filter_text} | Общее количество шагов поиска в ХТ: {total_steps}"
        stats_label.config(text=stats_text)

    def save_current_report(self, report_table):
        """Сохраняет текущее содержимое отчёта"""
        rows = []
        for item in report_table.get_children():
            values = report_table.item(item)["values"]
            rows.append(';'.join(str(v) for v in values))

        if not rows:
            messagebox.showinfo("Информация", "Отчёт пуст, нечего сохранять")
            return

        save_path = filedialog.asksaveasfilename(
            title="Сохранить отчёт",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if save_path:
            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write("OMS_Policy;Full_Name;Birth_Date;Diagnosis;Doctor;Appointment_Date\n")
                    for line in rows:
                        f.write(line + "\n")
                messagebox.showinfo("Успех", f"Отчёт сохранён в {save_path}\nЗаписей: {len(rows)}")
            except Exception as e:
                messagebox.showerror("Ошибка сохранения отчёта", str(e))

    # ========== ОТЛАДКА ==========
    
    def show_debug_window(self):
        win = tk.Toplevel(self)
        win.title("Отладка структур данных (текстовый вывод)")
        win.geometry("900x650")

        text = tk.Text(win, wrap="word", font=("Consolas", 9))
        scrollbar = tk.Scrollbar(win, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(fill="both", expand=True, padx=10, pady=10)

        text.insert("end", "="*80 + "\n")
        text.insert("end", "[HashTable Patients (OMS Policy -> Index)]\n")
        text.insert("end", "="*80 + "\n")
        text.insert("end", db.get_patient_ht_debug() + "\n\n")

        text.insert("end", "="*80 + "\n")
        text.insert("end", "[AVL Tree Appointments (OMS Policy -> Indices)]\n")
        text.insert("end", "="*80 + "\n")
        text.insert("end", db.get_appointment_tree_debug() + "\n\n")

        text.insert("end", "="*80 + "\n")
        text.insert("end", "[AVL Tree Appointments (Date -> Indices)]\n")
        text.insert("end", "="*80 + "\n")
        text.insert("end", db.get_appointment_date_tree_debug() + "\n")

        text.config(state="disabled")

    def show_visualization_window(self):
        """Открывает окно визуализации структур данных"""
        try:
            from visualization import VisualizationWindow
            VisualizationWindow(self, db)
        except ImportError as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить модуль визуализации:\n{e}\n\nУбедитесь, что файл visualization.py находится в той же папке.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при открытии визуализации:\n{e}")

    def show_about(self):
        messagebox.showinfo(
            "О программе",
            "Система учёта пациентов и приёмов\n"
            "Курсовая работа 2024-25\n\n"
            "Структуры данных:\n"
            "• Хеш-таблица (метод: середина квадрата, открытая адресация)\n"
            "• AVL-дерево (цепочки для неуникальных ключей)\n"
            "• Циклический связный список\n\n"
            "Справочники:\n"
            "1. Пациенты: OMS, ФИО, Дата рождения\n"
            "2. Приёмы: OMS, Диагноз, Врач, Дата приёма\n\n"
            "Фильтры:\n"
            "• Справочник 1, Поле 2 (ФИО)\n"
            "• Справочник 2, Поле 3 (Врач)\n\n"
            "Отчёт с фильтрацией:\n"
            "• ФИО пациента (Справ.1, Поле 2)\n"
            "• Врач (Справ.2, Поле 3)\n"
            "• Дата приёма (Справ.2, Поле 4)"
        )


if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Критическая ошибка", f"Не удалось запустить приложение:\n{e}")
        root.destroy()