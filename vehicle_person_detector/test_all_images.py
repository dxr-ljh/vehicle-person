import cv2
import os
from detector import VehiclePersonDetector

base_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(base_dir, "output")

print("加载模型...")
d = VehiclePersonDetector(model_size="n", conf_threshold=0.3)
d.load_model()
print("模型就绪\n")

test_images = [f for f in os.listdir(output_dir)
               if f.lower().endswith(('.jpg', '.jpeg', '.png'))
               and not f.startswith('result_')
               and not f.startswith('test_image')]

print("=" * 60)
print(f"{'图片':<25} {'行人':>5} {'汽车':>5}  状态")
print("=" * 60)

best_img = None
best_score = 0

for img_name in sorted(test_images):
    img_path = os.path.join(output_dir, img_name)
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
    score = persons + cars
    if persons > 0 and cars > 0:
        status = "⭐⭐⭐ 人车齐全"
        if score > best_score:
            best_score = score
            best_img = img_name
    elif persons > 0:
        status = "👤 有行人"
    elif cars > 0:
        status = "🚗 有汽车"
    else:
        status = "无目标"

    print(f"{img_name:<25} {persons:>3}人 {cars:>3}辆  {status}")

print("=" * 60)

if best_img:
    print(f"\n🏆 最佳演示图: {best_img}")
    print(f"   结果图: result_{best_img}")

print(f"\n✅ 全部检测完成，结果图保存在 output/ 目录")
