from typing import List


class ObjectPrediction:
    """Представляет предсказание детекции объектов, сделанное моделью.
    Содержит информацию о предсказанной области и её положении.

    Параметры
    ----------
    predicted_label : int
        Предсказанная метка области.
    top_left_x : float
        Координата x верхнего левого угла.
    top_left_y : float
        Координата y верхнего левого угла.
    bottom_right_x : float
        Координата x нижнего правого угла.
    bottom_right_y : float
        Координата y нижнего правого угла.
    """
    def __init__(
        self,
        predicted_label: int,
        top_left_x: float,
        top_left_y: float,
        bottom_right_x: float,
        bottom_right_y: float,
    ):
        self.center = None
        self.height = None
        self.width = None
        self.predicted_label = predicted_label
        self.top_left_x = top_left_x
        self.top_left_y = top_left_y
        self.bottom_right_x = bottom_right_x
        self.bottom_right_y = bottom_right_y
        self.calculate_box()

    def calculate_box(self):
        """Вычисляет дополнительную информацию об области: ширину, высоту и центр. """
        self.width = abs(self.bottom_right_x - self.top_left_x)
        self.height = abs(self.bottom_right_y - self.top_left_y)
        self.center = (
            self.top_left_x + self.width / 2,
            self.top_left_y + self.height / 2,
        )

    def get_box_coordinates(self) -> List[float]:
        """Возвращает координаты области в виде списка. """
        return [
            self.top_left_x,
            self.top_left_y,
            self.bottom_right_x,
            self.bottom_right_y,
        ]


class KeyPointPrediction:
    """Представляет предсказание детекции ключевых точек, сделанное моделью для распознавания потоков.
    Содержит информацию о предсказанной области, её положении и ключевых точках.

    Параметры
    ----------
    predicted_label : int
        Предсказанная метка области.
    top_left_x : float
        Координата x верхнего левого угла.
    top_left_y : float
        Координата y верхнего левого угла.
    bottom_right_x : float
        Координата x нижнего правого угла.
    bottom_right_y : float
        Координата y нижнего правого угла.
    head : list of float
        Координаты головы потока.
    tail : list of float
        Координаты хвоста потока.
    """
    def __init__(
        self,
        predicted_label: int,
        top_left_x: float,
        top_left_y: float,
        bottom_right_x: float,
        bottom_right_y: float,
        head: list,
        tail: list,
    ):
        self.predicted_label = predicted_label
        self.top_left_x = top_left_x
        self.top_left_y = top_left_y
        self.bottom_right_x = bottom_right_x
        self.bottom_right_y = bottom_right_y
        self.width = abs(self.bottom_right_x - self.top_left_x)
        self.height = abs(self.bottom_right_y - self.top_left_y)
        self.head = head
        self.tail = tail
        self.center = (
            self.top_left_x + self.width / 2,
            self.top_left_y + self.height / 2,
        )


class Text:
    """Представляет текст, распознанный с помощью OCR.

    Параметры
    ----------
    text : str
        Текстовая строка, распознанная OCR.
    x : float
        Координата x верхнего левого угла.
    y : float
        Координата y верхнего левого угла.
    width : float
        Ширина области, содержащей текст.
    height : float
        Высота области, содержащей текст.
    """
    def __init__(self, text, x, y, width, height):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center = (x + width / 2, y + height / 2)

    def __eq__(self, other):
        if not isinstance(other, Text):
            raise Exception("Error")

        return (
            self.x == other.x
            and self.y == other.y
            and self.width == other.width
            and self.height == other.height
            and self.text == other.text
        )
