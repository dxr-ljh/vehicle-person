import cv2
import os
from detector import VehiclePersonDetector

base_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(base_dir, "output")

print("加载模型...")
d = VehiclePersonDetector(model_size="n", conf_threshold=0.3)
d.load_model()
print("模型就绪\n")

img_path = os.path.join(output_dir, "demo_yolo_bus.jpg")
img = cv2.imread(img_path)

dets = d.detect_image(img)
persons = sum(1 for d in dets if d["class"] == "person")
vehicles = sum(1 for d in dets if d["class"] in ("car", "bus", "truck"))

print(f"📷 demo_yolo_bus.jpg (经典公交车测试图)")
print(f"   👤 行人: {persons} 个")
print(f"   🚗 汽车: {vehicles} 辆")
print(f"\n详细列表:")
for i, det in enumerate(dets, 1):
    print(f"  {i}. {det['class_cn']} ({det['class']}) - 置信度 {det['confidence']*100:.1f}%")

result = d.draw_detections(img, dets)
out_path = os.path.join(output_dir, "result_demo_yolo_bus.jpg")
cv2.imwrite(out_path, result)
print(f"\n结果图已保存: {out_path}")
print("中文标签应该正常显示了！")
