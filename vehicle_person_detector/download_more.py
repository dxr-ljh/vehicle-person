import os
import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(output_dir, exist_ok=True)

urls = [
    ("https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=640&q=80", "city_traffic.jpg"),
    ("https://images.unsplash.com/photo-1517760444937-f6397edcbbcd?w=640&q=80", "street_crowd.jpg"),
    ("https://images.unsplash.com/photo-1506521781263-d8422e82f27a?w=640&q=80", "crosswalk.jpg"),
    ("https://images.unsplash.com/photo-1502877338535-766e1452684a?w=640&q=80", "busy_street.jpg"),
]

print("正在下载更多测试图片...")

for url, filename in urls:
    filepath = os.path.join(output_dir, filename)
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            with open(filepath, "wb") as f:
                f.write(resp.read())
        size_kb = os.path.getsize(filepath) / 1024
        print(f"  ✅ {filename} ({size_kb:.1f} KB)")
    except Exception as e:
        print(f"  ❌ {filename} 下载失败: {e}")

print("\n完成！")
