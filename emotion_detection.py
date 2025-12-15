import cv2
import tkinter as tk
from tkinter import messagebox

try:
    from fer import FER
    FER_AVAILABLE = True
    print("✅ FER library loaded!")
except Exception as e:
    FER_AVAILABLE = False
    print(f"❌ FER not available: {e}")

class EmotionDetection:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("😊 Emotion Detection")
        self.root.geometry("500x400")
        self.root.configure(bg='#0f172a')
        
        self.is_running = False
        
        if FER_AVAILABLE:
            try:
                self.emotion_detector = FER(mtcnn=False)
                print("✅ Emotion detector initialized!")
            except Exception as e:
                print(f"❌ Failed to init detector: {e}")
                self.emotion_detector = None
        else:
            self.emotion_detector = None
        
        self.setup_gui()
    
    def setup_gui(self):
        header = tk.Frame(self.root, bg='#f59e0b', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Label(header, text="😊 Emotion Detection", font=('Helvetica', 24, 'bold'),
                bg='#f59e0b', fg='white').pack(pady=25)
        
        container = tk.Frame(self.root, bg='#1e293b', relief='raised', bd=2)
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        if FER_AVAILABLE and self.emotion_detector:
            tk.Label(container, text="Camera will open in separate window",
                    font=('Helvetica', 12), bg='#1e293b', fg='#10b981').pack(pady=20)
        else:
            tk.Label(container, text="⚠️ FER not working - only face detection available",
                    font=('Helvetica', 11), bg='#1e293b', fg='#f59e0b').pack(pady=20)
        
        self.status_label = tk.Label(container, text="Status: Idle", 
                                     font=('Helvetica', 12, 'bold'), bg='#1e293b', fg='white')
        self.status_label.pack(pady=20)
        
        btn_frame = tk.Frame(container, bg='#1e293b')
        btn_frame.pack(pady=20)
        
        self.start_btn = tk.Button(btn_frame, text="▶️ Start Detection", 
                                   command=self.start_detection,
                                   bg='#10b981', fg='white', font=('Helvetica', 13, 'bold'),
                                   relief='flat', padx=30, pady=12, cursor='hand2')
        self.start_btn.pack(side='left', padx=10)
        
        self.stop_btn = tk.Button(btn_frame, text="⏹️ Stop Detection", 
                                  command=self.stop_detection,
                                  bg='#ef4444', fg='white', font=('Helvetica', 13, 'bold'),
                                  relief='flat', padx=30, pady=12, cursor='hand2', state='disabled')
        self.stop_btn.pack(side='left', padx=10)
        
        camera_frame = tk.Frame(container, bg='#1e293b')
        camera_frame.pack(pady=10)
        
        tk.Label(camera_frame, text="Camera:", font=('Helvetica', 10),
                bg='#1e293b', fg='white').pack(side='left', padx=(0, 10))
        
        self.camera_var = tk.StringVar(value="0")
        tk.Radiobutton(camera_frame, text="Camera 0", variable=self.camera_var, value="0",
                      bg='#1e293b', fg='white', selectcolor='#334155',
                      font=('Helvetica', 10)).pack(side='left', padx=5)
        tk.Radiobutton(camera_frame, text="Camera 1", variable=self.camera_var, value="1",
                      bg='#1e293b', fg='white', selectcolor='#334155',
                      font=('Helvetica', 10)).pack(side='left', padx=5)
        
        tk.Label(container, text="💡 Press 'Q' in camera window to stop",
                bg='#1e293b', fg='#94a3b8', font=('Helvetica', 9)).pack(pady=10)
    
    def start_detection(self):
        print("🔵 Starting detection...")
        camera_index = int(self.camera_var.get())
        
        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(text="Status: Running ✅", fg='#10b981')
        
        try:
            cap = cv2.VideoCapture(camera_index)
            
            if not cap.isOpened():
                raise RuntimeError(f"Camera {camera_index} not accessible")
            
            print("✅ Camera opened!")
            
            while self.is_running:
                ret, frame = cap.read()
                
                if not ret:
                    print("❌ Can't read frame")
                    break
                
                # Try emotion detection if available
                if self.emotion_detector:
                    try:
                        results = self.emotion_detector.detect_emotions(frame)
                        
                        if results:
                            for result in results:
                                x, y, w, h = result["box"]
                                emotions = result["emotions"]
                                top_emotion = max(emotions, key=emotions.get)
                                confidence = emotions[top_emotion]
                                
                                # Draw rectangle
                                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                                
                                # Show top emotion
                                label = f"{top_emotion} ({confidence*100:.1f}%)"
                                cv2.putText(frame, label, (x, y-10),
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
                                
                                # Show top 3 emotions
                                y_offset = y + h + 25
                                for emotion, score in sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]:
                                    text = f"{emotion}: {score*100:.0f}%"
                                    cv2.putText(frame, text, (x, y_offset),
                                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                                    y_offset += 20
                        else:
                            # No face detected
                            cv2.putText(frame, "No face detected", (10, 30),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    except Exception as e:
                        print(f"⚠️ Emotion detection error: {e}")
                        # Fallback to simple face detection
                        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                        
                        for (x, y, w, h) in faces:
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                            cv2.putText(frame, "Face (no emotion)", (x, y-10),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    # Simple face detection only
                    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                    
                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        cv2.putText(frame, "Face Detected", (x, y-10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    
                    if len(faces) > 0:
                        cv2.putText(frame, f"Faces: {len(faces)}", (10, 30),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                cv2.imshow('Emotion Detection - Press Q to quit', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                self.root.update()
            
            cap.release()
            cv2.destroyAllWindows()
            print("✅ Camera closed")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            messagebox.showerror("Error", f"Camera error:\n{str(e)}\n\nTry the other camera option.")
        
        self.stop_detection()
    
    def stop_detection(self):
        print("🔴 Stopping...")
        self.is_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="Status: Stopped", fg='#ef4444')
        cv2.destroyAllWindows()
        print("✅ Stopped")
    
    def run(self):
        def on_close():
            self.is_running = False
            cv2.destroyAllWindows()
            self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_close)
        self.root.mainloop()

if __name__ == "__main__":
    print("="*50)
    print("EMOTION DETECTION")
    print("="*50)
    app = EmotionDetection()
    app.run()