import cv2
import os
import sys
from detector import VehiclePersonDetector

base_dir = os.path.dirname(os.path.abspath(__file__))
img_path = os.path.join(base_dir, "output", "city_street.jpg")

print(f"图片路径: {img_path}")
print(f"路径存在: {os.path.exists(img_path)}")

img = cv2.imread(img_path)
print(f"图片形状: {img.shape if img is not None else 'None'}")
print(f"图片为空: {img is None}")

print("\n加载模型...")
d = VehiclePersonDetector(model_size="n", conf_threshold=0.3)
d.load_model()

dets = d.detect_image(img)
print(f"检测到 {len(dets)} 个目标")

print("\n开始绘制...")
try:
    result = d.draw_detections(img, dets)
    out_path = os.path.join(base_dir, "output", "result_fixed.jpg")
    cv2.imwrite(out_path, result)
    print(f"成功！结果保存到: {out_path}")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
