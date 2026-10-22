import os
import cv2
import numpy as np
import torch
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont

TARGET_CLASSES = {
    "person": "行人",
    "car": "汽车",
    "bus": "汽车",
    "truck": "汽车",
}

VEHICLE_CLASSES = {"car", "bus", "truck"}

CLASS_COLORS = {
    "person": (0, 255, 0),
    "car": (0, 0, 255),
    "bus": (0, 0, 255),
    "truck": (0, 0, 255),
}

CLASS_COLORS_RGB = {
    "person": (0, 255, 0),
    "car": (255, 0, 0),
    "bus": (255, 0, 0),
    "truck": (255, 0, 0),
}


class VehiclePersonDetector:
    def __init__(self, model_size="n", device=None, conf_threshold=0.5):
        self.model_name = f"yolov8{model_size}.pt"
        self.conf_threshold = conf_threshold
        if device is None:
            self.device = 0 if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        self.model = None
        self.target_class_ids = None

    def load_model(self):
        self.model = YOLO(self.model_name)
        names = self.model.names
        self.target_class_ids = []
        for cls_name in TARGET_CLASSES.keys():
            for idx, name in names.items():
                if name == cls_name:
                    self.target_class_ids.append(idx)
                    break
        return self.model

    def detect_image(self, image):
        if self.model is None:
            self.load_model()

        results = self.model(
            image,
            conf=self.conf_threshold,
            classes=self.target_class_ids,
            verbose=False,
            device=self.device,
        )

        detections = []
        result = results[0]
        if result.boxes is not None:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                cls_name = result.names[cls_id]
                if cls_name in TARGET_CLASSES:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    detections.append({
                        "class": cls_name,
                        "class_cn": TARGET_CLASSES[cls_name],
                        "confidence": conf,
                        "bbox": (x1, y1, x2, y2),
                    })

        return detections

    def draw_detections(self, image, detections):
        img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)

        try:
            font = ImageFont.truetype("msyh.ttc", 18)
            font_small = ImageFont.truetype("msyh.ttc", 16)
        except:
            try:
                font = ImageFont.truetype("simhei.ttf", 18)
                font_small = ImageFont.truetype("simhei.ttf", 16)
            except:
                font = ImageFont.load_default()
                font_small = font

        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            cls_name = det["class"]
            cls_cn = det["class_cn"]
            conf = det["confidence"]

            color_rgb = CLASS_COLORS_RGB.get(cls_name, (255, 255, 0))

            draw.rectangle([x1, y1, x2, y2], outline=color_rgb, width=2)

            label = f"{cls_cn} {conf*100:.1f}%"
            try:
                bbox = draw.textbbox((0, 0), label, font=font_small)
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            except:
                tw, th = len(label) * 10, 18

            label_y1 = y1 - th - 6
            if label_y1 < 0:
                label_y1 = y1
                label_y2 = y1 + th + 6
            else:
                label_y2 = y1

            draw.rectangle([x1, label_y1, x1 + tw + 8, label_y2], fill=color_rgb)
            draw.text((x1 + 4, label_y1 + 2), label, fill=(255, 255, 255), font=font_small)

        person_count = 0
        vehicle_count = 0
        for det in detections:
            if det["class"] == "person":
                person_count += 1
            elif det["class"] in VEHICLE_CLASSES:
                vehicle_count += 1

        info_y = 15
        draw.text((15, info_y), f"行人: {person_count}",
                  fill=CLASS_COLORS_RGB["person"], font=font)
        info_y += 28
        draw.text((15, info_y), f"汽车: {vehicle_count}",
                  fill=CLASS_COLORS_RGB["car"], font=font)

        result = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        return result

    def detect_video(self, video_path, output_path=None, progress_callback=None):
        if self.model is None:
            self.load_model()

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        else:
            writer = None

        frame_idx = 0
        all_detections = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            detections = self.detect_image(frame)
            all_detections.append(detections)

            if writer is not None:
                annotated = self.draw_detections(frame, detections)
                writer.write(annotated)

            frame_idx += 1
            if progress_callback:
                progress_callback(frame_idx, total_frames)

        cap.release()
        if writer is not None:
            writer.release()

        return all_detections, fps, total_frames


def get_detector(model_size="n", conf_threshold=0.5):
    detector = VehiclePersonDetector(model_size=model_size, conf_threshold=conf_threshold)
    return detector
