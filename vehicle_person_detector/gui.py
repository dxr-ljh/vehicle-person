import os
import sys
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import threading
import numpy as np

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_dir)

from detector import VehiclePersonDetector, TARGET_CLASSES, CLASS_COLORS
from generate_data import generate_test_video, generate_test_image


class DetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("汽车与行人检测系统")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        self.root.minsize(1000, 650)

        self.detector = None
        self.current_image = None
        self.current_image_cv = None
        self.current_video_path = None
        self.is_running = False
        self._current_rgb_image = None
        self._resize_job = None

        self.setup_ui()
        self.load_model_async()

    def setup_ui(self):
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Microsoft YaHei", 16, "bold"))
        style.configure("Big.TButton", font=("Microsoft YaHei", 11), padding=8)
        style.configure("Result.TLabel", font=("Microsoft YaHei", 12, "bold"))

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(main_frame, text="🚗 汽车与行人检测系统", style="Title.TLabel")
        title.pack(pady=(0, 5))

        subtitle = ttk.Label(main_frame, text="基于 YOLOv8 (PyTorch) 目标检测",
                             font=("Microsoft YaHei", 10), foreground="gray")
        subtitle.pack(pady=(0, 10))

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.LabelFrame(content_frame, text="显示区域", padding=8)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        self.canvas = tk.Canvas(left_frame, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        self.canvas_text = ttk.Label(left_frame, text="请选择图片或视频进行检测",
                                     font=("Microsoft YaHei", 12), foreground="#aaaaaa",
                                     background="#1e1e1e")
        self.canvas_text.place(relx=0.5, rely=0.5, anchor="center")

        right_frame = ttk.Frame(content_frame, width=320)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        right_frame.pack_propagate(False)

        img_frame = ttk.LabelFrame(right_frame, text="🖼️ 图片检测", padding=8)
        img_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Button(img_frame, text="选择图片", style="Big.TButton",
                   command=self.select_image).pack(fill=tk.X, pady=2)
        ttk.Button(img_frame, text="生成测试图", style="Big.TButton",
                   command=self.generate_test_image).pack(fill=tk.X, pady=2)
        self.detect_img_btn = ttk.Button(img_frame, text="🔍 检测图片", style="Big.TButton",
                                          command=self.detect_current_image, state=tk.DISABLED)
        self.detect_img_btn.pack(fill=tk.X, pady=2)

        video_frame = ttk.LabelFrame(right_frame, text="🎬 视频检测", padding=8)
        video_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Button(video_frame, text="选择视频", style="Big.TButton",
                   command=self.select_video).pack(fill=tk.X, pady=2)
        ttk.Button(video_frame, text="生成测试视频", style="Big.TButton",
                   command=self.generate_test_video).pack(fill=tk.X, pady=2)
        self.detect_vid_btn = ttk.Button(video_frame, text="▶️ 检测视频", style="Big.TButton",
                                          command=self.detect_video, state=tk.DISABLED)
        self.detect_vid_btn.pack(fill=tk.X, pady=2)
        self.stop_vid_btn = ttk.Button(video_frame, text="⏹️ 停止检测", style="Big.TButton",
                                        command=self.stop_video, state=tk.DISABLED)
        self.stop_vid_btn.pack(fill=tk.X, pady=2)

        setting_frame = ttk.LabelFrame(right_frame, text="⚙️ 设置", padding=8)
        setting_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(setting_frame, text="置信度阈值:", font=("Microsoft YaHei", 9)).pack(anchor="w")
        self.conf_var = tk.DoubleVar(value=0.5)
        self.conf_slider = ttk.Scale(setting_frame, from_=0.1, to=0.9,
                                     variable=self.conf_var, command=self.on_conf_change)
        self.conf_slider.pack(fill=tk.X, pady=(2, 0))
        self.conf_label = ttk.Label(setting_frame, text="0.50", font=("Consolas", 9))
        self.conf_label.pack(anchor="e")

        tip_frame = ttk.LabelFrame(right_frame, text="💡 使用提示", padding=8)
        tip_frame.pack(fill=tk.X, pady=(0, 8))
        tip_text = "• 真实照片/视频效果最佳\n• 合成图仅用于演示流程\n• 支持 MP4/AVI/MOV 视频格式\n• 检测类别：汽车、行人"
        ttk.Label(tip_frame, text=tip_text, font=("Microsoft YaHei", 8),
                  foreground="#666", justify=tk.LEFT).pack(anchor="w")

        result_frame = ttk.LabelFrame(right_frame, text="📊 检测结果", padding=8)
        result_frame.pack(fill=tk.BOTH, expand=True)

        self.result_text = tk.Text(result_frame, height=18, font=("Consolas", 10),
                                   state=tk.DISABLED, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        self.progress_var = tk.StringVar(value="准备中...")
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(10, 0))

        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X)

        self.status_label = ttk.Label(progress_frame, textvariable=self.progress_var,
                                      font=("Microsoft YaHei", 9), foreground="blue")
        self.status_label.pack(anchor="w", pady=(3, 0))

    def set_status(self, text):
        self.progress_var.set(text)
        self.root.update_idletasks()

    def load_model_async(self):
        self.set_status("正在加载 YOLOv8 模型...")

        def do_load():
            try:
                self.detector = VehiclePersonDetector(model_size="n", conf_threshold=0.5)
                self.detector.load_model()
                self.root.after(0, self.on_model_loaded)
            except Exception as e:
                self.root.after(0, lambda: self.on_model_error(str(e)))

        threading.Thread(target=do_load, daemon=True).start()

    def on_model_loaded(self):
        self.detector.conf_threshold = self.conf_var.get()
        self.set_status("✅ 模型加载完成 - 就绪（检测类别：汽车、行人）")

    def on_model_error(self, msg):
        self.set_status(f"模型加载失败: {msg}")
        messagebox.showerror("错误", f"模型加载失败:\n{msg}\n\n请检查网络连接，首次使用需要下载模型。")

    def on_conf_change(self, value):
        conf = float(value)
        self.conf_label.config(text=f"{conf:.2f}")
        if self.detector is not None:
            self.detector.conf_threshold = conf

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp"), ("所有文件", "*.*")]
        )
        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path):
        try:
            img_cv = cv2.imread(file_path)
            if img_cv is None:
                raise ValueError("无法读取图片")
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
            self.current_image_cv = img_cv
            self.current_image_path = file_path
            self.show_image_on_canvas(img_cv)
            self.detect_img_btn.config(state=tk.NORMAL)
            self.set_status(f"已加载图片: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("错误", f"加载图片失败: {str(e)}")

    def show_image_on_canvas(self, img_rgb):
        self._current_rgb_image = img_rgb
        self._render_image()

    def _render_image(self):
        if self._current_rgb_image is None:
            return

        self.canvas.delete("all")
        self.canvas_text.place_forget()

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        if canvas_w < 10 or canvas_h < 10:
            canvas_w, canvas_h = 600, 400

        h, w = self._current_rgb_image.shape[:2]
        scale = min(canvas_w / w, canvas_h / h)
        new_w, new_h = int(w * scale), int(h * scale)

        if new_w < 1:
            new_w = 1
        if new_h < 1:
            new_h = 1

        img_pil = Image.fromarray(self._current_rgb_image)
        img_pil = img_pil.resize((new_w, new_h), Image.LANCZOS)
        self._photo = ImageTk.PhotoImage(img_pil)

        x = (canvas_w - new_w) // 2
        y = (canvas_h - new_h) // 2
        self.canvas.create_image(x, y, anchor="nw", image=self._photo)

    def _on_canvas_resize(self, event):
        if self._current_rgb_image is None:
            return
        if self._resize_job is not None:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(100, self._do_resize)

    def _do_resize(self):
        self._resize_job = None
        self._render_image()

    def generate_test_image(self):
        output_dir = os.path.join(base_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        img_path = os.path.join(output_dir, "test_image.jpg")
        generate_test_image(img_path)
        self.load_image(img_path)
        self.set_status("已生成测试图片")

    def detect_current_image(self):
        if self.current_image_cv is None or self.detector is None:
            return

        self.detect_img_btn.config(state=tk.DISABLED)
        self.set_status("正在检测...")

        def do_detect():
            try:
                detections = self.detector.detect_image(
                    cv2.cvtColor(self.current_image_cv, cv2.COLOR_RGB2BGR)
                )
                annotated = self.detector.draw_detections(
                    cv2.cvtColor(self.current_image_cv, cv2.COLOR_RGB2BGR),
                    detections
                )
                annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                self.root.after(0, lambda: self.show_detection_result(annotated_rgb, detections))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"检测失败: {str(e)}"))
                self.root.after(0, lambda: self.detect_img_btn.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.set_status("检测失败"))

        threading.Thread(target=do_detect, daemon=True).start()

    def show_detection_result(self, img_rgb, detections):
        self.show_image_on_canvas(img_rgb)

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)

        person_count = sum(1 for d in detections if d["class"] == "person")
        car_count = sum(1 for d in detections if d["class"] in ("car", "bus", "truck"))

        self.result_text.insert(tk.END, "📊 检测结果统计\n", "title")
        self.result_text.insert(tk.END, "═" * 30 + "\n\n")
        self.result_text.insert(tk.END, f"  👤 行人: {person_count} 个\n", "person")
        self.result_text.insert(tk.END, f"  🚗 汽车: {car_count} 辆\n", "car")
        self.result_text.insert(tk.END, f"  📦 总计: {len(detections)} 个目标\n\n")

        if detections:
            self.result_text.insert(tk.END, "📋 详细列表\n", "subtitle")
            self.result_text.insert(tk.END, "─" * 30 + "\n")
            for i, det in enumerate(detections, 1):
                x1, y1, x2, y2 = det["bbox"]
                self.result_text.insert(
                    tk.END,
                    f"  {i:>2}. {det['class_cn']:>4} | "
                    f"置信度: {det['confidence']*100:5.1f}% | "
                    f"位置: ({x1},{y1})-({x2},{y2})\n"
                )

        self.result_text.tag_config("title", font=("Microsoft YaHei", 12, "bold"), foreground="#2c3e50")
        self.result_text.tag_config("person", font=("Microsoft YaHei", 11, "bold"), foreground="#27ae60")
        self.result_text.tag_config("car", font=("Microsoft YaHei", 11, "bold"), foreground="#e74c3c")
        self.result_text.tag_config("subtitle", font=("Microsoft YaHei", 10, "bold"), foreground="#2980b9")

        self.result_text.config(state=tk.DISABLED)
        self.detect_img_btn.config(state=tk.NORMAL)
        self.set_status(f"检测完成 - 行人: {person_count}, 汽车: {car_count}")

    def select_video(self):
        file_path = filedialog.askopenfilename(
            title="选择视频",
            filetypes=[("视频文件", "*.mp4 *.avi *.mov *.mkv"), ("所有文件", "*.*")]
        )
        if file_path:
            self.current_video_path = file_path
            self.detect_vid_btn.config(state=tk.NORMAL)
            self.set_status(f"已选择视频: {os.path.basename(file_path)}")

            cap = cv2.VideoCapture(file_path)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.current_image_cv = frame_rgb
                    self.show_image_on_canvas(frame_rgb)
                cap.release()

    def generate_test_video(self):
        output_dir = os.path.join(base_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        video_path = os.path.join(output_dir, "test_video.mp4")
        self.set_status("正在生成测试视频...")

        def do_gen():
            generate_test_video(video_path, duration=5)
            self.root.after(0, lambda: self.on_video_generated(video_path))

        threading.Thread(target=do_gen, daemon=True).start()

    def on_video_generated(self, video_path):
        self.current_video_path = video_path
        self.detect_vid_btn.config(state=tk.NORMAL)

        cap = cv2.VideoCapture(video_path)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.current_image_cv = frame_rgb
                self.show_image_on_canvas(frame_rgb)
            cap.release()

        self.set_status("测试视频生成完成 (5秒)")

    def detect_video(self):
        if self.current_video_path is None or self.detector is None:
            return

        self.detect_vid_btn.config(state=tk.DISABLED)
        self.detect_img_btn.config(state=tk.DISABLED)
        self.stop_vid_btn.config(state=tk.NORMAL)
        self.is_running = True
        self._stop_video = False

        output_dir = os.path.join(base_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "result_video.mp4")

        self.progress_bar["value"] = 0
        self.set_status("正在检测视频...")

        def do_detect():
            try:
                cap = cv2.VideoCapture(self.current_video_path)
                if not cap.isOpened():
                    raise ValueError("无法打开视频文件")

                fps = cap.get(cv2.CAP_PROP_FPS)
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                if fps <= 0:
                    fps = 25

                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

                frame_interval = 1.0 / fps
                start_time = time.time()

                all_detections = []
                frame_idx = 0

                while not self._stop_video:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    detections = self.detector.detect_image(frame)
                    all_detections.append(detections)

                    annotated = self.detector.draw_detections(frame, detections)
                    writer.write(annotated)

                    annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                    frame_idx += 1

                    self.root.after(0, lambda f=annotated_rgb, i=frame_idx, t=total_frames,
                                           d=detections: self._update_video_frame(f, i, t, d))

                    elapsed = time.time() - start_time
                    expected = frame_idx * frame_interval
                    if elapsed < expected:
                        time.sleep(expected - elapsed)

                cap.release()
                writer.release()

                if self._stop_video:
                    self.root.after(0, lambda: self.set_status("视频检测已停止"))
                else:
                    self.root.after(0, lambda: self.on_video_done(
                        all_detections, output_path, fps))

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"检测失败: {str(e)}"))
                self.root.after(0, self.reset_buttons)
                self.root.after(0, lambda: self.set_status("检测失败"))

        threading.Thread(target=do_detect, daemon=True).start()

    def _update_video_frame(self, frame_rgb, current, total, detections):
        self._current_rgb_image = frame_rgb
        self._render_image()

        if total > 0:
            pct = (current / total) * 100
            self.progress_bar["value"] = pct

        persons = sum(1 for d in detections if d["class"] == "person")
        cars = sum(1 for d in detections if d["class"] in ("car", "bus", "truck"))
        self.set_status(f"检测中... 第 {current}/{total} 帧 | 行人: {persons} 汽车: {cars}")

    def update_video_progress(self, pct, current, total):
        self.progress_bar["value"] = pct
        self.set_status(f"检测中... {current}/{total} 帧 ({pct:.1f}%)")

    def on_video_done(self, all_detections, output_path, fps):
        total_persons = 0
        total_cars = 0
        max_persons = 0
        max_cars = 0
        for frame_dets in all_detections:
            p = sum(1 for d in frame_dets if d["class"] == "person")
            c = sum(1 for d in frame_dets if d["class"] in ("car", "bus", "truck"))
            total_persons += p
            total_cars += c
            max_persons = max(max_persons, p)
            max_cars = max(max_cars, c)

        avg_persons = total_persons / len(all_detections) if all_detections else 0
        avg_cars = total_cars / len(all_detections) if all_detections else 0

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)

        self.result_text.insert(tk.END, "🎬 视频检测结果\n", "title")
        self.result_text.insert(tk.END, "═" * 35 + "\n\n")
        self.result_text.insert(tk.END, f"  总帧数: {len(all_detections)}\n")
        self.result_text.insert(tk.END, f"  视频帧率: {fps:.1f} FPS\n")
        self.result_text.insert(tk.END, f"  输出文件: {os.path.basename(output_path)}\n\n")

        self.result_text.insert(tk.END, "👤 行人统计\n", "person_title")
        self.result_text.insert(tk.END, "─" * 35 + "\n")
        self.result_text.insert(tk.END, f"    累计检测: {total_persons} 人次\n")
        self.result_text.insert(tk.END, f"    单帧最多: {max_persons} 人\n")
        self.result_text.insert(tk.END, f"    平均每帧: {avg_persons:.1f} 人\n\n")

        self.result_text.insert(tk.END, "🚗 汽车统计\n", "car_title")
        self.result_text.insert(tk.END, "─" * 35 + "\n")
        self.result_text.insert(tk.END, f"    累计检测: {total_cars} 辆次\n")
        self.result_text.insert(tk.END, f"    单帧最多: {max_cars} 辆\n")
        self.result_text.insert(tk.END, f"    平均每帧: {avg_cars:.1f} 辆\n")

        self.result_text.tag_config("title", font=("Microsoft YaHei", 12, "bold"), foreground="#2c3e50")
        self.result_text.tag_config("person_title", font=("Microsoft YaHei", 11, "bold"), foreground="#27ae60")
        self.result_text.tag_config("car_title", font=("Microsoft YaHei", 11, "bold"), foreground="#e74c3c")

        self.result_text.config(state=tk.DISABLED)

        self.progress_bar["value"] = 100
        self.set_status(f"视频检测完成 - 输出: {output_path}")
        self.reset_buttons()

        cap = cv2.VideoCapture(output_path)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.show_image_on_canvas(frame_rgb)
            cap.release()

        messagebox.showinfo("完成", f"视频检测完成！\n\n"
                             f"输出文件: {output_path}\n"
                             f"行人: 平均 {avg_persons:.1f}人/帧\n"
                             f"汽车: 平均 {avg_cars:.1f}辆/帧")

    def stop_video(self):
        self._stop_video = True
        self.stop_vid_btn.config(state=tk.DISABLED)
        self.set_status("正在停止...")

    def reset_buttons(self):
        self.detect_vid_btn.config(state=tk.NORMAL if self.current_video_path else tk.DISABLED)
        self.detect_img_btn.config(state=tk.NORMAL if self.current_image_cv is not None else tk.DISABLED)
        self.stop_vid_btn.config(state=tk.DISABLED)
        self.is_running = False


def main():
    root = tk.Tk()
    app = DetectorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
