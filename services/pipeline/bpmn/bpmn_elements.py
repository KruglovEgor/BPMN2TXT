from dataclasses import dataclass, field
from typing import List

from jinja2 import Environment, BaseLoader

from bpmn.predictions import ObjectPrediction, Text


class Element:
    """Базовый класс для элементов BPMN-процесса."""
    def __init__(
        self,
        id: str,
        prediction: ObjectPrediction,
    ):
        self.id = id
        self.prediction = prediction
        self.name = []
        self.jinja_environment = Environment(loader=BaseLoader())
        self.incoming = []
        self.outgoing = []

    def render_element(self):
        """Возвращает XML-строку элемента."""

    def get_name(self):
        """Возвращает текст элемента."""
        return " ".join([text.text for text in self.name])

    def render_shape(self):
        """Возвращает XML с информацией о форме элемента."""
        template = """<bpmndi:BPMNShape id="{{ element.id }}_di" bpmnElement="{{ element.id }}" >
        <dc:Bounds x="{{ element.prediction.top_left_x }}" y="{{ element.prediction.top_left_y }}" width="{{ element.prediction.width }}" height="{{ element.prediction.height }}" />
      </bpmndi:BPMNShape>
        """
        rtemplate = self.jinja_environment.from_string(template)
        data = rtemplate.render(element=self)

        return data


class StartEvent(Element):
    """Стартовое событие BPMN."""
    def __init__(
        self,
        id: str,
        prediction: ObjectPrediction,
        type: str,
    ):
        super(StartEvent, self).__init__(id, prediction)
        self.type = type

    def render_element(self):
        if self.type == "startEvent":
            template = """<bpmn:startEvent id="{{ start_event.id }}" name="{{ start_event.get_name() }}" />"""
        else:
            template = """<bpmn:startEvent id="{{ start_event.id }}" name="{{ start_event.get_name() }}">
      <bpmn:{{ start_event.type }} />
    </bpmn:startEvent>
        """

        rtemplate = self.jinja_environment.from_string(template)
        data = rtemplate.render(start_event=self)

        return data


class EndEvent(Element):
    """Конечное событие BPMN."""
    def __init__(self, id: str, prediction: ObjectPrediction, type: str):
        super(EndEvent, self).__init__(id, prediction)
        self.type = type

    def render_element(self):
        if self.type == "endEvent":
            template = """<bpmn:endEvent id="{{ end_event.id }}" name="{{ end_event.get_name() }}"/>"""
        else:
            template = """<bpmn:endEvent id="{{ end_event.id }}" name="{{ end_event.get_name() }}">
      <bpmn:{{ end_event.type }} />
    </bpmn:endEvent>
        """

        rtemplate = self.jinja_environment.from_string(template)
        data = rtemplate.render(end_event=self)

        return data


class IntermediateThrowEvent(Element):
    """Промежуточное событие генерации BPMN."""
    def __init__(self, id: str, prediction: ObjectPrediction, type: str):
        super(IntermediateThrowEvent, self).__init__(id, prediction)
        self.type = type

    def render_element(self):
        if self.type == "intermediateThrowEvent":
            template = """<bpmn:intermediateThrowEvent id="{{ intermediate_event.id }}" name="{{ intermediate_event.get_name() }}" />"""
        else:
            template = """<bpmn:intermediateThrowEvent id="{{ intermediate_event.id }}" name="{{ intermediate_event.get_name() }}">
      <bpmn:{{ intermediate_event.type }} />
    </bpmn:intermediateThrowEvent>
        """

        rtemplate = self.jinja_environment.from_string(template)
        data = rtemplate.render(intermediate_event=self)

        return data


class IntermediateCatchEvent(Element):
    """Промежуточное событие ожидания BPMN."""
    def __init__(self, id: str, prediction: ObjectPrediction, type: str):
        super(IntermediateCatchEvent, self).__init__(id, prediction)
        self.type = type

    def render_element(self):
        template = """<bpmn:intermediateCatchEvent id="{{ intermediate_event.id }}" name="{{ intermediate_event.get_name() }}">
      <bpmn:{{ intermediate_event.type }} />
    </bpmn:intermediateCatchEvent>
        """

        rtemplate = self.jinja_environment.from_string(template)
        data = rtemplate.render(intermediate_event=self)

        return data


class Gateway(Element):
    """Шлюз BPMN."""
    def __init__(self, id: str, prediction: ObjectPrediction, type: str):
        super(Gateway, self).__init__(id, prediction)
        self.type = type

    def render_element(self):
        template = """<bpmn:{{ gateway.type }} id="{{ gateway.id }}" name="{{ gateway.get_name() }}" />"""

        rtemplate = self.jinja_environment.from_string(template)
        data = rtemplate.render(gateway=self)

        return data


class Task(Element):
    """Задача BPMN."""
    def __init__(self, id: str, prediction: ObjectPrediction, type: str):
        super(Task, self).__init__(id, prediction)
        self.type = type

    def render_element(self):
        template = """<bpmn:{{ task.type }} id="{{ task.id }}" name="{{ task.get_name() }}"/>"""

        rtemplate = self.jinja_environment.from_string(template)
        data = rtemplate.render(task=self)

        return data


class TextAnnotation(Element):
    """Текстовая аннотация BPMN."""
    def __init__(self, id: str, prediction: ObjectPrediction, type: str):
        super(TextAnnotation, self).__init__(id, prediction)
        self.type = type

    def render_element(self):
        template = """<bpmn:textAnnotation id="{{ textAnnotation.id }}">
      <bpmn:text>{{ textAnnotation.get_name() }}</bpmn:text>
    </bpmn:textAnnotation>
        """

        rtemplate = self.jinja_environment.from_string(template)
        data = rtemplate.render(textAnnotation=self)

        return data


@dataclass()
class Process:
    """Процесс BPMN, содержащий элементы диаграммы."""
    id: str
    elements: List[Element] = field(default_factory=lambda: [])


@dataclass()
class Participant:
    """Участник BPMN (pool), связанный с одним процессом."""
    id: str
    prediction: ObjectPrediction
    process: Process
    name: List[Text] = field(default_factory=lambda: [])

    def get_name(self):
        return " ".join([text.text for text in self.name])

    def __hash__(self):
        return hash((frozenset(self.id), frozenset(self.process.id)))


class Collaboration:
    """Представляет сотрудничество BPMN, которое является XML-тегом, содержащим участников и потоки сообщений.

    Параметры
    ----------
    id : str
        Уникальный идентификатор элемента BPMN.
    participants : list of Participant
        Список участников для включения в XML-файл.
    message_flows : list of MessageFlow
        Список потоков сообщений для включения в XML-файл.
    """
    def __init__(self, id: str, participants: List[Participant], message_flows):
        self.id = id
        self.participants = participants
        self.message_flows = message_flows


@dataclass()
class Diagram:
    """BPMN-диаграмма со всеми процессами и элементами для генерации XML."""
    id: str
    definition_id: str
    processes: List[Process]
    collaboration: Collaboration = None
