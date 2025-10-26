# avl_tree.py

# Импортируем нашу собственную реализацию списка для цепочек
from List import MyList
from typing import Optional, Iterator, Generic, TypeVar

T = TypeVar('T')


class AVLNode(Generic[T]):
    def __init__(self, key: T, value: int) -> None:
        self.key: T = key
        # Используем MyList (циклический, не сортирующий) для хранения цепочки индексов
        # Соответствует требованию: "для авл и кч – описание цепочки в случае неуникального ключа"
        self.values: MyList[int] = MyList[int]()
        self.values.append(value)
        self.left: Optional[AVLNode[T]] = None
        self.right: Optional[AVLNode[T]] = None
        self.height: int = 1


class AVLTree(Generic[T]):
    def __init__(self) -> None:
        # self._key_type = ... # Опционально, можно оставить или убрать _assert_type
        self.root: Optional[AVLNode[T]] = None

    def __len__(self) -> int:
        def count(node: Optional[AVLNode[T]]) -> int:
            return 0 if node is None else 1 + count(node.left) + count(node.right)
        return count(self.root)

    # _assert_type можно оставить, но часто в дженериках не используется внутри СД
    # def _assert_type(self, key: T) -> None:

    @staticmethod
    def _get_height(node: Optional[AVLNode[T]]) -> int:
        return node.height if node else 0

    def _update_height(self, node: AVLNode[T]) -> None:
        node.height = max(self._get_height(node.left), self._get_height(node.right)) + 1

    def _get_balance(self, node: Optional[AVLNode[T]]) -> int:
        return self._get_height(node.left) - self._get_height(node.right) if node else 0

    def _rotate_right(self, y: AVLNode[T]) -> AVLNode[T]:
        x = y.left
        t2 = x.right
        x.right, y.left = y, t2
        self._update_height(y)
        self._update_height(x)
        return x

    def _rotate_left(self, x: AVLNode[T]) -> AVLNode[T]:
        y = x.right
        t2 = y.left
        y.left, x.right = x, t2
        self._update_height(x)
        self._update_height(y)
        return y

    def insert(self, key: T, value: int) -> AVLNode[T]:
        # if not isinstance(value, int): # Проверка типа value
        #     raise TypeError(f"value must be int, not {type(value).__name__}")
        self.root = self._insert(self.root, key, value)
        return self.find(key)  # type: ignore[arg-type]

    def _insert(self, node: Optional[AVLNode[T]], key: T, value: int) -> AVLNode[T]:
        if node is None:
            return AVLNode(key, value)
        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            # Ключ уже существует -> добавляем значение в цепочку (MyList)
            node.values.append(value)
            return node

        self._update_height(node)
        balance = self._get_balance(node)
        # Балансировка дерева
        if balance > 1 and key < node.left.key:
            return self._rotate_right(node)
        if balance < -1 and key > node.right.key:
            return self._rotate_left(node)
        if balance > 1 and key > node.left.key:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if balance < -1 and key < node.right.key:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        return node

    def find(self, key: T) -> Optional[AVLNode[T]]:
        # self._assert_type(key) # Опционально
        return self._find(self.root, key)

    def _find(self, node: Optional[AVLNode[T]], key: T) -> Optional[AVLNode[T]]:
        if node is None:
            return None
        if key < node.key:
            return self._find(node.left, key)
        if key > node.key:
            return self._find(node.right, key)
        return node

    def __iter__(self) -> Iterator['AVLNode[T]']:
        yield from self._value_gen(self.root)

    def _value_gen(self, node: Optional['AVLNode[T]']) -> Iterator['AVLNode[T]']:
        if node:
            yield from self._value_gen(node.left)
            yield node
            yield from self._value_gen(node.right)

    def delete_node(self, key: T) -> Optional[AVLNode[T]]:
        # self._assert_type(key) # Опционально
        node = self.find(key)
        self.root = self._delete_node(self.root, key)
        return node

    def _delete_node(self, node: Optional[AVLNode], key: T) -> Optional[AVLNode]: # Исправлен тип параметра
        if node is None:
            return None
        if key < node.key:
            node.left = self._delete_node(node.left, key)
        elif key > node.key:
            node.right = self._delete_node(node.right, key)
        else:
            # Найден узел для удаления
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            # Найдем наследника (минимальный элемент в правом поддереве)
            successor = self.min_value_node(node.right)
            # Скопируем данные наследника в текущий узел
            node.key, node.values = successor.key, successor.values
            # Удалим наследника
            node.right = self._delete_node(node.right, successor.key)
        self._update_height(node)
        balance = self._get_balance(node)
        # Балансировка после удаления
        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._rotate_right(node)
        if balance > 1 and self._get_balance(node.left) < 0:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._rotate_left(node)
        if balance < -1 and self._get_balance(node.right) > 0:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        return node

    def delete_by_value_only(self, value: int) -> bool:
        def traverse_and_delete(node):
            if node is None:
                return False
            if value in node.values:
                node.values.remove(value)
                if len(node.values) == 0:
                    self.delete_node(node.key)
                return True
            return traverse_and_delete(node.left) or traverse_and_delete(node.right)

        return traverse_and_delete(self.root)

    def delete_value(self, key: T, value: int) -> bool:
        # self._assert_type(key) # Опционально
        # if not isinstance(value, int): # Проверка типа value
        #     raise TypeError(f"value must be int, not {type(value).__name__}")
        node = self.find(key)
        if node is None:
            return False
        try:
            node.values.remove(value)
        except ValueError:
            return False
        if len(node.values) == 0:
            self.delete_node(key)
        return True

    @staticmethod
    def min_value_node(node: AVLNode[T]) -> AVLNode[T]:
        current = node
        while current.left:
            current = current.left
        return current

    def __repr__(self):
        # Метод для отладки, выводит дерево с ключами, высотами и цепочками значений
        # Соответствует требованию: "печать БДП(в том числе- цепочки в элементе...)"
        def node_str(node, indent=""):
            if not node:
                return ""
            s = ""
            s += node_str(node.right, indent + "    ")
            s += f"{indent}{node.key} (h={getattr(node, 'height', '?')}) : {list(node.values)}\n" # Выводим цепочку как список
            s += node_str(node.left, indent + "    ")
            return s

        return node_str(getattr(self, 'root', None)).rstrip()
