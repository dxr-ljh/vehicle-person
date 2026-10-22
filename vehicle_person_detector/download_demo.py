import os
import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(output_dir, exist_ok=True)

images = [
    ("https://picsum.photos/id/1005/800/500", "demo_people1.jpg"),
    ("https://picsum.photos/id/1006/800/500", "demo_people2.jpg"),
    ("https://picsum.photos/id/1007/800/500", "demo_people3.jpg"),
    ("https://picsum.photos/id/1010/800/500", "demo_people4.jpg"),
    ("https://picsum.photos/id/1027/800/500", "demo_car1.jpg"),
    ("https://picsum.photos/id/1033/800/500", "demo_car2.jpg"),
    ("https://picsum.photos/id/1042/800/500", "demo_car3.jpg"),
    ("https://picsum.photos/id/1059/800/500", "demo_car4.jpg"),
    ("https://picsum.photos/id/1062/800/500", "demo_car5.jpg"),
    ("https://picsum.photos/id/1071/800/500", "demo_city1.jpg"),
    ("https://picsum.photos/id/1072/800/500", "demo_city2.jpg"),
    ("https://picsum.photos/id/1081/800/500", "demo_city3.jpg"),
    ("https://picsum.photos/id/1084/800/500", "demo_city4.jpg"),
    ("https://picsum.photos/id/1089/800/500", "demo_city5.jpg"),
]

print("下载更多演示图片...")
ok = 0
for url, filename in images:
    filepath = os.path.join(output_dir, filename)
    if os.path.exists(filepath):
        ok += 1
        continue
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            with open(filepath, "wb") as f:
                f.write(data)
        print(f"  ✅ {filename} ({len(data)/1024:.1f}KB)")
        ok += 1
    except Exception as e:
        print(f"  ❌ {filename}: {e}")

print(f"\n成功 {ok}/{len(images)} 张")
