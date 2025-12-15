import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import datetime
import uuid

class Task:
    def __init__(self, title, description="", priority="Medium"):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.priority = priority
        self.created_at = datetime.datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        task = cls(data['title'], data['description'], data['priority'])
        task.id = data['id']
        task.created_at = data['created_at']
        return task

class TodoList:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("✅ To-Do List")
        self.root.geometry("900x800")
        self.root.configure(bg='#0f172a')
        
        self.tasks = {}
        self.data_file = "tasks.json"
        self.load_tasks()
        self.setup_gui()
    
    def setup_gui(self):
        header = tk.Frame(self.root, bg='#8b5cf6', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Label(header, text="✅ To-Do List", font=('Helvetica', 24, 'bold'),
                bg='#8b5cf6', fg='white').pack(pady=25)
        
        input_frame = tk.Frame(self.root, bg='#1e293b', relief='raised', bd=2)
        input_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(input_frame, text="Task Title:", font=('Helvetica', 11, 'bold'),
                bg='#1e293b', fg='white').pack(anchor='w', padx=20, pady=(20, 5))
        
        self.task_entry = tk.Entry(input_frame, font=('Helvetica', 10),
                                   relief='flat', bd=5, bg='#0f172a', fg='white',
                                   insertbackground='white')
        self.task_entry.pack(fill='x', padx=20, pady=(0, 10))
        self.task_entry.bind('<Return>', lambda e: self.add_task())
        
        tk.Label(input_frame, text="Description (Optional):", font=('Helvetica', 11, 'bold'),
                bg='#1e293b', fg='white').pack(anchor='w', padx=20, pady=(0, 5))
        
        self.desc_entry = tk.Text(input_frame, height=3, font=('Helvetica', 10),
                                 relief='flat', bd=5, bg='#0f172a', fg='white',
                                 insertbackground='white')
        self.desc_entry.pack(fill='x', padx=20, pady=(0, 10))
        
        control_frame = tk.Frame(input_frame, bg='#1e293b')
        control_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        tk.Label(control_frame, text="Priority:", font=('Helvetica', 11, 'bold'),
                bg='#1e293b', fg='white').pack(side='left')
        
        self.priority_var = tk.StringVar(value="Medium")
        priority_menu = ttk.Combobox(control_frame, textvariable=self.priority_var,
                                    values=["Low", "Medium", "High", "Critical"],
                                    state="readonly", width=10)
        priority_menu.pack(side='left', padx=(10, 20))
        
        tk.Button(control_frame, text="➕ Add Task", command=self.add_task,
                 bg='#10b981', fg='white', font=('Helvetica', 11, 'bold'),
                 relief='flat', padx=20, pady=8, cursor='hand2').pack(side='right')
        
        stats_frame = tk.Frame(self.root, bg='#1e293b', relief='raised', bd=2)
        stats_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        self.stats_label = tk.Label(stats_frame, text="📊 Total Tasks: 0",
                                   font=('Helvetica', 11, 'bold'),
                                   bg='#1e293b', fg='white', pady=10)
        self.stats_label.pack()
        
        list_frame = tk.Frame(self.root, bg='#1e293b', relief='raised', bd=2)
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        tk.Label(list_frame, text="Your Tasks",
                font=('Helvetica', 12, 'bold'),
                bg='#1e293b', fg='white').pack(anchor='w', padx=20, pady=(15, 10))
        
        canvas = tk.Canvas(list_frame, bg='#1e293b', highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg='#1e293b')
        
        self.scroll_frame.bind("<Configure>", 
                              lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=(0, 10))
        scrollbar.pack(side="right", fill="y", pady=(0, 10))
        
        footer = tk.Frame(self.root, bg='#0f172a')
        footer.pack(fill='x', side='bottom', pady=(0, 10))
        
        tk.Label(footer, text="💡 Press Enter to quickly add tasks | Tasks auto-save",
                font=('Helvetica', 9), bg='#0f172a', fg='#94a3b8').pack()
        
        self.refresh_tasks()
    
    def add_task(self):
        title = self.task_entry.get().strip()
        if not title:
            messagebox.showwarning("Error", "Please enter a task title!")
            return
        
        description = self.desc_entry.get("1.0", tk.END).strip()
        priority = self.priority_var.get()
        
        task = Task(title, description, priority)
        self.tasks[task.id] = task
        
        self.task_entry.delete(0, tk.END)
        self.desc_entry.delete("1.0", tk.END)
        self.priority_var.set("Medium")
        
        self.refresh_tasks()
        self.save_tasks()
        self.task_entry.focus()
    
    def refresh_tasks(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        sorted_tasks = sorted(self.tasks.values(), key=lambda t: priority_order[t.priority])
        
        if not sorted_tasks:
            tk.Label(self.scroll_frame, text="🎯 No tasks yet! Add your first task above.",
                    font=('Helvetica', 12), bg='#1e293b', fg='#94a3b8',
                    pady=50).pack()
        else:
            for task in sorted_tasks:
                self.create_task_widget(task)
        
        self.stats_label.config(text=f"📊 Total Tasks: {len(self.tasks)}")
    
    def create_task_widget(self, task):
        colors = {
            "Low": "#10b981",
            "Medium": "#3b82f6",
            "High": "#f59e0b",
            "Critical": "#ef4444"
        }
        
        frame = tk.Frame(self.scroll_frame, bg='#0f172a', relief='solid', bd=1, pady=10)
        frame.pack(fill='x', padx=10, pady=5)
        
        tk.Frame(frame, bg=colors[task.priority], width=5).pack(side='left', fill='y', padx=(0, 15))
        
        content = tk.Frame(frame, bg='#0f172a')
        content.pack(side='left', fill='both', expand=True)
        
        title_frame = tk.Frame(content, bg='#0f172a')
        title_frame.pack(fill='x', padx=10, pady=(5, 2))
        
        tk.Label(title_frame, text=f"📋 {task.title}", font=('Helvetica', 11, 'bold'),
                bg='#0f172a', fg='white', anchor='w').pack(side='left', fill='x', expand=True)
        
        try:
            created = datetime.datetime.fromisoformat(task.created_at)
            time_str = created.strftime("%b %d, %I:%M %p")
            tk.Label(title_frame, text=f"🕐 {time_str}", font=('Helvetica', 8),
                    bg='#0f172a', fg='#64748b').pack(side='right')
        except:
            pass
        
        if task.description:
            tk.Label(content, text=task.description, font=('Helvetica', 9),
                    bg='#0f172a', fg='#94a3b8', anchor='w', 
                    wraplength=500, justify='left').pack(fill='x', padx=10, pady=(0, 5))
        
        tk.Label(content, text=f"🎯 Priority: {task.priority}", font=('Helvetica', 9),
                bg='#0f172a', fg=colors[task.priority], anchor='w').pack(fill='x', padx=10, pady=(0, 5))
        
        btn_frame = tk.Frame(frame, bg='#0f172a')
        btn_frame.pack(side='right', padx=15)
        
        tk.Button(btn_frame, text="✅ Complete", command=lambda: self.complete_task(task.id),
                 bg='#10b981', fg='white', font=('Helvetica', 9, 'bold'),
                 relief='flat', padx=12, pady=5, cursor='hand2').pack(pady=(0, 5))
        
        tk.Button(btn_frame, text="🗑️ Delete", command=lambda: self.delete_task(task.id),
                 bg='#ef4444', fg='white', font=('Helvetica', 9, 'bold'),
                 relief='flat', padx=12, pady=5, cursor='hand2').pack()
    
    def complete_task(self, task_id):
        if task_id in self.tasks:
            task = self.tasks[task_id]
            result = messagebox.askyesno("Complete Task", 
                                        f"Mark '{task.title}' as completed?\n\nThis will remove the task.")
            if result:
                del self.tasks[task_id]
                self.refresh_tasks()
                self.save_tasks()
                messagebox.showinfo("Success", "Task completed! 🎉")
    
    def delete_task(self, task_id):
        if task_id in self.tasks:
            task = self.tasks[task_id]
            result = messagebox.askyesno("Delete Task", 
                                        f"Are you sure you want to delete '{task.title}'?")
            if result:
                del self.tasks[task_id]
                self.refresh_tasks()
                self.save_tasks()
    
    def save_tasks(self):
        try:
            data = {tid: task.to_dict() for tid, task in self.tasks.items()}
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Save error: {e}")
    
    def load_tasks(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = {tid: Task.from_dict(td) for tid, td in data.items()}
        except Exception as e:
            print(f"Load error: {e}")
            self.tasks = {}
    
    def run(self):
        def on_close():
            self.save_tasks()
            self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_close)
        self.root.mainloop()

if __name__ == "__main__":
    app = TodoList()
    app.run()