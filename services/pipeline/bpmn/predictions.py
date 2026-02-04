from typing import List


class ObjectPrediction:
    """Предсказание детекции объекта: метка и координаты bounding box."""

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
        """Вычисляет ширину, высоту и центр области."""
        self.width = abs(self.bottom_right_x - self.top_left_x)
        self.height = abs(self.bottom_right_y - self.top_left_y)
        self.center = (
            self.top_left_x + self.width / 2,
            self.top_left_y + self.height / 2,
        )

    def get_box_coordinates(self) -> List[float]:
        """Возвращает координаты [x1, y1, x2, y2]."""
        return [
            self.top_left_x,
            self.top_left_y,
            self.bottom_right_x,
            self.bottom_right_y,
        ]


class KeyPointPrediction:
    """Предсказание детекции потока (стрелки): метка, bounding box и ключевые точки (head/tail)."""

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
    """Текст, распознанный OCR: строка и координаты."""

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
