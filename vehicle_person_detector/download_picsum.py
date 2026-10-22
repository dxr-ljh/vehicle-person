import os
import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(output_dir, exist_ok=True)

images = [
    ("https://picsum.photos/id/1011/800/500", "test_street_1.jpg"),
    ("https://picsum.photos/id/1015/800/500", "test_street_2.jpg"),
    ("https://picsum.photos/id/1018/800/500", "test_street_3.jpg"),
    ("https://picsum.photos/id/1019/800/500", "test_street_4.jpg"),
    ("https://picsum.photos/id/1039/800/500", "test_street_5.jpg"),
]

print("下载测试图片（来自 picsum.photos）...")
success = 0
for url, filename in images:
    filepath = os.path.join(output_dir, filename)
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
            with open(filepath, "wb") as f:
                f.write(data)
        size_kb = len(data) / 1024
        print(f"  ✅ {filename} ({size_kb:.1f} KB)")
        success += 1
    except Exception as e:
        print(f"  ❌ {filename}: {e}")

print(f"\n成功下载 {success}/{len(images)} 张图片")
print(f"保存在: {output_dir}")
