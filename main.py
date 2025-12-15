import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

class AIToolsLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NeuroTask: MultiAI")
        self.root.geometry("600x700")
        self.root.configure(bg='#0f172a')
        self.root.resizable(False, False)
        self.setup_gui()
    
    def setup_gui(self):
        header = tk.Frame(self.root, bg='#1e40af', height=100)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="NeuroTask: MultiAI", 
                font=('Helvetica', 28, 'bold'),
                bg='#1e40af', fg='white').pack(pady=30)
        
        container = tk.Frame(self.root, bg='#0f172a')
        container.pack(fill='both', expand=True, padx=30, pady=30)
        
        tk.Label(container, text="Select an AI Tool to Launch:",
                font=('Helvetica', 14, 'bold'),
                bg='#0f172a', fg='white').pack(anchor='w', pady=(0, 20))
        
        tools = [
            {'name': '🎤 Voice Assistant', 'desc': 'Speech recognition and text-to-speech', 
             'file': 'voice_assistant.py', 'color': '#3b82f6'},
            {'name': '📷 Object Detection', 'desc': 'Real-time object detection', 
             'file': 'object_detection.py', 'color': '#10b981'},
            {'name': '😊 Emotion Detection', 'desc': 'Face emotion recognition', 
             'file': 'emotion_detection.py', 'color': '#f59e0b'},
            {'name': '✅ To-Do List', 'desc': 'Smart task manager', 
             'file': 'todo_list.py', 'color': '#8b5cf6'}
        ]
        
        for tool in tools:
            self.create_tool_button(container, tool)
        
        footer = tk.Frame(self.root, bg='#1e293b', height=60)
        footer.pack(fill='x', side='bottom')
        footer.pack_propagate(False)
        
        tk.Label(footer, text="💡 You can run multiple tools simultaneously",
                font=('Helvetica', 10),
                bg='#1e293b', fg='#94a3b8').pack(pady=20)
    
    def create_tool_button(self, parent, tool):
        frame = tk.Frame(parent, bg='#1e293b', relief='raised', bd=2)
        frame.pack(fill='x', pady=10)
        
        indicator = tk.Frame(frame, bg=tool['color'], width=8)
        indicator.pack(side='left', fill='y')
        
        content = tk.Frame(frame, bg='#1e293b')
        content.pack(side='left', fill='both', expand=True, padx=20, pady=15)
        
        tk.Label(content, text=tool['name'],
                font=('Helvetica', 14, 'bold'),
                bg='#1e293b', fg='white', anchor='w').pack(fill='x')
        
        tk.Label(content, text=tool['desc'],
                font=('Helvetica', 10),
                bg='#1e293b', fg='#94a3b8', anchor='w').pack(fill='x', pady=(5, 0))
        
        btn = tk.Button(frame, text="Launch ▶️",
                       command=lambda f=tool['file']: self.launch_tool(f),
                       bg=tool['color'], fg='white',
                       font=('Helvetica', 11, 'bold'),
                       relief='flat', padx=20, pady=10, cursor='hand2')
        btn.pack(side='right', padx=15)
    
    def launch_tool(self, filename):
        if not os.path.exists(filename):
            messagebox.showerror("File Not Found", f"Could not find {filename}")
            return
        try:
            subprocess.Popen([sys.executable, filename])
            messagebox.showinfo("Success", f"Launched {filename}!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch: {str(e)}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AIToolsLauncher()
    app.run()