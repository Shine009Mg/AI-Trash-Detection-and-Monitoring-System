import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from roboflow import Roboflow
import cv2
from datetime import datetime
import math
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
from PIL import Image, ImageTk
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Roboflow Setup
rf = Roboflow(api_key="CqyEeTN5eILbFqISpz5b")
project = rf.workspace().project("-garbage")
model = project.version("1").model

# Email Configuration
EMAIL_SENDER = 'trashtrack001@gmail.com'
EMAIL_PASSWORD = 'ndas qjsk uouy nkea'
EMAIL_RECEIVER = 'shinelinhtet.ec@gmail.com'

# InfluxDB Configuration
token = "_LCIX_vllrDU1cCh8u3Mvgs4YjhuiW3LBmaYYn057dnJnmV4cvtSdLXEe0jFXm1BBFnZ6g27jYQTAbq9y9xmuw=="
org = "Student Research"
bucket = "Trash Data Bucket"
url = "https://us-east-1-1.aws.cloud2.influxdata.com"

# File Paths
BASE_PATH = "E:\\Kasetsart University Sriracha Campus\\2nd Sem\\Computer Progarmming Project"
TEMP_IMAGE_PATH = os.path.join(BASE_PATH, "temp_frame.jpg")
LOG_PATH = os.path.join(BASE_PATH, "predition_result.txt")
CAPTURE_FOLDER = os.path.join(BASE_PATH, "captured")
os.makedirs(CAPTURE_FOLDER, exist_ok=True)

class TrashDetectionSystem:
    def __init__(self):
        self.running = False
        self.counted_trash_centers = []
        self.trash_type_count = defaultdict(int)
        self.overall_trash_count = 0
        self.minute_detection_count = defaultdict(int)
        self.latest_captured_image = ""
        self.last_alert_minute = -1
        self.DIST_THRESHOLD = 50
        self.influx_client = InfluxDBClient(url=url, token=token, org=org)
        self.influx_write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)

    def send_email(self, subject, body):
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_SENDER
            msg['To'] = EMAIL_RECEIVER
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.send_message(msg)
            self.append_log("[INFO] Email alert sent.")
        except Exception as e:
            self.append_log(f"[ERROR] Failed to send email: {e}")

    def send_to_influx(self, trash_type, confidence, timestamp):
        point = (
            Point("trash_detection")
            .tag("location", "Zone 1")
            .field("type", trash_type)
            .field("confidence", float(confidence))
            .time(timestamp)
        )
        self.influx_write_api.write(bucket=bucket, org=org, record=point)

    def get_center(self, pred):
        return (pred['x'], pred['y'])

    def euclidean_distance(self, p1, p2):
        return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    def is_new_trash(self, center):
        return all(self.euclidean_distance(center, c) >= self.DIST_THRESHOLD for c in self.counted_trash_centers)

    def detect_trash(self):
        cap = cv2.VideoCapture(0)
        self.counted_trash_centers = []

        try:
            while self.running and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                cv2.imwrite(TEMP_IMAGE_PATH, frame)
                confidence = confidence_slider.get()
                data = model.predict(TEMP_IMAGE_PATH, confidence=confidence, overlap=30).json()

                now = datetime.now()
                timestamp_for_file = now.strftime("%Y%m%d_%H%M%S")
                timestamp_for_log = now.strftime("%Y-%m-%d %H:%M:%S")
                minute = now.minute

                if data['predictions']:
                    for i, pred in enumerate(data['predictions']):
                        center = self.get_center(pred)
                        if self.is_new_trash(center):
                            self.counted_trash_centers.append(center)

                            x = int(pred['x'] - pred['width'] / 2)
                            y = int(pred['y'] - pred['height'] / 2)
                            w = int(pred['width'])
                            h = int(pred['height'])
                            confidence_percent = int(pred['confidence'] * 100)
                            trash_type = pred['class'].replace(" ", "_")

                            label = f"{trash_type} ({confidence_percent}%)"
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                            capture_name = f"{trash_type}_{confidence_percent}pct_{timestamp_for_file}_{i}.jpg"
                            capture_path = os.path.join(CAPTURE_FOLDER, capture_name)
                            cv2.imwrite(capture_path, frame)

                            log_text = f"[{timestamp_for_log}] Detected trash: {trash_type} with confidence {confidence_percent}%"
                            self.append_log(log_text)
                            self.send_to_influx(trash_type, confidence_percent, now)

                            self.latest_captured_image = capture_path
                            self.minute_detection_count[minute] += 1
                            self.overall_trash_count += 1
                            self.trash_type_count[trash_type] += 1

                if self.minute_detection_count[minute] > 5 and minute != self.last_alert_minute:
                    subject = "⚠️ High Trash Activity Detected"
                    body = (
                        f"{self.minute_detection_count[minute]} trash items detected at {timestamp_for_log}.\n"
                        f"Types: {dict(self.trash_type_count)}"
                    )
                    self.send_email(subject, body)
                    self.last_alert_minute = minute

                if self.latest_captured_image:
                    self.update_displayed_image(self.latest_captured_image)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            cap.release()
            cv2.destroyAllWindows()

    def append_log(self, text):
        log_output.insert(tk.END, text + "\n")
        log_output.see(tk.END)
        with open(LOG_PATH, "a") as f:
            f.write(text + "\n")

    def update_displayed_image(self, image_path):
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = img.resize((300, 300))
        img_tk = ImageTk.PhotoImage(img)
        image_label.config(image=img_tk)
        image_label.image = img_tk

    def update_trash_counts(self):
        overall_label.config(text=f"Overall Trash Count: {self.overall_trash_count}")
        trash_label.config(text=f"Trash Types Count: {dict(self.trash_type_count)}")

        pie_ax.clear()
        labels = list(self.trash_type_count.keys())
        sizes = list(self.trash_type_count.values())
        if sizes:
            pie_ax.pie(sizes, labels=labels, autopct=lambda p: f'{int(p * sum(sizes) / 100)}', startangle=140)
            pie_ax.set_title("Trash Type Distribution (Raw Count)")
        else:
            pie_ax.text(0.5, 0.5, "No Data Yet", ha='center', va='center', fontsize=12)
        pie_canvas.draw()

        line_ax.clear()
        all_minutes = list(range(0, 60))
        for minute in all_minutes:
            if minute not in self.minute_detection_count:
                self.minute_detection_count[minute] = 0
        minutes = sorted(self.minute_detection_count.keys())
        counts = [self.minute_detection_count[minute] for minute in minutes]

        line_ax.plot(minutes, counts, color='blue', marker='o', linestyle='-', linewidth=2, markersize=5)
        line_ax.set_xlabel('Minute of the Hour')
        line_ax.set_ylabel('Trash Detections')
        line_ax.set_title('Minute-Based Trash Density')
        line_ax.grid(True)
        line_canvas.draw()


# GUI Setup
window = tk.Tk()
window.title("Trash Detection GUI")

detector = TrashDetectionSystem()

confidence_slider = tk.Scale(window, from_=30, to=90, orient='horizontal', label='Confidence Threshold (%)')
confidence_slider.set(40)
confidence_slider.pack(pady=5)

def start_detection():
    if not detector.running:
        detector.running = True
        thread = threading.Thread(target=detector.detect_trash)
        thread.daemon = True
        thread.start()
        detector.append_log("[INFO] Detection started.")

def stop_detection():
    detector.running = False
    detector.append_log("[INFO] Detection stopped.")

def show_trend():
    trend_window = tk.Toplevel(window)
    trend_window.title("Minute-Based Trash Trend")
    fig, ax = plt.subplots(figsize=(6, 4))

    if detector.minute_detection_count:
        all_minutes = list(range(0, 60))
        for minute in all_minutes:
            if minute not in detector.minute_detection_count:
                detector.minute_detection_count[minute] = 0

        minutes = sorted(detector.minute_detection_count.keys())
        counts = [detector.minute_detection_count[minute] for minute in minutes]

        ax.plot(minutes, counts, color='blue', marker='o', linestyle='-', linewidth=2, markersize=5)

    ax.set_xlabel('Minute of the Hour')
    ax.set_ylabel('Trash Detections')
    ax.set_title('Minute-Based Trash Density (Line Graph)')
    ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=trend_window)
    canvas.draw()
    canvas.get_tk_widget().pack(padx=10, pady=10)

start_button = tk.Button(window, text="Start Detection", command=start_detection, bg="green", fg="white", width=20)
start_button.pack(pady=5)

stop_button = tk.Button(window, text="Stop Detection", command=stop_detection, bg="red", fg="white", width=20)
stop_button.pack(pady=5)

log_output = ScrolledText(window, width=80, height=15, font=("Consolas", 10))
log_output.pack(padx=10, pady=10)

trend_button = tk.Button(window, text="Show Graph Trend", command=show_trend, bg="blue", fg="white", width=20)
trend_button.pack(pady=5)

overall_label = tk.Label(window, text="Overall Trash Count: 0", font=("Arial", 14))
overall_label.pack(pady=5)

trash_label = tk.Label(window, text="Trash Types Count: {}", font=("Arial", 14))
trash_label.pack(pady=5)

image_pie_frame = tk.Frame(window)
image_pie_frame.pack(padx=10, pady=10)

image_label = tk.Label(image_pie_frame)
image_label.pack(side=tk.LEFT, padx=10)

pie_fig, pie_ax = plt.subplots(figsize=(4, 4))
pie_canvas = FigureCanvasTkAgg(pie_fig, master=image_pie_frame)
pie_canvas.get_tk_widget().pack(side=tk.LEFT, padx=10)

log_graph_frame = tk.Frame(window)
log_graph_frame.pack(padx=10, pady=10)

line_fig, line_ax = plt.subplots(figsize=(5, 4))
line_canvas = FigureCanvasTkAgg(line_fig, master=log_graph_frame)
line_canvas.get_tk_widget().pack(side=tk.LEFT, padx=10)

def update_counts_periodically():
    detector.update_trash_counts()
    window.after(1000, update_counts_periodically)

update_counts_periodically()

def on_closing():
    detector.running = False
    window.destroy()

window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()
