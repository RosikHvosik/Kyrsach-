from typing import Optional, Iterator, Generic, TypeVar

T = TypeVar('T')

class Node(Generic[T]):
    def __init__(self, data: T) -> None:

        self.data = data
        self.next: Optional[Node[T]] = None

    def __repr__(self) -> str:
        return f"Node({self.data!r})"

class MyList(Generic[T]):
    def __init__(self) -> None:

        self.head: Optional[Node[T]] = None
        self._size: int = 0

    def __len__(self) -> int:
        return self._size



    def append(self, item: T) -> int:

        new_node = Node(item)

        if self.head is None:

            self.head = new_node
            new_node.next = new_node 
        else:

            tail = self.head
            while tail.next is not self.head:
                tail = tail.next

            new_node.next = self.head
            tail.next = new_node  
            self.head = new_node 

        self._size += 1

        return 0

 


    def remove(self, item: T) -> T:

        if self.head is None:
            raise ValueError(f"{item!r} not in list")


        if self.head.data == item:
            removed_data = self.head.data
            if self._size == 1:
                self.head = None
            else:

                tail = self.head
                while tail.next is not self.head:
                    tail = tail.next

                self.head = self.head.next
                tail.next = self.head
            self._size -= 1
            return removed_data


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

    def pop(self, index: int = -1) -> T:
        if self._size == 0:
            raise IndexError("pop from empty list")
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")

        if index == 0:
            return self.remove(self.head.data)


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

        current = self.head
        for _ in range(index):
            current = current.next
        current.data = value


    def __contains__(self, item: T) -> bool:
        if self.head is None:
            return False
        current = self.head
        for _ in range(self._size):
            if current.data == item:
                return True
            current = current.next
        return False

    def __iter__(self) -> Iterator[T]:
        if self.head is None:
            return
        current = self.head
        for _ in range(self._size): 
            yield current.data
            current = current.next

    def __repr__(self) -> str:
        if self.head is None:
            return "MyList([])"
        result = "MyList(["
        current = self.head
        for _ in range(self._size):
            result += repr(current.data)
            current = current.next
            if current is not self.head:
                result += ", "
        result += "])"
        return result

    def __str__(self) -> str:
        if self.head is None:
            return "[]"
        result = "["
        current = self.head
        for _ in range(self._size):
            result += str(current.data)
            current = current.next
            if current is not self.head: 
                result += ", "
        result += "]"
        return result

