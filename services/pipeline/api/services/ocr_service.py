import pytesseract
from typing import List
from numpy import ndarray
from bpmn.bpmn_elements import Participant, Element
from bpmn.predictions import Text
from commons.utils import get_nearest_element


def get_text_from_img(img: ndarray) -> List[Text]:
    """Извлекает текст из изображения через OCR (pytesseract)."""

    text_list = []

    # rus+eng — русский + английский; --psm 12 — режим для разреженного текста
    d = pytesseract.image_to_data(
        img, output_type=pytesseract.Output.DICT, config="--psm 12 -l rus+eng"
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
        (x, y, w, h) = (d["left"][i], d["top"]
                        [i], d["width"][i], d["height"][i])
        text_list.append(([x, y, w, h], text))

    return [Text(txt, *box) for box, txt in text_list]


def link_text(texts: List[Text], elements: List[Element]):
    """Привязывает распознанный текст к ближайшим элементам."""

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
