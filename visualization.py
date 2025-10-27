# visualization.py - Модуль визуализации структур данных

import tkinter as tk
from tkinter import ttk

class VisualizationWindow(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.title("Визуализация структур данных")
        self.geometry("1400x800")
        
        # Notebook для разных визуализаций
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладки
        self.create_hash_table_tab()
        self.create_avl_oms_tab()
        self.create_avl_date_tab()
        
    def create_hash_table_tab(self):
        """Визуализация хеш-таблицы"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Хеш-таблица (ХТ пациентов)")
        
        # Верхняя панель с информацией
        info_frame = tk.Frame(frame, bg="#e8f4f8", height=70)
        info_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        info_frame.pack_propagate(False)
        
        ht = self.db.patient_ht
        capacity = ht.capacity
        size = ht.size
        load_factor = size / capacity if capacity > 0 else 0
        
        tk.Label(info_frame, text="Хеш-таблица пациентов", font=("Arial", 14, "bold"), bg="#e8f4f8").pack(pady=5)
        
        stats_text = f"Размер: {capacity} | Занято: {size} | Загруженность: {load_factor:.1%} | Метод: середина квадрата | Пробирование: линейное"
        tk.Label(info_frame, text=stats_text, font=("Arial", 10), bg="#e8f4f8").pack()
        
        # Canvas для визуализации
        canvas_frame = tk.Frame(frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(canvas_frame, bg="white")
        scrollbar_y = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar_x = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Рисуем хеш-таблицу
        self.draw_hash_table(canvas, ht)
        
    def draw_hash_table(self, canvas, ht):
        """Рисует хеш-таблицу с ячейками"""
        cell_height = 45
        cell_width = 750
        start_x = 30
        start_y = 30
        
        # Заголовок
        canvas.create_text(start_x + cell_width // 2, start_y - 15, 
                          text="Структура хеш-таблицы (показаны занятые/удалённые ячейки + первые 30 для примера)",
                          font=("Arial", 11, "bold"), fill="#333")
        
        # Собираем только занятые/удалённые ячейки для отображения
        cells_to_draw = []
        for i in range(ht.capacity):
            slot = ht._elements[i]
            if slot.status != 0:  # Не пустая
                cells_to_draw.append((i, slot))
        
        # Если ячеек мало, показываем первые 30 ячеек для примера структуры
        if len(cells_to_draw) < 30:
            cells_to_draw = [(i, ht._elements[i]) for i in range(min(30, ht.capacity))]
        
        y_offset = start_y
        for idx, slot in cells_to_draw:
            # Цвет в зависимости от статуса
            if slot.status == 0:
                color = "#f5f5f5"  # Пустая (светло-серый)
                text_color = "#999"
                border_color = "#ddd"
            elif slot.status == 1:
                color = "#90EE90"  # Занята (светло-зелёный)
                text_color = "black"
                border_color = "#2d862d"
            else:  # status == 2
                color = "#FFB6C1"  # Удалена (светло-розовый)
                text_color = "#666"
                border_color = "#d63384"
            
            # Рисуем ячейку
            canvas.create_rectangle(start_x, y_offset, start_x + cell_width, y_offset + cell_height,
                                   fill=color, outline=border_color, width=2)
            
            # Индекс ячейки (hash2)
            canvas.create_text(start_x + 60, y_offset + cell_height // 2,
                              text=f"[{idx}]", font=("Courier", 11, "bold"), anchor="center")
            
            # Статус
            status_text = {0: "EMPTY", 1: "OCCUPIED", 2: "DELETED"}[slot.status]
            canvas.create_text(start_x + 150, y_offset + cell_height // 2,
                              text=status_text, font=("Courier", 10), fill=text_color, anchor="center")
            
            if slot.key is not None:
                # Hash1 (первичный хеш - результат функции "середина квадрата")
                hash1 = ht.hash(slot.key)
                canvas.create_text(start_x + 260, y_offset + cell_height // 2,
                                  text=f"h₁={hash1}", font=("Courier", 10, "bold"), fill="blue", anchor="center")
                
                # Ключ (OMS Policy)
                key_text = str(slot.key)
                if len(key_text) > 16:
                    key_text = key_text[:16] + "..."
                canvas.create_text(start_x + 450, y_offset + cell_height // 2,
                                  text=f"OMS: {key_text}", font=("Courier", 10), fill=text_color, anchor="center")
                
                # Значение (индекс в массиве пациентов)
                canvas.create_text(start_x + 650, y_offset + cell_height // 2,
                                  text=f"→ arr[{slot.value}]", font=("Courier", 10, "bold"), fill="green", anchor="center")
            
            y_offset += cell_height + 3
        
        # Легенда
        legend_y = y_offset + 30
        legend_x = start_x
        
        canvas.create_text(legend_x + 350, legend_y - 15, text="Легенда:", font=("Arial", 11, "bold"))
        
        # Занята
        canvas.create_rectangle(legend_x, legend_y, legend_x + 35, legend_y + 25, fill="#90EE90", outline="#2d862d", width=2)
        canvas.create_text(legend_x + 55, legend_y + 12, text="Занята (status=1)", anchor="w", font=("Arial", 10))
        
        # Удалена
        canvas.create_rectangle(legend_x + 200, legend_y, legend_x + 235, legend_y + 25, fill="#FFB6C1", outline="#d63384", width=2)
        canvas.create_text(legend_x + 255, legend_y + 12, text="Удалена (status=2)", anchor="w", font=("Arial", 10))
        
        # Пустая
        canvas.create_rectangle(legend_x + 420, legend_y, legend_x + 455, legend_y + 25, fill="#f5f5f5", outline="#ddd", width=2)
        canvas.create_text(legend_x + 475, legend_y + 12, text="Пустая (status=0)", anchor="w", font=("Arial", 10))
        
        # Пояснения
        explanation_y = legend_y + 50
        canvas.create_text(start_x, explanation_y, 
                          text="h₁ - первичный хеш (метод 'середина квадрата'), [index] - текущая позиция в таблице (hash2)",
                          anchor="w", font=("Arial", 9, "italic"), fill="#666")
        
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    def create_avl_oms_tab(self):
        """Визуализация AVL-дерева по OMS"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="AVL-дерево (приёмы по OMS)")
        
        # Информация
        info_frame = tk.Frame(frame, bg="#e8f4f8", height=70)
        info_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        info_frame.pack_propagate(False)
        
        tree = self.db.appointment_tree
        node_count = len(tree)
        height = self.get_tree_height(tree.root)
        
        tk.Label(info_frame, text="AVL-дерево приёмов (ключ: OMS Policy)", font=("Arial", 14, "bold"), bg="#e8f4f8").pack(pady=5)
        
        stats_text = f"Узлов: {node_count} | Высота дерева: {height} | Неуникальные ключи → цепочки индексов"
        tk.Label(info_frame, text=stats_text, font=("Arial", 10), bg="#e8f4f8").pack()
        
        # Canvas
        canvas_frame = tk.Frame(frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(canvas_frame, bg="white")
        scrollbar_y = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar_x = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Рисуем дерево
        if tree.root:
            self.draw_avl_tree(canvas, tree.root, canvas_width=1300)
        else:
            canvas.create_text(400, 200, text="Дерево пусто", font=("Arial", 16), fill="gray")
        
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    def create_avl_date_tab(self):
        """Визуализация AVL-дерева по датам"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="AVL-дерево (приёмы по датам)")
        
        # Информация
        info_frame = tk.Frame(frame, bg="#e8f4f8", height=70)
        info_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        info_frame.pack_propagate(False)
        
        tree = self.db.appointment_date_tree
        node_count = len(tree)
        height = self.get_tree_height(tree.root)
        
        tk.Label(info_frame, text="AVL-дерево приёмов (ключ: Дата приёма)", font=("Arial", 14, "bold"), bg="#e8f4f8").pack(pady=5)
        
        stats_text = f"Узлов: {node_count} | Высота дерева: {height} | Одинаковые даты → цепочки индексов"
        tk.Label(info_frame, text=stats_text, font=("Arial", 10), bg="#e8f4f8").pack()
        
        # Canvas
        canvas_frame = tk.Frame(frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        canvas = tk.Canvas(canvas_frame, bg="white")
        scrollbar_y = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar_x = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Рисуем дерево
        if tree.root:
            self.draw_avl_tree(canvas, tree.root, canvas_width=1300)
        else:
            canvas.create_text(400, 200, text="Дерево пусто", font=("Arial", 16), fill="gray")
        
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    def get_tree_height(self, node):
        """Вычисляет высоту дерева"""
        if node is None:
            return 0
        return node.height
    
    def draw_avl_tree(self, canvas, root, canvas_width=1300):
        """Рисует AVL-дерево"""
        if root is None:
            return
        
        # Параметры отрисовки
        node_radius = 32
        level_height = 95
        
        # Вычисляем позиции узлов
        positions = {}
        self.calculate_positions(root, positions, canvas_width // 2, 60, canvas_width // 4, level_height)
        
        # Рисуем рёбра
        self.draw_edges(canvas, root, positions, node_radius)
        
        # Рисуем узлы
        self.draw_nodes(canvas, root, positions, node_radius)
        
        # Легенда
        self.draw_tree_legend(canvas, canvas_width)
    
    def calculate_positions(self, node, positions, x, y, offset, level_height):
        """Рекурсивно вычисляет позиции узлов"""
        if node is None:
            return
        
        positions[id(node)] = (x, y)
        
        if node.left:
            self.calculate_positions(node.left, positions, x - offset, y + level_height, offset // 2, level_height)
        if node.right:
            self.calculate_positions(node.right, positions, x + offset, y + level_height, offset // 2, level_height)
    
    def draw_edges(self, canvas, node, positions, radius):
        """Рисует рёбра дерева"""
        if node is None:
            return
        
        x1, y1 = positions[id(node)]
        
        if node.left:
            x2, y2 = positions[id(node.left)]
            canvas.create_line(x1, y1 + radius, x2, y2 - radius, width=2, fill="#555", arrow=tk.LAST)
            self.draw_edges(canvas, node.left, positions, radius)
        
        if node.right:
            x2, y2 = positions[id(node.right)]
            canvas.create_line(x1, y1 + radius, x2, y2 - radius, width=2, fill="#555", arrow=tk.LAST)
            self.draw_edges(canvas, node.right, positions, radius)
    
    def draw_nodes(self, canvas, node, positions, radius):
        """Рисует узлы дерева"""
        if node is None:
            return
        
        x, y = positions[id(node)]
        
        # Баланс фактор для цвета
        balance = self.get_balance(node)
        if abs(balance) <= 1:
            color = "#90EE90"  # Сбалансирован (зелёный)
            border_color = "#2d862d"
        else:
            color = "#FFB6C1"  # Несбалансирован (розовый) - не должно быть в AVL!
            border_color = "#d63384"
        
        # Круг узла
        canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                          fill=color, outline=border_color, width=3)
        
        # Ключ
        key_text = str(node.key)
        if len(key_text) > 16:
            key_text = key_text[:13] + "..."
        canvas.create_text(x, y - 10, text=key_text, font=("Courier", 10, "bold"))
        
        # Высота узла
        canvas.create_text(x, y + 12, text=f"h={node.height}", font=("Courier", 9), fill="blue")
        
        # Цепочка индексов (количество элементов в цепочке)
        chain_count = len(node.values)
        if chain_count > 0:
            chain_text = f"цепь[{chain_count}]"
            # Рисуем информацию о цепочке справа от узла
            canvas.create_rectangle(x + radius + 5, y - 15, x + radius + 75, y + 15, 
                                   fill="#fffacd", outline="#f0e68c", width=1)
            canvas.create_text(x + radius + 40, y - 5, text=chain_text, 
                              font=("Courier", 9, "bold"), fill="red")
            
            # Показываем первые индексы (если их немного)
            if chain_count <= 4:
                indices_text = ",".join(str(idx) for idx in list(node.values)[:4])
                canvas.create_text(x + radius + 40, y + 7, text=f"[{indices_text}]", 
                                  font=("Courier", 7), fill="darkred")
        
        # Рекурсия
        if node.left:
            self.draw_nodes(canvas, node.left, positions, radius)
        if node.right:
            self.draw_nodes(canvas, node.right, positions, radius)
    
    def draw_tree_legend(self, canvas, canvas_width):
        """Рисует легенду для дерева"""
        legend_y = 15
        legend_x = canvas_width - 250
        
        # Сбалансирован
        canvas.create_oval(legend_x, legend_y, legend_x + 20, legend_y + 20, 
                          fill="#90EE90", outline="#2d862d", width=2)
        canvas.create_text(legend_x + 30, legend_y + 10, text="Сбалансирован", 
                          anchor="w", font=("Arial", 9))
        
        # Цепочка
        legend_y += 25
        canvas.create_rectangle(legend_x, legend_y, legend_x + 20, legend_y + 15, 
                               fill="#fffacd", outline="#f0e68c", width=1)
        canvas.create_text(legend_x + 30, legend_y + 7, text="Цепочка индексов", 
                          anchor="w", font=("Arial", 9))
    
    def get_balance(self, node):
        """Вычисляет баланс-фактор узла"""
        if node is None:
            return 0
        left_height = node.left.height if node.left else 0
        right_height = node.right.height if node.right else 0
        return left_height - right_height