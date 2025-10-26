# List.py (Циклический список для цепочек)

from typing import Optional, Iterator, Generic, TypeVar

T = TypeVar('T')

class Node(Generic[T]):
    def __init__(self, data: T) -> None:
        # Исправлена опечатка: self. T = data -> self.data = data
        self.data = data
        self.next: Optional[Node[T]] = None

    def __repr__(self) -> str:
        return f"Node({self.data!r})"

class MyList(Generic[T]):
    def __init__(self) -> None:
        # orig = getattr(self, "__orig_class__", None)
        # if orig is not None:
        #     self._type = get_args(orig)
        # else:
        #     self._type = None
        self.head: Optional[Node[T]] = None
        self._size: int = 0

    def __len__(self) -> int:
        return self._size

    # _assert_type может быть определён или нет, в зависимости от ваших требований.
    # def _assert_type(self, item):

    # Метод append добавлен СНАРУЖИ класса MyList, внутри класса MyList
    def append(self, item: T) -> int:
        # self._assert_type(item) # Закомментировано, так как _assert_type, возможно, не определён
        new_node = Node(item)

        if self.head is None:
            # Если список пуст
            self.head = new_node
            new_node.next = new_node  # Циклический
        else:
            # Найти последний узел (тот, чей next указывает на head)
            tail = self.head
            while tail.next is not self.head:
                tail = tail.next

            # Вставить новый узел в начало
            new_node.next = self.head
            tail.next = new_node  # Последний теперь указывает на новый узел
            self.head = new_node  # Новый узел становится головой

        self._size += 1
        # Возвращаем индекс, под которым элемент *был бы* в линейном списке.
        # Так как добавляем в начало, это всегда 0.
        return 0

    # АЛЬТЕРНАТИВНЫЙ append: добавление в конец (тогда head не меняется)
    # def append(self, item: T) -> None:
    #     """Добавляет элемент в конец циклического списка."""
    #     new_node = Node(item)
    #     if self.head is None:
    #         self.head = new_node
    #         new_node.next = new_node
    #     else:
    #         tail = self.head
    #         while tail.next is not self.head:
    #             tail = tail.next
    #         tail.next = new_node
    #         new_node.next = self.head
    #     self._size += 1


    def remove(self, item: T) -> T:
        """Удаляет первое вхождение элемента. Возвращает удаленное значение."""
        if self.head is None:
            raise ValueError(f"{item!r} not in list")

        # Проверяем голову
        if self.head.data == item:
            removed_data = self.head.data
            if self._size == 1:
                self.head = None
            else:
                # Найдем хвост
                tail = self.head
                while tail.next is not self.head:
                    tail = tail.next
                # Переназначим голову и замкнем
                self.head = self.head.next
                tail.next = self.head
            self._size -= 1
            return removed_data

        # Ищем элемент, начиная с next от head
        prev = self.head
        current = self.head.next
        while current is not self.head:
            if current.data == item:
                prev.next = current.next
                self._size -= 1
                return current.data
            prev = current
            current = current.next

        raise ValueError(f"{item!r} not in list")

    # --- Опциональные методы, можно оставить или упростить ---
    def pop(self, index: int = -1) -> T:
        if self._size == 0:
            raise IndexError("pop from empty list")
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")

        if index == 0:
            return self.remove(self.head.data) # Используем remove для головы

        # Найдем элемент по индексу
        prev = self.head
        current = self.head.next
        current_index = 1
        while current is not self.head and current_index != index:
            prev = current
            current = current.next
            current_index += 1

        if current is self.head and current_index != index:
             raise IndexError("Index out of range")

        prev.next = current.next
        self._size -= 1
        return current.data

    def __getitem__(self, index: int) -> T:
        if self._size == 0:
            raise IndexError("list is empty")
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")

        current = self.head
        for _ in range(index):
            current = current.next
        return current.data

    def __setitem__(self, index: int, value: T) -> None:
        if self._size == 0:
            raise IndexError("list is empty")
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")
        # Не проверяем тип
        current = self.head
        for _ in range(index):
            current = current.next
        current.data = value
    # --- Конец опциональных методов ---

    def __contains__(self, item: T) -> bool:
        if self.head is None:
            return False
        current = self.head
        for _ in range(self._size): # Обходим кольцо
            if current.data == item:
                return True
            current = current.next
        return False

    def __iter__(self) -> Iterator[T]:
        if self.head is None:
            return
        current = self.head
        for _ in range(self._size): # Обходим кольцо
            yield current.data
            current = current.next

    def __repr__(self) -> str:
        if self.head is None:
            return "MyList([])"
        result = "MyList(["
        current = self.head
        for _ in range(self._size): # Обходим кольцо
            result += repr(current.data)
            current = current.next
            if current is not self.head: # Не добавляем запятую после последнего
                result += ", "
        result += "])"
        return result

    def __str__(self) -> str:
        if self.head is None:
            return "[]"
        result = "["
        current = self.head
        for _ in range(self._size): # Обходим кольцо
            result += str(current.data)
            current = current.next
            if current is not self.head: # Не добавляем запятую после последнего
                result += ", "
        result += "]"
        return result

    # from_string и _assert_type убираем, если не используются
    # @staticmethod
    # def from_string(string: str, sep: str = ' ') -> "MyList[str]":
