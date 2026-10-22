import os
import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(output_dir, exist_ok=True)

urls = [
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/People_walking_on_street.jpg/640px-People_walking_on_street.jpg",
     "street_people.jpg"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Car_on_street.jpg/640px-Car_on_street.jpg",
     "street_car.jpg"),
]

test_urls = [
    ("https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=640&q=80", "city_street.jpg"),
    ("https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=640&q=80", "shopping_street.jpg"),
    ("https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=640&q=80", "cars_road.jpg"),
]

print("正在下载测试图片...")

for url, filename in test_urls:
    filepath = os.path.join(output_dir, filename)
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            with open(filepath, "wb") as f:
                f.write(resp.read())
        print(f"  ✅ {filename} 下载成功")
    except Exception as e:
        print(f"  ❌ {filename} 下载失败: {e}")

print("\n下载完成！图片保存在 output 目录")
