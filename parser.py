# parser.py

# Импортируем MyList из нашего основного файла List.py
from List import MyList

def parse(string: str, sep: str = ' ') -> MyList[str]:
    """
    Разбивает строку на компоненты по разделителю и возвращает MyList[str].
    """
    print(f"[DEBUG] parser.parse: входная строка: '{string}', разделитель: '{sep}'") # Лог 1

    if not isinstance(string, str):
        raise TypeError(f"Expected str, got {type(string).__name__}")
    if not isinstance(sep, str):
        raise TypeError(f"Expected str, got {type(sep).__name__}")
    if sep == "":
        raise ValueError("Separator must not be empty")

    components: MyList[str] = MyList[str]()
    start_i: int = 0
    sep_len: int = len(sep)
    while True:
        index: int = string.find(sep, start_i)
        print(f"[DEBUG] parser.parse: ищем '{sep}' начиная с {start_i}, найден индекс {index}") # Лог 2
        if index == -1:
            remaining_part = string[start_i:]
            print(f"[DEBUG] parser.parse: достигнут конец строки, добавляем остаток: '{remaining_part}'") # Лог 3
            components.append(remaining_part)
            break
        part = string[start_i:index]
        print(f"[DEBUG] parser.parse: найдена часть: '{part}'") # Лог 4
        components.append(part)
        start_i = index + sep_len

    print(f"[DEBUG] parser.parse: результат MyList: {components}") # Лог 5
    print(f"[DEBUG] parser.parse: длина результата: {len(components)}") # Лог 6
    for i in range(len(components)):
        print(f"[DEBUG] parser.parse: components[{i}] = '{components[i]}'") # Лог 7

    return components

# --- Тестирование ---
if __name__ == "__main__":
    # Примеры использования
    result1 = parse("oms_policy;full_name;birth_date", sep=';')
    print(f"Parse 1: {result1}") # -> MyList(['oms_policy', 'full_name', 'birth_date'])
    print(f"Type of result1: {type(result1)}") # -> <class 'List.MyList'> (или как у вас будет импортировано)

    print("\n--- Следующий тест ---\n")

    result2 = parse("12345;Иванов Иван Иванович;01 Jan 1980", sep=';')
    print(f"Parse 2: {result2}") # -> MyList(['12345', 'Иванов Иван Иванович', '01 Jan 1980'])
    print(f"Length: {len(result2)}") # -> 3
    print(f"First part: {result2[0]}") # -> 12345

    # result3 = parse("test", sep="") # -> ValueError
    # result4 = parse(123, sep=";") # -> TypeError
    # result5 = parse("a,b,c", sep=1) # -> TypeError
