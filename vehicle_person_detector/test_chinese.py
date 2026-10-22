import cv2
import os
from detector import VehiclePersonDetector

base_dir = os.path.dirname(os.path.abspath(__file__))
img_path = os.path.join(base_dir, "output", "city_street.jpg")

print("加载模型...")
d = VehiclePersonDetector(model_size="n", conf_threshold=0.3)
d.load_model()

img = cv2.imread(img_path)
dets = d.detect_image(img)
print(f"检测到 {len(dets)} 个目标")
for det in dets[:5]:
    print(f"  {det['class_cn']}: {det['confidence']*100:.1f}%")

result = d.draw_detections(img, dets)
out_path = os.path.join(base_dir, "output", "result_fixed.jpg")
cv2.imwrite(out_path, result)
print(f"\n结果已保存: {out_path}")
print("中文标签应该正常显示了！")
