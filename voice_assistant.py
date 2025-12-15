import tkinter as tk
from tkinter import scrolledtext
import threading
import datetime

try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except:
    VOICE_AVAILABLE = False

class VoiceAssistant:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎤 Voice Assistant")
        self.root.geometry("800x700")
        self.root.configure(bg='#0f172a')
        self.voice_listening = False
        
        if VOICE_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
        
        self.setup_gui()
    
    def setup_gui(self):
        header = tk.Frame(self.root, bg='#1e40af', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Label(header, text="🎤 Voice Assistant", font=('Helvetica', 24, 'bold'),
                bg='#1e40af', fg='white').pack(pady=25)
        
        container = tk.Frame(self.root, bg='#1e293b', relief='raised', bd=2)
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.status_frame = tk.Frame(container, bg='#1e293b')
        self.status_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        self.status_indicator = tk.Label(self.status_frame, text="●", font=('Helvetica', 20),
                                        bg='#1e293b', fg='#10b981')
        self.status_indicator.pack(side='left')
        
        self.status_text = tk.Label(self.status_frame, text="Ready", font=('Helvetica', 12, 'bold'),
                                   bg='#1e293b', fg='white')
        self.status_text.pack(side='left', padx=10)
        
        self.chat_display = scrolledtext.ScrolledText(container, height=20, font=('Helvetica', 11),
                                                      bg='#0f172a', fg='white', wrap=tk.WORD,
                                                      padx=15, pady=15)
        self.chat_display.pack(fill='both', expand=True, padx=20, pady=(10, 20))
        
        btn_frame = tk.Frame(container, bg='#1e293b')
        btn_frame.pack(pady=(0, 20))
        
        self.listen_btn = tk.Button(btn_frame, text="🎤 Start Listening",
                                   command=self.toggle_listening, bg='#3b82f6', fg='white',
                                   font=('Helvetica', 13, 'bold'), relief='flat', 
                                   padx=30, pady=12, cursor='hand2')
        self.listen_btn.pack(side='left', padx=10)
        
        tk.Button(btn_frame, text="🗑️ Clear", command=lambda: self.chat_display.delete(1.0, tk.END),
                 bg='#ef4444', fg='white', font=('Helvetica', 13, 'bold'),
                 relief='flat', padx=30, pady=12, cursor='hand2').pack(side='left', padx=10)
        
        footer = tk.Frame(self.root, bg='#0f172a')
        footer.pack(fill='x', side='bottom', pady=(0, 10))
        
        tk.Label(footer, text="💡 Say 'hello', 'time', 'date', 'thanks', 'bye' or anything!",
                font=('Helvetica', 9), bg='#0f172a', fg='#94a3b8').pack()
        
        if not VOICE_AVAILABLE:
            self.add_message("⚠️ Voice features not available!")
            self.add_message("Install: pip install SpeechRecognition pyttsx3 pyaudio")
            self.listen_btn.config(state='disabled')
        else:
            self.add_message("Ready! Click 'Start Listening' to begin.")
    
    def toggle_listening(self):
        if not self.voice_listening:
            self.voice_listening = True
            self.listen_btn.config(text="🛑 Stop Listening", bg='#ef4444')
            self.status_indicator.config(fg='#3b82f6')
            self.status_text.config(text='Listening...')
            threading.Thread(target=self.listen_loop, daemon=True).start()
        else:
            self.voice_listening = False
            self.listen_btn.config(text="🎤 Start Listening", bg='#3b82f6')
            self.status_indicator.config(fg='#10b981')
            self.status_text.config(text='Ready')
    
    def listen_loop(self):
        while self.voice_listening:
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    
                    self.status_text.config(text='Processing...')
                    self.status_indicator.config(fg='#f59e0b')
                    
                    text = self.recognizer.recognize_google(audio)
                    
                    self.add_message(f"You: {text}")
                    response = self.process_command(text)
                    self.add_message(f"Assistant: {response}")
                    
                    self.tts_engine.say(response)
                    self.tts_engine.runAndWait()
                    
                    self.status_text.config(text='Listening...')
                    self.status_indicator.config(fg='#3b82f6')
                    
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                self.add_message("❌ Could not understand audio")
                self.status_text.config(text='Listening...')
            except sr.RequestError as e:
                self.add_message(f"❌ Request error: {e}")
                self.status_text.config(text='Listening...')
            except Exception as e:
                self.add_message(f"❌ Error: {str(e)}")
                break
    
    def process_command(self, text):
        t = text.lower()
        
        if any(w in t for w in ['hello', 'hi', 'hey', 'greetings']):
            return "Hello! How can I help you today?"
        elif 'time' in t:
            return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}"
        elif 'date' in t or 'today' in t:
            return f"Today is {datetime.datetime.now().strftime('%B %d, %Y')}"
        elif 'day' in t:
            return f"Today is {datetime.datetime.now().strftime('%A')}"
        elif 'weather' in t:
            return "I don't have access to weather data right now, but I hope it's nice where you are!"
        elif 'your name' in t or 'who are you' in t:
            return "I'm your AI Voice Assistant, here to help you!"
        elif 'how are you' in t:
            return "I'm doing great, thank you for asking! How can I help you?"
        elif any(w in t for w in ['thank', 'thanks', 'appreciate']):
            return "You're very welcome! Happy to help!"
        elif any(w in t for w in ['bye', 'goodbye', 'see you', 'exit']):
            return "Goodbye! Have a wonderful day!"
        elif 'help' in t:
            return "I can tell you the time, date, day, or just chat with you. Try asking me something!"
        else:
            return f"You said: {text}. I'm learning more commands every day!"
    
    def add_message(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"[{timestamp}] {message}\n\n")
        self.chat_display.see(tk.END)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = VoiceAssistant()
    app.run()