from typing import Tuple, List, Union, Set

from bpmn.bpmn_elements import (
    Task,
    Participant,
    Element,
    Gateway,
    Process,
    Diagram,
    Collaboration,
    StartEvent,
    EndEvent,
    IntermediateThrowEvent,
    IntermediateCatchEvent, TextAnnotation,
)
from bpmn.bpmn_flows import SequenceFlow, MessageFlow
from bpmn.predictions import ObjectPrediction
from commons.utils import (
    generate_id,
    get_nearest_element,
)


def calculate_width_height(
    x_start: float, y_start: float, x_end: float, y_end: float
) -> Tuple[float, float]:
    """Возвращает ширину и высоту области по начальным и конечным координатам x и y."""
    return abs(x_end - x_start), abs(y_end - y_start)


def connect_participants(participant, elements):
    """Возвращает все элементы, содержащиеся в участнике"""

    return list(
        filter(
            lambda elem: participant.prediction.top_left_x < elem.prediction.top_left_x
            and participant.prediction.top_left_y < elem.prediction.top_left_y
            and participant.prediction.bottom_right_x > elem.prediction.bottom_right_x
            and participant.prediction.bottom_right_y > elem.prediction.bottom_right_y,
            elements,
        )
    )


def extend_participants(processed_participants: Set[Participant]):
    """Этот метод расширяет всех участников, у которых есть элементы за пределами их области.
    Таким образом, расширенный участник будет включать эти элементы."""
    for participant in processed_participants:
        elements = [
            el
            for el in participant.process.elements
            if not isinstance(el, SequenceFlow)
        ]
        min_top_x = min(map(lambda el: el.prediction.top_left_x, elements))
        min_top_y = min(map(lambda el: el.prediction.top_left_y, elements))
        max_bottom_x = max(
            map(lambda el: el.prediction.bottom_right_x, elements))
        max_bottom_y = max(
            map(lambda el: el.prediction.bottom_right_y, elements))

        if min_top_x <= participant.prediction.top_left_x:
            participant.prediction.top_left_x = min_top_x - 20
        if min_top_y <= participant.prediction.top_left_y:
            participant.prediction.top_left_y = min_top_y - 20
        if max_bottom_x >= participant.prediction.bottom_right_x:
            participant.prediction.bottom_right_x = max_bottom_x + 20
        if max_bottom_y >= participant.prediction.bottom_right_y:
            participant.prediction.bottom_right_y = max_bottom_y + 20

        participant.prediction.calculate_box()


class DiagramFactory:
    """Класс-фабрика для создания диаграммы на основе набора элементов, которые могут быть Element или Participant.
    """
    @staticmethod
    def create_element(elements: List[Union[Element, Participant]]) -> Diagram:
        """Фабричный метод, который создаёт диаграмму из набора элементов, которые могут быть
        объектами Element или Participant. """
        def get_elem_types(wanted_type, elem_list):
            return [elem for elem in elem_list if isinstance(elem, wanted_type)]

        message_flows = []
        participants = get_elem_types(Participant, elements)

        processes = []

        if participants:
            processed_elements = []
            for participant in participants:
                process_elements = connect_participants(
                    participant,
                    [
                        elem
                        for elem in elements
                        if not isinstance(elem, Participant)
                        and elem not in processed_elements
                    ],
                )
                if process_elements:
                    processed_elements.extend(process_elements)
                    participant.process.elements = process_elements
                    processes.append(participant.process)
                else:
                    participant.process.id = ""

            if remaining_elements := [
                el
                for el in elements
                if el not in processed_elements and not isinstance(el, Participant)
            ]:
                processed_participants = set()
                for element in remaining_elements:
                    if isinstance(element, MessageFlow):
                        message_flows.append(element)
                        continue

                    parts = [
                        part for part in participants if part.process.elements]
                    closest_part = get_nearest_element(
                        element.prediction.center, parts)
                    processed_participants.add(closest_part)
                    closest_part.process.elements.append(element)

                extend_participants(processed_participants)
        else:
            processes.append(Process(generate_id("Process"), elements))
        diagram_id = generate_id("BPMNDiagram")
        definitions_id = generate_id("Definitions")
        return (
            Diagram(
                diagram_id,
                definitions_id,
                processes,
                Collaboration(
                    generate_id("Collaboration"), participants, message_flows
                ),
            )
            if participants
            else Diagram(diagram_id, definitions_id, processes)
        )


class BPMNFactory:
    """Родительский класс для фабрик, используемых для создания элементов BPMN, которые могут быть объектами
    Element или Participant. """
    generated_ids = []

    def create_element(self, prediction: ObjectPrediction) -> Union[Element, Participant]:
        """Возвращает элемент BPMN, связанный с фабрикой"""


class GenericElementFactory(BPMNFactory):
    """Универсальная фабрика для объектов Element, которая создаёт выбранный Element, извлекая информацию
    об области, текст и ID.

    Параметры
    ----------
    element_class : type of Element
        Фактический класс Element для создания.
    element_type : str
        Параметр типа для передачи при создании Element.
    """

    def __init__(self, element_class: type(Element), element_type: str):
        self.element_class = element_class
        self.element_type = element_type

    def create_element(self, prediction: ObjectPrediction) -> Element:
        """Возвращает выбранный элемент BPMN, созданный фабрикой"""
        while (True):
            id = generate_id(self.element_class.__name__)

            if id not in self.generated_ids:
                break

        self.generated_ids.append(id)

        return self.element_class(id, prediction, self.element_type)


class ParticipantFactory(BPMNFactory):
    """Фабрика для объектов Participant, которая создаёт Participant, извлекая информацию об области,
    текст и ID. """

    def create_element(self, prediction: ObjectPrediction) -> Participant:
        """Возвращает участника BPMN. """
        id = generate_id("Participant")
        processRef = generate_id("Process")
        self.generated_ids.extend([id, processRef])

        process = Process(processRef)

        return Participant(id, prediction, process=process)


CATEGORIES = {
    0: "compensateEndEvent",
    1: "timerIntermediateCatchEvent",
    2: "signalIntermediateCatchEvent",
    3: "messageIntermediateCatchEvent",
    4: "escalationEndEvent",
    5: "inclusiveGateway",
    6: "eventBasedGateway",
    7: "signalStartEvent",
    8: "timerStartEvent",
    9: "task",
    10: "conditionalStartEvent",
    11: "messageEndEvent",
    12: "dataObjectReference",
    13: "exclusiveGateway",
    14: "complexGateway",
    15: "dataStoreReference",
    16: "endEvent",
    17: "parallelGateway",
    18: "textAnnotation",
    19: "escalationIntermediateThrowEvent",
    20: "conditionalIntermediateCatchEvent",
    21: "startEvent",
    22: "messageStartEvent",
    23: "signalIntermediateThrowEvent",
    24: "intermediateThrowEvent",
    25: "errorEndEvent",
    26: "linkIntermediateThrowEvent",
    27: "messageIntermediateThrowEvent",
    28: "compensateIntermediateThrowEvent",
    29: "signalEndEvent",
    30: "participant",
    31: "terminateEndEvent",
    32: "linkIntermediateCatchEvent"
}

FACTORIES = {
    "messageEndEvent": GenericElementFactory(EndEvent, "messageEventDefinition"),
    "task": GenericElementFactory(Task, "task"),
    "messageIntermediateCatchEvent": GenericElementFactory(IntermediateCatchEvent, "messageEventDefinition"),
    "inclusiveGateway": GenericElementFactory(Gateway, "inclusiveGateway"),
    "errorEndEvent": GenericElementFactory(EndEvent, "errorEventDefinition"),
    "participant": ParticipantFactory(),
    "messageIntermediateThrowEvent": GenericElementFactory(IntermediateThrowEvent, "messageEventDefinition"),
    "endEvent": GenericElementFactory(EndEvent, "endEvent"),
    "messageStartEvent": GenericElementFactory(StartEvent, "messageEventDefinition"),
    "parallelGateway": GenericElementFactory(Gateway, "parallelGateway"),
    "timerIntermediateCatchEvent": GenericElementFactory(IntermediateCatchEvent, "timerEventDefinition"),
    "exclusiveGateway": GenericElementFactory(Gateway, "exclusiveGateway"),
    "eventBasedGateway": GenericElementFactory(Gateway, "eventBasedGateway"),
    "dataObjectReference": GenericElementFactory(Task, "dataObjectReference"),
    "escalationEndEvent": GenericElementFactory(EndEvent, "escalationEventDefinition"),
    "signalStartEvent": GenericElementFactory(StartEvent, "signalEventDefinition"),
    "startEvent": GenericElementFactory(StartEvent, "startEvent"),
    "timerStartEvent": GenericElementFactory(StartEvent, "timerEventDefinition"),
    "terminateEndEvent": GenericElementFactory(EndEvent, "terminateEventDefinition"),
    "complexGateway": GenericElementFactory(Gateway, "complexGateway"),
    "intermediateThrowEvent": GenericElementFactory(IntermediateThrowEvent, "intermediateThrowEvent"),
    "escalationIntermediateThrowEvent": GenericElementFactory(IntermediateThrowEvent, "escalationEventDefinition"),
    "compensateEndEvent": GenericElementFactory(EndEvent, "compensateEventDefinition"),
    "signalIntermediateCatchEvent": GenericElementFactory(IntermediateCatchEvent, "signalEventDefinition"),
    "conditionalStartEvent": GenericElementFactory(StartEvent, "conditionalEventDefinition"),
    "dataStoreReference": GenericElementFactory(Task, "dataStoreReference"),
    "conditionalIntermediateCatchEvent": GenericElementFactory(IntermediateCatchEvent, "conditionalEventDefinition"),
    "signalIntermediateThrowEvent": GenericElementFactory(IntermediateThrowEvent, "signalEventDefinition"),
    "linkIntermediateThrowEvent": GenericElementFactory(IntermediateThrowEvent, "linkEventDefinition"),
    "compensateIntermediateThrowEvent": GenericElementFactory(IntermediateThrowEvent, "compensateEventDefinition"),
    "signalEndEvent": GenericElementFactory(EndEvent, "signalEventDefinition"),
    "linkIntermediateCatchEvent": GenericElementFactory(IntermediateCatchEvent, "linkEventDefinition"),
    "textAnnotation": GenericElementFactory(TextAnnotation, "")
}


def get_factory(category_id: int) -> BPMNFactory:
    """Возвращает фабрику для создания элемента, None если категория недоступна."""
    category = CATEGORIES.get(category_id)
    return FACTORIES.get(category)
