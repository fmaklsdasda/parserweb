import tkinter as tk
from tkinter import filedialog, messagebox
from timeparser import ScheduleParser  

class ScheduleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер расписания(Создано Чуевым В.О)")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        self.load_button = tk.Button(root, text="Загрузите файл с расписанием", command=self.load_file)
        self.load_button.pack(pady=20)

        self.teachers_listbox = tk.Listbox(root, width=50, height=10)
        self.teachers_listbox.pack(pady=20, fill=tk.BOTH, expand=True)
        self.teachers_listbox.bind('<<ListboxSelect>>', self.show_teacher_info)

        self.info_text = tk.Text(root, width=60, height=10, state='disabled')
        self.info_text.pack(pady=20, fill=tk.BOTH, expand=True)

        self.parser = None
        self.teachers = {}

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите эксель файл",
            filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*"))
        )
        if file_path:
            try:
                self.parser = ScheduleParser(file_path)
                self.parser.parse_schedule()
                self.teachers = self.parser.get_teachers_schedule()
                self.populate_teachers_list()
            except Exception as e:
                messagebox.showerror("Ошибка", f"не удалось обработать: {e}")

    def populate_teachers_list(self):
        self.teachers_listbox.delete(0, tk.END)

        for teacher in self.teachers:
            self.teachers_listbox.insert(tk.END, teacher)

    def show_teacher_info(self, event):
        selection = self.teachers_listbox.curselection()
        if selection:
            teacher_name = self.teachers_listbox.get(selection[0])

          
            self.info_text.config(state='normal')
            self.info_text.delete(1.0, tk.END)

            schedule = self.teachers[teacher_name]
            entries = []
            for entry in schedule:
                dt = entry['dt'].strftime('%d.%m.%Y')
                num = entry['lesson_num']
                mem_str = dt + str(num)
                if mem_str in entries:
                    self.info_text.insert(tk.END, f"ДУБЛИКАТ!!!\n", fill='FAFD0A')
                else:
                    entries.append(mem_str)
                self.info_text.insert(tk.END, f"Дата: {dt}\n")
                self.info_text.insert(tk.END, f"Номер пары: {num}\n")
                self.info_text.insert(tk.END, f"Предмет: {entry['subj']}\n")
                self.info_text.insert(tk.END, "-"*40 + "\n")

            self.info_text.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = ScheduleApp(root)
    root.mainloop()
