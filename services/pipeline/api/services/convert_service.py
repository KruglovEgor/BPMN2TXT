import math
import json
import jinja2
from typing import List, Dict, Any, Union, Optional, TYPE_CHECKING

from bpmn.bpmn_elements import (
    Participant, Element, Diagram,
    StartEvent, EndEvent, IntermediateThrowEvent, IntermediateCatchEvent,
    Gateway, Task, TextAnnotation
)
from bpmn.bpmn_flows import Flow, SequenceFlow, MessageFlow
from bpmn.element_factories import get_factory, CATEGORIES
from bpmn.flow_factories import get_keypoint_factory
from commons.utils import get_nearest_element, here

if TYPE_CHECKING:
    from bpmn.predictions import (
        ObjectPrediction,
        KeyPointPrediction,
    )


def convert_object_predictions(predictions: List["ObjectPrediction"]):
    """Преобразует предсказания в BPMN-элементы."""

    elements = []
    for prediction in predictions:
        factory = get_factory(prediction.predicted_label)
        if factory is not None:
            bpmn_element = factory.create_element(prediction)
            if bpmn_element is not None:
                elements.append(bpmn_element)

    return elements


def render_diagram(bpmn_diagram: Diagram):
    """Рендерит диаграмму в BPMN XML-строку."""

    template_loader = jinja2.FileSystemLoader(
        searchpath=here("../../commons/templates/")
    )
    template_env = jinja2.Environment(loader=template_loader)
    template_file = "bpmntemplate.jinja"
    template = template_env.get_template(template_file)
    output_text = template.render({"diagram": bpmn_diagram})

    return output_text


def convert_keypoint_prediction(predictions: List["KeyPointPrediction"]):
    """Преобразует предсказания ключевых точек в BPMN-потоки."""

    flows = []
    for prediction in predictions:
        factory = get_keypoint_factory(prediction.predicted_label)
        if factory is not None:
            flow = factory.create_flow(prediction)
            if flow is not None:
                flows.append(flow)

    return flows


def link_flows(flows: List[Flow], elements: List[Element]):
    """Привязывает потоки к ближайшим элементам (source/target)."""

    def _xy(point):
        return point[0], point[1]

    def _point_inside(point, element, padding=4.0):
        x, y = _xy(point)
        return (
            element.prediction.top_left_x -
            padding <= x <= element.prediction.bottom_right_x + padding
            and element.prediction.top_left_y - padding <= y <= element.prediction.bottom_right_y + padding
        )

    def _distance(point, element):
        px, py = _xy(point)
        cx, cy = element.prediction.center
        return math.sqrt(pow(px - cx, 2) + pow(py - cy, 2))

    def _closest(point, candidates, exclude_ids=None):
        if not candidates:
            return None
        exclude_ids = exclude_ids or set()

        def _best(pool):
            ranked = sorted(pool, key=lambda el: _distance(point, el))
            for el in ranked:
                if el.id not in exclude_ids:
                    return el
            return None

        inside = [el for el in candidates if _point_inside(point, el)]
        if inside:
            choice = _best(inside)
            if choice:
                return choice
        return _best(candidates) or get_nearest_element(_xy(point), candidates)

    participants = [el for el in elements if isinstance(el, Participant)]
    element_candidates = [
        el for el in elements if not isinstance(el, Participant)]

    def _owner(element: Element):
        for participant in participants:
            if _point_inside(element.prediction.center, participant):
                return participant
        return None

    for flow in flows:
        candidates = element_candidates
        if isinstance(flow, SequenceFlow):
            source = _closest(flow.prediction.tail, candidates)
            target = _closest(flow.prediction.head, candidates, exclude_ids={
                              source.id} if source else None)
        else:  # MessageFlow and others
            source = _closest(flow.prediction.tail, candidates)
            source_owner = _owner(source) if source else None
            target_pool_filtered = [
                el for el in candidates if _owner(el) is None or _owner(el) != source_owner
            ] or candidates
            target = _closest(
                flow.prediction.head,
                target_pool_filtered,
                exclude_ids={source.id} if source else None,
            )

        if source is None or target is None:
            continue

        flow.sourceRef = source.id
        flow.targetRef = target.id

        if not isinstance(source, Participant):
            source.outgoing.append(flow.id)
        if not isinstance(target, Participant):
            target.incoming.append(flow.id)

    return elements, flows


def _get_element_type(element: Union[Element, Participant]) -> str:
    """Возвращает строковый тип элемента BPMN."""
    if isinstance(element, Participant):
        return "participant"
    elif isinstance(element, StartEvent):
        return "startEvent"
    elif isinstance(element, EndEvent):
        return "endEvent"
    elif isinstance(element, IntermediateThrowEvent):
        return "intermediateThrowEvent"
    elif isinstance(element, IntermediateCatchEvent):
        return "intermediateCatchEvent"
    elif isinstance(element, Gateway):
        return "gateway"
    elif isinstance(element, Task):
        return "task"
    elif isinstance(element, TextAnnotation):
        return "textAnnotation"
    else:
        return "unknown"


def _get_element_subtype(element: Element) -> str:
    """Возвращает подтип элемента (например, timerEventDefinition)."""
    return getattr(element, 'type', "")


def _element_to_dict(element: Union[Element, Participant]) -> Dict[str, Any]:
    """Преобразует BPMN элемент в словарь."""
    if isinstance(element, Participant):
        return {
            "id": element.id,
            "type": "participant",
            "name": element.get_name(),
            "processId": element.process.id if element.process else None
        }

    result = {
        "id": element.id,
        "type": _get_element_type(element),
        "name": element.get_name()
    }

    # Добавляем подтип если он отличается от базового типа
    subtype = _get_element_subtype(element)
    if subtype and subtype != result["type"]:
        result["subtype"] = subtype

    return result


def _flow_to_dict(flow: Flow) -> Dict[str, Any]:
    """Преобразует BPMN поток в словарь."""
    return {
        "id": flow.id,
        "type": "sequenceFlow" if isinstance(flow, SequenceFlow) else "messageFlow",
        "name": flow.get_name(),
        "source": flow.sourceRef,
        "target": flow.targetRef
    }


def elements_to_json(elements: List[Union[Element, Participant, Flow]]) -> Dict[str, Any]:
    """
    Преобразует список BPMN элементов и потоков в структурированный JSON.

    Формат вывода:
    {
        "participants": [...],  # Участники (пулы)
        "elements": [...],      # Элементы (задачи, события, шлюзы)
        "flows": [...]          # Потоки (связи между элементами)
    }
    """
    participants = []
    bpmn_elements = []
    flows = []

    for item in elements:
        if isinstance(item, Participant):
            participants.append(_element_to_dict(item))
        elif isinstance(item, Flow):
            flows.append(_flow_to_dict(item))
        elif isinstance(item, Element):
            bpmn_elements.append(_element_to_dict(item))

    result = {}

    # Добавляем только непустые секции
    if participants:
        result["participants"] = participants
    if bpmn_elements:
        result["elements"] = bpmn_elements
    if flows:
        result["flows"] = flows

    return result


def elements_to_json_string(elements: List[Union[Element, Participant, Flow]],
                            indent: Optional[int] = None) -> str:
    """Преобразует список BPMN элементов в JSON строку."""
    return json.dumps(elements_to_json(elements), ensure_ascii=False, indent=indent)
