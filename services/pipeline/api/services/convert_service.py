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
