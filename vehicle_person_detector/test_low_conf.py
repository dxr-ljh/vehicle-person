import os
import cv2
from detector import VehiclePersonDetector

base_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(base_dir, "output")

print("加载模型...")
d = VehiclePersonDetector(model_size="n", conf_threshold=0.15)
d.load_model()
print("模型就绪 (置信度阈值: 0.15)\n")

test_images = [
    "street_crowd.jpg",
    "crosswalk.jpg",
    "busy_street.jpg",
    "city_street.jpg",
    "city_traffic.jpg",
]

print("=" * 60)
print(f"{'图片':<20} {'行人':>6} {'汽车':>6}  状态")
print("=" * 60)

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

    status = ""
    if persons > 0 and cars > 0:
        status = "⭐⭐⭐ 人车齐全（最佳演示图）"
    elif persons > 0:
        status = "👤 有人无车"
    elif cars > 0:
        status = "🚗 有车无人"

    print(f"{img_name:<20} {persons:>4}人 {cars:>4}辆  {status}")

print("=" * 60)
print(f"\n✅ 检测完成！")
print(f"   结果图: output/result_*.jpg")
print(f"   推荐用 GUI 打开查看带框的检测效果")
