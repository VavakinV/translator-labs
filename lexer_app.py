import tkinter as tk
from tkinter import filedialog, messagebox
from lexer import Lexer

class LexerApp:
    def __init__(self, root):
        self.lexer = Lexer()
        self.root = root
        self.root.title('Лексический анализатор Python')

        self.input_text = tk.Text(root, height=40, width=50)
        self.input_text.grid(row=0, column=0, padx=10, pady=10)

        self.output_text = tk.Text(root, height=40, width=50, state='disabled')
        self.output_text.grid(row=0, column=1, padx=10, pady=10)

        self.button_frame = tk.Frame(root)
        self.button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        self.load_button = tk.Button(self.button_frame, text='Загрузить файл', command=self.load_file)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.translate_button = tk.Button(self.button_frame, text='Транслировать', command=self.translate)
        self.translate_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(self.button_frame, text='Сохранить результаты', command=self.save_results)
        self.save_button.pack(side=tk.LEFT, padx=5)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[('Python Files', '*.py')])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.input_text.delete('1.0', tk.END)
                self.input_text.insert('1.0', content)

    def translate(self):
        self.lexer.reset_counters()
        
        input_code = self.input_text.get('1.0', tk.END).strip()
        if not input_code:
            messagebox.showwarning('Ошибка', 'Отсутствуют входные данные')
            return

        try:
            translated_code = self.lexer.process_text(input_code)
            self.output_text.config(state='normal')
            self.output_text.delete('1.0', tk.END)
            self.output_text.insert('1.0', translated_code)
            self.output_text.config(state='disabled')
        except ValueError as e:
            messagebox.showerror('Ошибка', str(e))

    def save_results(self):
        input_code = self.input_text.get('1.0', tk.END).strip()
        if not input_code:
            messagebox.showwarning('Ошибка', 'Нет данных для сохранения')
            return

        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        try:
            lexeme_info = self.lexer.get_full_lexeme_info(input_code)

            with open(f'{folder_path}/lexeme_sequence.txt', 'w', encoding='utf-8') as f:
                f.write(lexeme_info['sequence'])

            with open(f'{folder_path}/lexeme_tables.txt', 'w', encoding='utf-8') as f:
                for table_name, table in lexeme_info['tables'].items():
                    f.write(f"=== {table_name.upper()} ===\n")
                    for code, value in sorted(table.items(), key=lambda x: int(x[0][1:])):
                        f.write(f"{code}: {value}\n")

            with open(f'{folder_path}/source_code.py', 'w', encoding='utf-8') as f:
                f.write(input_code)

            messagebox.showinfo('Успех', f'Результаты сохранены в папку:\n{folder_path}')
            
        except Exception as e:
            messagebox.showerror('Ошибка', f'Ошибка при сохранении: {str(e)}')