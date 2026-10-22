import os
import cv2
from detector import VehiclePersonDetector

base_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(base_dir, "output")

print("加载模型...")
d = VehiclePersonDetector(model_size="n", conf_threshold=0.25)
d.load_model()
print("模型就绪\n")

test_images = [
    "city_traffic.jpg",
    "street_crowd.jpg",
    "crosswalk.jpg",
    "busy_street.jpg",
    "city_street.jpg",
    "cars_road.jpg",
]

print("=" * 55)
print(f"{'图片':<20} {'行人':>6} {'汽车':>6}  说明")
print("=" * 55)

for img_name in test_images:
    img_path = os.path.join(output_dir, img_name)
    if not os.path.exists(img_path):
        continue

    img = cv2.imread(img_path)
    if img is None:
        continue

    dets = d.detect_image(img)
    persons = sum(1 for d in dets if d["class"] == "person")
    cars = sum(1 for d in dets if d["class"] == "car")

    annotated = d.draw_detections(img, dets)
    out_path = os.path.join(output_dir, f"result_{img_name}")
    cv2.imwrite(out_path, annotated)

    note = ""
    if persons > 0 and cars > 0:
        note = "⭐ 人车都有"
    elif persons > 0:
        note = "👤 有人"
    elif cars > 0:
        note = "🚗 有车"

    print(f"{img_name:<20} {persons:>4}人 {cars:>4}辆  {note}")

print("=" * 55)
print(f"\n✅ 检测完成！结果图保存在 output/result_*.jpg")
print(f"   在 GUI 中选择这些图片可以直观展示检测效果")
