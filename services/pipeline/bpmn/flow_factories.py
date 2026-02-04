from bpmn.bpmn_flows import Flow, SequenceFlow, MessageFlow
from bpmn.predictions import KeyPointPrediction
from commons.utils import generate_id


class FlowFactory:
    """Родительский класс для фабрик, используемых для создания потоков BPMN, которые могут быть
    объектами SequenceFlow или MessageFlow. """
    generated_ids = []

    def create_flow(self, prediction: KeyPointPrediction):
        """Возвращает соответствующий поток, связанный с фабрикой"""


class GenericFlowFactory(FlowFactory):
    """Универсальная фабрика для объектов Flow, которая создаёт выбранный Flow, извлекая информацию
    об области, текст и ID.

    Параметры
    ----------
    flow_class : type of Flow
        Фактический подкласс Flow для создания.
    """
    def __init__(self, flow_class: type(Flow)):
        self.flow_class = flow_class

    def create_flow(self, prediction: KeyPointPrediction) -> Flow:
        while (True):
            id = generate_id(self.flow_class.__name__)

            if id not in self.generated_ids:
                break

        self.generated_ids.append(id)

        return self.flow_class(id, prediction)


KEYPOINT_CATEGORIES = {
    0: "sequenceFLow",
    1: "dataAssociation",
    2: "messageFlow",
}
KEYPOINT_FACTORIES = {
    "sequenceFLow": GenericFlowFactory(SequenceFlow),
    "messageFlow": GenericFlowFactory(MessageFlow),
}


def get_keypoint_factory(category_id: int) -> FlowFactory:
    """Возвращает фабрику ключевых точек для создания потока, None если категория недоступна."""
    category = KEYPOINT_CATEGORIES.get(category_id)
    return KEYPOINT_FACTORIES.get(category)
