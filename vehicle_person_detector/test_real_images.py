import os
import cv2
from detector import VehiclePersonDetector

base_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(base_dir, "output")

print("加载模型...")
d = VehiclePersonDetector(model_size="n", conf_threshold=0.3)
d.load_model()
print("模型就绪\n")

test_images = [
    "city_street.jpg",
    "shopping_street.jpg",
    "cars_road.jpg",
]

for img_name in test_images:
    img_path = os.path.join(output_dir, img_name)
    if not os.path.exists(img_path):
        print(f"跳过 {img_name}: 文件不存在")
        continue

    img = cv2.imread(img_path)
    if img is None:
        print(f"跳过 {img_name}: 无法读取")
        continue

    dets = d.detect_image(img)
    persons = sum(1 for d in dets if d["class"] == "person")
    cars = sum(1 for d in dets if d["class"] == "car")

    annotated = d.draw_detections(img, dets)
    out_path = os.path.join(output_dir, f"result_{img_name}")
    cv2.imwrite(out_path, annotated)

    print(f"📷 {img_name}")
    print(f"   👤 行人: {persons} 个")
    print(f"   🚗 汽车: {cars} 辆")
    if dets:
        print(f"   前3个目标:")
        for i, det in enumerate(dets[:3], 1):
            print(f"     {i}. {det['class_cn']} ({det['confidence']*100:.1f}%)")
    print(f"   结果图: result_{img_name}")
    print()

print("✅ 全部检测完成！打开 output 目录查看结果图片")
