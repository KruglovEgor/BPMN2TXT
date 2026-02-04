from typing import List

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


class ObjectPredictor:
    """Класс для представления Detectron2-предиктора, обученного с faster_rcnn"""

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
        """Метод для предсказания и извлечения элементов BPMN из изображения

        Параметры
        ----------

        img: ndarry
            Изображение для детекции элементов (в виде ndarray)

        Возвращает
        -------
        dict
            Предсказания элементов
        """

        outs = self._predictor(img)

        # v = Visualizer(img[:, :, ::-1],
        #                scale=1.5,
        #                instance_mode=ColorMode.IMAGE_BW
        #                )
        # out = v.draw_instance_predictions(outs["instances"].to("cpu"))
        # cv2.imshow("", out.get_image()[:, :, ::-1])
        # cv2.waitKey(0)

        return outs


class KeyPointPredictor:
    """Класс для представления Detectron2-предиктора, обученного с keypoint_faster_rcnn"""

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
        """Метод для предсказания и извлечения стрелок из изображения

        Параметры
        ----------
        img: ndarry
            Изображение для детекции стрелок (в виде ndarray)

        Возвращает
        -------
        dict
            Предсказания стрелок
        """
        outs = self._predictor(img)

        # for kp in outs.get("instances").pred_keypoints.numpy():
        #     cv2.circle(img, (int(kp[0][0]), int(kp[0][1])), 4, (0, 255, 0), -1)
        #     cv2.circle(img, (int(kp[1][0]), int(kp[1][1])), 4, (0, 0, 255), -1)
        # cv2.imshow("", img)
        # cv2.waitKey(0)

        return outs


object_predictor = ObjectPredictor()
keypoint_predictor = KeyPointPredictor()


def predict_object(image: ndarray) -> List[ObjectPrediction]:
    """Передаёт изображение обученной нейросети детекции объектов, которая возвращает
    обнаруженные экземпляры с связанными метками

    Параметры
    ----------
    image: ndarray
        Изображение для детекции элементов (в виде ndarray)

    Возвращает
    ------
    List[ObjectPrediction]
        Список предсказаний ObjectPrediction
    """

    predictions = object_predictor.predict(image)

    pred_boxes = predictions.get("instances").get("pred_boxes").tensor.numpy()
    pred_classes = predictions.get("instances").get("pred_classes").numpy()

    predictions = list(zip(pred_boxes, pred_classes))

    return [ObjectPrediction(label, *box) for box, label in predictions]


def predict_keypoint(image: ndarray) -> List[KeyPointPrediction]:
    """Передаёт изображение обученной нейросети детекции ключевых точек, которая возвращает
    соответствующие предсказания

    Параметры
    ----------
    image: ndarray
        Изображение для детекции элементов (в виде ndarray)

    Возвращает
    ------
    List[KeyPointPrediction]
        Список предсказаний KeyPointPrediction
    """

    predictions = keypoint_predictor.predict(image)

    boxes = predictions.get("instances").get("pred_boxes").tensor.numpy()
    classes = predictions.get("instances").get("pred_classes").numpy()
    keypoint = predictions.get("instances").pred_keypoints.numpy()

    predictions = list(zip(classes, boxes, keypoint))

    return [
        KeyPointPrediction(clazz, *box, key[0], key[1])
        for clazz, box, key in predictions
    ]
