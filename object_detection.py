import cv2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
classFile = os.path.join(BASE_DIR, "coco.names")
configPath = os.path.join(BASE_DIR, "ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt")
weightsPath = os.path.join(BASE_DIR, "frozen_inference_graph.pb")

FILES_EXIST = all(os.path.exists(f) for f in [classFile, configPath, weightsPath])

class ObjectDetection:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📷 Object Detection")
        self.root.geometry("900x750")
        self.root.configure(bg='#0f172a')
        
        self.is_running = False
        self.last_time = time.time()
        self.cap = None
        
        if FILES_EXIST:
            with open(classFile, "r") as f:
                self.classNames = f.read().strip().split("\n")
            
            self.net = cv2.dnn_DetectionModel(weightsPath, configPath)
            self.net.setInputSize(320, 320)
            self.net.setInputScale(1 / 127.5)
            self.net.setInputMean((127.5, 127.5, 127.5))
            self.net.setInputSwapRB(True)
        
        self.setup_gui()
    
    def setup_gui(self):
        header = tk.Frame(self.root, bg='#10b981', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Label(header, text="📷 Object Detection", font=('Helvetica', 24, 'bold'),
                bg='#10b981', fg='white').pack(pady=25)
        
        container = tk.Frame(self.root, bg='#1e293b', relief='raised', bd=2)
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text="Real-time Object Detection using SSD MobileNet",
                font=('Helvetica', 12), bg='#1e293b', fg='#94a3b8').pack(pady=(20, 10))
        
        self.video_label = tk.Label(container, bg='black')
        self.video_label.pack(padx=20, pady=20)
        
        self.status_label = tk.Label(container, text="Status: Idle", 
                                     font=('Helvetica', 12, 'bold'), bg='#1e293b', fg='white')
        self.status_label.pack(pady=10)
        
        btn_frame = tk.Frame(container, bg='#1e293b')
        btn_frame.pack(pady=10)
        
        self.start_btn = tk.Button(btn_frame, text="▶️ Start Detection", command=self.start_detection,
                                   bg='#10b981', fg='white', font=('Helvetica', 13, 'bold'),
                                   relief='flat', padx=30, pady=12, cursor='hand2')
        self.start_btn.pack(side='left', padx=10)
        
        self.stop_btn = tk.Button(btn_frame, text="⏹️ Stop Detection", command=self.stop_detection,
                                  bg='#ef4444', fg='white', font=('Helvetica', 13, 'bold'),
                                  relief='flat', padx=30, pady=12, cursor='hand2', state='disabled')
        self.stop_btn.pack(side='left', padx=10)
        
        camera_frame = tk.Frame(container, bg='#1e293b')
        camera_frame.pack(pady=5)
        
        tk.Label(camera_frame, text="Camera:", font=('Helvetica', 10),
                bg='#1e293b', fg='white').pack(side='left', padx=(0, 10))
        
        self.camera_var = tk.StringVar(value="0")
        tk.Radiobutton(camera_frame, text="Camera 0", variable=self.camera_var, value="0",
                      bg='#1e293b', fg='white', selectcolor='#334155',
                      font=('Helvetica', 10)).pack(side='left', padx=5)
        tk.Radiobutton(camera_frame, text="Camera 1", variable=self.camera_var, value="1",
                      bg='#1e293b', fg='white', selectcolor='#334155',
                      font=('Helvetica', 10)).pack(side='left', padx=5)
        
        footer = tk.Frame(self.root, bg='#0f172a')
        footer.pack(fill='x', side='bottom', pady=(0, 10))
        
        if not FILES_EXIST:
            tk.Label(footer, text="⚠️ Missing files: coco.names, .pbtxt, .pb",
                    bg='#0f172a', fg='#f59e0b', font=('Helvetica', 9)).pack(pady=5)
            self.start_btn.config(state='disabled')
        else:
            tk.Label(footer, text="💡 Camera feed displays in this window",
                    bg='#0f172a', fg='#94a3b8', font=('Helvetica', 9)).pack(pady=5)
    
    def start_detection(self):
        if not FILES_EXIST:
            messagebox.showerror("Error", "Model files not found!")
            return
        
        camera_index = int(self.camera_var.get())
        
        try:
            self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)  # Windows optimization
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            if not self.cap.isOpened():
                raise RuntimeError(f"Camera {camera_index} not accessible")
            
            ret, test_frame = self.cap.read()
            if not ret:
                self.cap.release()
                raise RuntimeError(f"Camera {camera_index} can't read frames")
            
            self.is_running = True
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.status_label.config(text="Status: Detection Running ✅", fg='#10b981')
            self.last_time = time.time()
            self.update()
            
        except Exception as e:
            messagebox.showerror("Camera Error", f"Failed to start camera:\n{str(e)}")
            if self.cap:
                self.cap.release()
    
    def stop_detection(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="Status: Stopped", fg='#ef4444')
        self.video_label.config(image='')
    
    def update(self):
        if not self.is_running or not self.cap:
            return
        
        ret, frame = self.cap.read()
        if not ret:
            self.stop_detection()
            return
        
        try:
            classIds, confs, boxes = self.net.detect(frame, confThreshold=0.5)
            
            if len(classIds) > 0:
                for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), boxes):
                    label = f"{self.classNames[classId - 1]} {confidence:.2f}"
                    cv2.rectangle(frame, box, (0, 255, 0), 2)
                    cv2.putText(frame, label, (box[0], box[1] - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        except Exception as e:
            print(f"Detection error: {e}")
        
        current_time = time.time()
        fps = 1 / (current_time - self.last_time)
        self.last_time = current_time
        cv2.putText(frame, f"FPS: {int(fps)}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        frame = cv2.resize(frame, (640, 480))
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(rgb))
        self.video_label.config(image=img)
        self.video_label.image = img
        
        self.root.after(30, self.update)
    
    def run(self):
        def on_close():
            self.is_running = False
            if self.cap:
                self.cap.release()
            self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_close)
        self.root.mainloop()

if __name__ == "__main__":
    app = ObjectDetection()
    app.run()