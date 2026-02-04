from typing import List
import warnings

from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from numpy import ndarray

from bpmn.element_factories import CATEGORIES
from bpmn.predictions import (
    ObjectPrediction,
    KeyPointPrediction,
)

from commons.utils import here

# Detectron2 v0.6 + torch 1.10 печатают предупреждения о будущих изменениях API
warnings.filterwarnings(
    "ignore",
    message=r"__floordiv__ is deprecated.*",
    category=UserWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r"torch\.meshgrid: in an upcoming release.*",
    category=UserWarning,
)


class ObjectPredictor:
    """Предиктор Detectron2 для детекции BPMN-элементов (faster_rcnn)."""

    def __init__(self):
        cfg = get_cfg()
        cfg.merge_from_file(
            model_zoo.get_config_file(
                "COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml")
        )
        cfg.OUTPUT_DIR = "output"
        cfg.MODEL.WEIGHTS = here(
            "../../detectron_model/object_detection_model.pth")
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = len(CATEGORIES)
        cfg.MODEL.DEVICE = "cpu"
        self._predictor = DefaultPredictor(cfg)

    def predict(self, img: ndarray):
        """Детекция BPMN-элементов на изображении."""

        outs = self._predictor(img)

        return outs


class KeyPointPredictor:
    """Предиктор Detectron2 для детекции стрелок (keypoint_rcnn)."""

    def __init__(self):
        cfg = get_cfg()
        cfg.merge_from_file(
            model_zoo.get_config_file(
                "COCO-Keypoints/keypoint_rcnn_R_101_FPN_3x.yaml")
        )
        cfg.OUTPUT_DIR = "output"
        cfg.MODEL.WEIGHTS = here(
            "../../detectron_model/keypoint_detection_model.pth")
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.8
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = 3
        cfg.MODEL.RETINANET.NUM_CLASSES = 3
        cfg.MODEL.ROI_KEYPOINT_HEAD.NUM_KEYPOINTS = 2
        cfg.MODEL.DEVICE = "cpu"
        self._predictor = DefaultPredictor(cfg)

    def predict(self, img):
        """Детекция стрелок (потоков) на изображении."""
        outs = self._predictor(img)

        return outs


object_predictor = ObjectPredictor()
keypoint_predictor = KeyPointPredictor()


def predict_object(image: ndarray) -> List[ObjectPrediction]:
    """Детектирует BPMN-элементы на изображении."""

    predictions = object_predictor.predict(image)

    pred_boxes = predictions.get("instances").get("pred_boxes").tensor.numpy()
    pred_classes = predictions.get("instances").get("pred_classes").numpy()

    predictions = list(zip(pred_boxes, pred_classes))

    return [ObjectPrediction(label, *box) for box, label in predictions]


def predict_keypoint(image: ndarray) -> List[KeyPointPrediction]:
    """Детектирует стрелки (потоки) на изображении."""

    predictions = keypoint_predictor.predict(image)

    boxes = predictions.get("instances").get("pred_boxes").tensor.numpy()
    classes = predictions.get("instances").get("pred_classes").numpy()
    keypoint = predictions.get("instances").pred_keypoints.numpy()

    predictions = list(zip(classes, boxes, keypoint))

    return [
        KeyPointPrediction(clazz, *box, key[0], key[1])
        for clazz, box, key in predictions
    ]
