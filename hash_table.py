# hash_table.py (Статическая ХТ с методом середины квадрата)
import math
import ctypes
from typing import Optional

class Item:
    def __init__(self, key: Optional[int] = None, value: Optional[int] = None, status: int = 0) -> None:
        self.key: Optional[int] = key
        self.value: Optional[int] = value
        self.status: int = status

    def __repr__(self) -> str:
        return f"Item(key={self.key}, value={self.value}, status={self.status})"

class HashTable:
    # Фиксированный размер таблицы
    STATIC_CAPACITY: int = 1000

    def __init__(self) -> None:
        self.capacity: int = self.STATIC_CAPACITY
        self.size: int = 0
        # Убираем load_factor и threshold
        ArrayType = ctypes.py_object * self.capacity
        self._elements: ctypes.Array = ArrayType()
        for i in range(self.capacity):
            self._elements[i] = Item(status=0)

    @staticmethod
    def _assert_int(var: int) -> None:
        if not isinstance(var, int):
            raise TypeError(f"Expected int, got {type(var).__name__}")

    # --- НОВАЯ ХЕШ-ФУНКЦИЯ: Середина квадрата ---
    def hash(self, key: int) -> int:
        self._assert_int(key)
        if key < 0:
            raise ValueError("Key must be non-negative for 'middle square' hash.")

        k = key
        k_squared = k * k

        # Считаем количество цифр
        if k_squared == 0:
            digit_count = 1
        else:
            digit_count = int(math.log10(k_squared)) + 1

        # Если нечётное — добавляем ведущий ноль (умножаем на 10)
        if digit_count % 2 != 0:
            k_squared_padded = k_squared * 10
            padded_digit_count = digit_count + 1
        else:
            k_squared_padded = k_squared
            padded_digit_count = digit_count

        # r — количество младших разрядов, которые нужно отбросить
        r = (padded_digit_count // 2) - 1
        # d — количество цифр, которые берём из середины (всегда 2)
        d = 2

        # Отбрасываем r младших разрядов
        temp = k_squared_padded // (10 ** r)
        # Берём d цифр с конца (остаток от деления на 10^d)
        middle_digits = temp % (10 ** d)

        # Применяем модуль от capacity
        return middle_digits % self.capacity
    # --- КОНЕЦ НОВОЙ ХЕШ-ФУНКЦИИ ---

    def probe(self, h0: int, i: int) -> int:
        # Линейное пробирование
        return (h0 + i) % self.capacity

    # Убираем set_size и _resize
    # def set_size(self, capacity: int):
    # def _resize(self, new_capacity: int) -> None:

    def insert(self, key: int, value: int) -> int:
        self._assert_int(key)
        self._assert_int(value)
        item = Item(key, value)

        # Убираем проверку порога и рехеширование
        # if self.size / self.capacity > self.threshold:
        #     self._resize(self.capacity * 2)

        h0 = self.hash(key)
        first_tombstone: Optional[int] = None
        for i in range(self.capacity):
            idx = self.probe(h0, i)
            slot: Item = self._elements[idx]
            if slot.status == 1:
                if slot.key == key:
                    # Ключ уже существует
                    return -1
            elif slot.status == 2 and first_tombstone is None:
                # Запоминаем первую "могилу"
                first_tombstone = idx
            elif slot.status == 0:
                # Найдена пустая ячейка
                # Вставляем в первую могилу, если была, иначе в текущую
                insert_idx = first_tombstone if first_tombstone is not None else idx
                item.status = 1
                self._elements[insert_idx] = item
                self.size += 1
                return insert_idx
        # Если таблица заполнена и не нашли место (все ячейки заняты или удалены)
        # Это маловероятно при 1000 ячейках, но на всякий случай
        raise Exception("Hash table is full")

    def search(self, key: int) -> ctypes.Array:
        self._assert_int(key)
        h0 = self.hash(key)
        steps: int = 0
        found: Optional[Item] = None
        for i in range(self.capacity):
            steps += 1
            idx = self.probe(h0, i)
            slot: Item = self._elements[idx]
            if slot.status == 0:
                # Пустая ячейка - ключа нет
                break
            if slot.status == 1 and slot.key == key:
                # Найден ключ
                found = slot
                break
        # Возвращаем массив с найденным Item и количеством шагов
        ResultType = ctypes.py_object * 2
        result: ctypes.Array = ResultType()
        result[0] = found
        result[1] = steps
        return result

    def delete(self, key: int) -> bool:
        self._assert_int(key)
        h0 = self.hash(key)
        for i in range(self.capacity):
            idx = self.probe(h0, i)
            slot: Item = self._elements[idx]
            if slot.status == 0:
                # Пустая ячейка - ключа нет
                return False
            if slot.status == 1 and slot.key == key:
                # Найден ключ - помечаем как удалённый
                slot.status = 2
                self.size -= 1
                return True
        # Ключ не найден
        return False

    def __contains__(self, key: int) -> bool:
        return self.search(key)[0] is not None

    def __repr__(self) -> str:
        slots_str = ""
        for i in range(self.capacity):
            slot: Item = self._elements[i]
            # hash1 - первичный хеш ключа (если ключ есть)
            primary_hash = self.hash(slot.key) if slot.key is not None else None
            # hash2 - индекс ячейки
            secondary_hash = i if slot.key is not None else None
            slots_str += (f"\n[hash1:{primary_hash}, hash2:{secondary_hash}, "
                          f"key={slot.key}, value={slot.value}, status={slot.status}]")
        return (f"HashTable(capacity={self.capacity}, size={self.size}, slots="
                f"{slots_str}\n)")

# --- Пример использования ---
if __name__ == "__main__":
    ht = HashTable()
    print(f"Initial capacity: {ht.capacity}")

    # Попробуем вставить несколько ключей
    # Для хеш-функции середины квадрата лучше брать числа, квадраты которых дают 2+ цифры в середине
    # Например: 1234 -> 1522756 -> середина 27 -> hash = 27 % 1000 = 27
    try:
        print("Inserting 1234 -> 0:", ht.insert(1234, 0))
        print("Inserting 5678 -> 1:", ht.insert(5678, 1))
        print("Inserting 9999 -> 2:", ht.insert(9999, 2))
        print("Inserting 100 -> 3:", ht.insert(100, 3))
        print("Inserting 101 -> 4:", ht.insert(101, 4))
        print(f"Size: {ht.size}")
    except Exception as e:
        print(f"Insert error: {e}")

    # Поиск
    res = ht.search(1234)
    print(f"Search 1234: found={res[0]}, steps={res[1]}")
    res = ht.search(9998) # Не существует
    print(f"Search 9998: found={res[0]}, steps={res[1]}")

    # Удаление
    print("Delete 1234:", ht.delete(1234))
    print(f"Size after delete: {ht.size}")
    res = ht.search(1234)
    print(f"Search 1234 after delete: found={res[0]}, steps={res[1]}")

    # Содержит
    print("Contains 5678:", 5678 in ht)
    print("Contains 1234:", 1234 in ht)

    # Печать
    # print("\nHash Table state:")
    # print(ht)
