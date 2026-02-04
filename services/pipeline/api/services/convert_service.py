import jinja2
from typing import List, TYPE_CHECKING

from bpmn.bpmn_elements import Participant, Element, Diagram
from bpmn.bpmn_flows import Flow
from bpmn.element_factories import get_factory
from bpmn.flow_factories import get_keypoint_factory
from commons.utils import get_nearest_element, here

if TYPE_CHECKING:
    from bpmn.predictions import (
        ObjectPrediction,
        KeyPointPrediction,
    )


def convert_object_predictions(predictions: List["ObjectPrediction"]):
    """Метод, который преобразует предсказания обнаруженных объектов BPMN в элементы

    Параметры
    ----------
    predictions: List[ObjectPrediction]
        Список предсказаний ObjectPrediction

    Возвращает
    -------
    List[Element]
        Список преобразованных элементов BPMN
    """

    elements = []
    for prediction in predictions:
        factory = get_factory(prediction.predicted_label)
        if factory is not None:
            bpmn_element = factory.create_element(prediction)
            if bpmn_element is not None:
                elements.append(bpmn_element)

    return elements


def render_diagram(bpmn_diagram: Diagram):
    """Метод, который преобразует класс Diagram в итоговую BPMN-строку

    Параметры
    ----------
    bpmn_diagram: Diagram
        Объект Diagram

    Возвращает
    -------
    str
        Строка, представляющая итоговую BPMN-модель
    """

    template_loader = jinja2.FileSystemLoader(
        searchpath=here("../../commons/templates/")
    )
    template_env = jinja2.Environment(loader=template_loader)
    template_file = "bpmntemplate.jinja"
    template = template_env.get_template(template_file)
    output_text = template.render({"diagram": bpmn_diagram})

    return output_text


def convert_keypoint_prediction(predictions: List["KeyPointPrediction"]):
    """Метод, который преобразует предсказания ключевых точек в потоки

    Параметры
    ----------
    predictions: List[KeyPointPrediction]
        Список предсказаний KeyPointPrediction

    Возвращает
    -------
    List[Flow]
        Список преобразованных потоков BPMN
    """

    flows = []
    for prediction in predictions:
        factory = get_keypoint_factory(prediction.predicted_label)
        if factory is not None:
            flow = factory.create_flow(prediction)
            if flow is not None:
                flows.append(flow)

    return flows


def link_flows(flows: List[Flow], elements: List[Element]):
    """Метод, который связывает потоки с соответствующими элементами

    Параметры
    ----------
    flows: List[Flow]
        Список обнаруженных потоков
    elements: List[Element}
        Список элементов для связывания

    Возвращает
    -------
    tuple: tuple[List[Element], List[Flow]]
        Список обновлённых элементов и потоков

    """

    # try to find a better way to link them
    for flow in flows:
        head = flow.prediction.head
        tail = flow.prediction.tail

        near_head = get_nearest_element(head, elements)
        near_tail = get_nearest_element(tail, elements)

        flow.targetRef = near_head.id
        flow.sourceRef = near_tail.id

        if not isinstance(near_tail, Participant):
            near_tail.outgoing.append(flow.id)
        if not isinstance(near_head, Participant):
            near_head.incoming.append(flow.id)

    return elements, flows
