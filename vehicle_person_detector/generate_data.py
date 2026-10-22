import os
import cv2
import numpy as np
import random


def draw_road(img, width, height):
    cv2.rectangle(img, (0, height // 3), (width, height * 2 // 3), (80, 80, 80), -1)
    lane_y = height // 2
    for x in range(0, width, 60):
        cv2.rectangle(img, (x, lane_y - 3), (x + 30, lane_y + 3), (255, 255, 255), -1)
    cv2.rectangle(img, (0, height * 2 // 3), (width, height), (100, 160, 80), -1)
    cv2.rectangle(img, (0, 0), (width, height // 3), (130, 180, 100), -1)
    cv2.rectangle(img, (0, height // 3 - 8), (width, height // 3), (200, 200, 200), -1)
    cv2.rectangle(img, (0, height * 2 // 3), (width, height * 2 // 3 + 8), (200, 200, 200), -1)


def draw_car(img, x, y, color, direction="right"):
    w, h = 70, 35
    if direction == "left":
        x = x - w
    cv2.rectangle(img, (x, y - h // 2), (x + w, y + h // 2), color, -1)
    roof_h = 15
    cv2.rectangle(img, (x + 15, y - h // 2 - roof_h),
                  (x + w - 20, y - h // 2 + 5),
                  tuple(min(255, c + 20) for c in color), -1)
    wheel_r = 6
    cv2.circle(img, (x + 15, y + h // 2), wheel_r, (30, 30, 30), -1)
    cv2.circle(img, (x + w - 15, y + h // 2), wheel_r, (30, 30, 30), -1)
    cv2.circle(img, (x + 15, y - h // 2), wheel_r, (30, 30, 30), -1)
    cv2.circle(img, (x + w - 15, y - h // 2), wheel_r, (30, 30, 30), -1)
    if direction == "right":
        cv2.rectangle(img, (x + w - 5, y - 8), (x + w, y + 8), (255, 255, 150), -1)
    else:
        cv2.rectangle(img, (x, y - 8), (x + 5, y + 8), (255, 255, 150), -1)


def draw_person(img, x, y, direction="right", walking=True, frame_offset=0):
    body_color = (200, 100, 100)
    head_r = 10
    cv2.circle(img, (x, y - 35), head_r, (255, 220, 180), -1)
    cv2.rectangle(img, (x - 10, y - 25), (x + 10, y + 5), body_color, -1)
    leg_offset = int(8 * np.sin(frame_offset * 0.5)) if walking else 0
    cv2.rectangle(img, (x - 8, y + 5), (x - 2, y + 30 + leg_offset), (50, 80, 160), -1)
    cv2.rectangle(img, (x + 2, y + 5), (x + 8, y + 30 - leg_offset), (50, 80, 160), -1)
    arm_offset = int(5 * np.sin(frame_offset * 0.5 + np.pi)) if walking else 0
    cv2.rectangle(img, (x - 15, y - 20 + arm_offset), (x - 10, y + 5), body_color, -1)
    cv2.rectangle(img, (x + 10, y - 20 - arm_offset), (x + 15, y + 5), body_color, -1)


def generate_test_video(output_path, width=640, height=480, fps=20, duration=5):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    total_frames = fps * duration
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    car_colors = [
        (200, 50, 50),
        (50, 50, 200),
        (255, 255, 50),
        (255, 255, 255),
        (50, 50, 50),
        (200, 100, 200),
    ]

    cars_right = [
        {"x": -100, "y": height // 2 + 20, "speed": random.randint(3, 6),
         "color": random.choice(car_colors)}
        for _ in range(3)
    ]
    for i, car in enumerate(cars_right):
        car["x"] = -i * 200

    cars_left = [
        {"x": width + 100, "y": height // 2 - 25, "speed": random.randint(2, 5),
         "color": random.choice(car_colors)}
        for _ in range(2)
    ]
    for i, car in enumerate(cars_left):
        car["x"] = width + i * 180

    pedestrians = [
        {"x": random.randint(50, width - 50),
         "y": height * 2 // 3 + 40 + random.randint(-20, 20),
         "speed": random.uniform(1.0, 2.5),
         "direction": random.choice(["left", "right"])}
        for _ in range(3)
    ]

    for frame_idx in range(total_frames):
        img = np.zeros((height, width, 3), dtype=np.uint8)
        draw_road(img, width, height)

        for car in cars_right:
            draw_car(img, int(car["x"]), int(car["y"]), car["color"], "right")
            car["x"] += car["speed"]
            if car["x"] > width + 100:
                car["x"] = -100
                car["color"] = random.choice(car_colors)
                car["speed"] = random.randint(3, 6)

        for car in cars_left:
            draw_car(img, int(car["x"]), int(car["y"]), car["color"], "left")
            car["x"] -= car["speed"]
            if car["x"] < -100:
                car["x"] = width + 100
                car["color"] = random.choice(car_colors)
                car["speed"] = random.randint(2, 5)

        for ped in pedestrians:
            draw_person(img, int(ped["x"]), int(ped["y"]),
                        ped["direction"], walking=True, frame_offset=frame_idx)
            if ped["direction"] == "right":
                ped["x"] += ped["speed"]
                if ped["x"] > width - 30:
                    ped["direction"] = "left"
            else:
                ped["x"] -= ped["speed"]
                if ped["x"] < 30:
                    ped["direction"] = "right"

        writer.write(img)

    writer.release()
    return output_path


def generate_test_image(output_path, width=640, height=480):
    img = np.zeros((height, width, 3), dtype=np.uint8)
    draw_road(img, width, height)

    draw_car(img, 150, height // 2 + 20, (200, 50, 50), "right")
    draw_car(img, 400, height // 2 - 25, (50, 50, 200), "left")
    draw_person(img, 100, height * 2 // 3 + 40, "right", walking=False)
    draw_person(img, 500, height * 2 // 3 + 40, "left", walking=False)

    cv2.imwrite(output_path, img)
    return output_path


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    video_path = os.path.join(output_dir, "test_video.mp4")
    print(f"生成测试视频: {video_path}")
    generate_test_video(video_path, duration=5)
    print("完成！5秒测试视频已生成")

    img_path = os.path.join(output_dir, "test_image.jpg")
    print(f"生成测试图片: {img_path}")
    generate_test_image(img_path)
    print("完成！测试图片已生成")
