import os
import shutil
import ultralytics

pkg_dir = os.path.dirname(ultralytics.__file__)
assets_dir = os.path.join(pkg_dir, "assets")
print(f"YOLOv8 assets 目录: {assets_dir}")

if os.path.exists(assets_dir):
    files = os.listdir(assets_dir)
    print(f"包含文件: {files}")
    
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            src = os.path.join(assets_dir, f)
            dst = os.path.join(output_dir, f"demo_yolo_{f}")
            shutil.copy2(src, dst)
            print(f"已复制: {f} -> demo_yolo_{f}")
else:
    print("assets 目录不存在")
