import pytesseract
from typing import List
from numpy import ndarray
from bpmn.bpmn_elements import Participant, Element
from bpmn.predictions import Text
from commons.utils import get_nearest_element


def get_text_from_img(img: ndarray) -> List[Text]:
    """Извлекает весь текст из изображения с помощью OCR через pytesseract

    Параметры
    ----------
    img: ndarray
        Изображение для извлечения текста (в виде Numpy ndarray)

    Возвращает
    -------
    List[Text]
        Список обнаруженного текста
    """

    text_list = []

    d = pytesseract.image_to_data(
        img, output_type=pytesseract.Output.DICT, config="--psm 12"
    )
    n_boxes = len(d["level"])
    for i in range(n_boxes):
        text = d["text"][i]
        if (
            len(text) == 0
            or any(not c.isalnum() for c in text[:-1])
            or len(text) > 1
            and not (text[-1].isalnum() or text[-1] in "-?")
            or text.lower().count(text[0].lower()) == len(text)
        ):
            continue
        (x, y, w, h) = (d["left"][i], d["top"][i], d["width"][i], d["height"][i])
        # cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text_list.append(([x, y, w, h], text))

    # cv2.imshow("img", img)
    # cv2.waitKey(0)

    return [Text(txt, *box) for box, txt in text_list]


def link_text(texts: List[Text], elements: List[Element]):
    """Метод, который связывает текст с соответствующими элементами

    Параметры
    ----------
    texts: List[Text]
        Список обнаруженного текста
    elements: List[Element}
        Список элементов для связывания

    Возвращает
    -------
    List[Element]
        Список обновлённых элементов
    """

    for el in elements:
        if isinstance(el, Participant):
            el.prediction.center = (
                el.prediction.top_left_x,
                el.prediction.top_left_y + el.prediction.height / 2,
            )
    for text in texts:
        nearest = get_nearest_element(text.center, elements)
        nearest.name.append(text)
    return elements
