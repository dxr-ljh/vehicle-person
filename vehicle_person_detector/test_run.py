import os
import cv2
from detector import VehiclePersonDetector

base_dir = os.path.dirname(os.path.abspath(__file__))

print("正在加载 YOLOv8 模型...")
d = VehiclePersonDetector(model_size="n", conf_threshold=0.3)
d.load_model()
print("模型加载成功！")

img_path = os.path.join(base_dir, "output", "test_image.jpg")
img = cv2.imread(img_path)
if img is None:
    print("找不到测试图片")
    exit(1)

print(f"\n正在检测图片: {os.path.basename(img_path)}")
dets = d.detect_image(img)
print(f"检测到 {len(dets)} 个目标:")
for i, x in enumerate(dets, 1):
    print(f"  {i}. {x['class_cn']}: 置信度 {x['confidence']*100:.1f}%")

person_count = sum(1 for d in dets if d["class"] == "person")
car_count = sum(1 for d in dets if d["class"] == "car")
print(f"\n  👤 行人: {person_count}")
print(f"  🚗 汽车: {car_count}")

print("\n正在检测视频...")
video_path = os.path.join(base_dir, "output", "test_video.mp4")
all_dets, fps, total = d.detect_video(video_path, output_path=os.path.join(base_dir, "output", "test_result.mp4"))
print(f"视频检测完成: {total} 帧, {fps} FPS")

total_persons = sum(sum(1 for d in frame if d["class"] == "person") for frame in all_dets)
total_cars = sum(sum(1 for d in frame if d["class"] == "car") for frame in all_dets)
print(f"累计行人: {total_persons} 人次, 累计汽车: {total_cars} 辆次")
print("\n✅ 全部测试通过！")
