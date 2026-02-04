from jinja2 import Environment, BaseLoader

from bpmn.predictions import KeyPointPrediction


class Flow:
    """Родительский класс для всех потоков, которые могут быть размещены в BPMN-диаграмме.

    Параметры
    ----------
    id : str
        Уникальный идентификатор потока.
    prediction : KeyPointPrediction
        Предсказание, полученное от детектора ключевых точек.
    """
    def __init__(
        self,
        id: str,
        prediction: KeyPointPrediction,
    ):
        self.id = id
        self.prediction = prediction
        self.name = []
        self.jinja_environment = Environment(loader=BaseLoader())
        self.sourceRef = None
        self.targetRef = None

    def render_element(self):
        """Возвращает XML-строку, связанную с этим типом потока"""

    def get_name(self):
        """Возвращает текст потока в виде строки"""
        return " ".join([text.text for text in self.name])

    def render_shape(self):
        """Возвращает XML-строку с информацией о форме этого типа потока"""
        template = """<bpmndi:BPMNEdge id="{{ element.id }}_di" bpmnElement="{{ element.id }}" >
        <di:waypoint x="{{ element.prediction.tail[0] }}" y="{{ element.prediction.tail[1] }}" />
        <di:waypoint x="{{ element.prediction.head[0] }}" y="{{ element.prediction.head[1] }}" />
      </bpmndi:BPMNEdge>
        """
        rtemplate = self.jinja_environment.from_string(template)
        data = rtemplate.render(element=self)

        return data


class SequenceFlow(Flow):
    """Представляет последовательный поток BPMN.

    Параметры
    ----------
    id : str
        Уникальный идентификатор потока.
    prediction : KeyPointPrediction
        Предсказание, полученное от детектора ключевых точек.
    """
    def __init__(
        self,
        id: str,
        prediction: KeyPointPrediction,
    ):
        super(SequenceFlow, self).__init__(id, prediction)

    def render_element(self):
        """Возвращает XML-строку, связанную с последовательным потоком"""

        template = """<bpmn:sequenceFlow id="{{ flow.id }}" name="{{ flow.get_name() }}" sourceRef="{{ flow.sourceRef }}" targetRef="{{ flow.targetRef }}" />"""
        render_template = self.jinja_environment.from_string(template)
        data = render_template.render(flow=self)

        return data


class MessageFlow(Flow):
    """Представляет поток сообщений BPMN.

    Параметры
    ----------
    id : str
        Уникальный идентификатор потока.
    prediction : KeyPointPrediction
        Предсказание, полученное от детектора ключевых точек.
    """
    def __init__(
        self,
        id: str,
        prediction: KeyPointPrediction,
    ):
        super(MessageFlow, self).__init__(id, prediction)

    def render_element(self):
        """Возвращает XML-строку, связанную с потоком сообщений"""

        template = """<bpmn:messageFlow id="{{ flow.id }}" name="{{ flow.get_name() }}" sourceRef="{{ flow.sourceRef }}" targetRef="{{ flow.targetRef }}" />"""
        render_template = self.jinja_environment.from_string(template)
        data = render_template.render(flow=self)

        return data
