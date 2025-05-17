import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current = self.tokens[self.pos] if tokens else None

    def advance(self):
        self.pos += 1
        self.current = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def accept(self, code):
        if self.current and self.current['code'] == code:
            self.advance()
            return True
        return False

    def expect(self, code):
        if not self.accept(code):
            raise SyntaxError(f"Ожидалось {lexeme_table[code]['value']}, но найдено {self.current['value']}")

    def expect_class(self, class_name):
        if self.current and self.current['class'] == class_name:
            self.advance()
        else:
            raise SyntaxError(f"Ожидался {class_name}, найдено: {self.current['class']}")

    def parse_program(self):
        while self.current:
            self.parse_statement()

    def parse_statement(self):
        if self.current['code'] == 'W5':
            self.parse_function()
        elif self.current['code'] == 'W2':
            self.parse_if()
        elif self.current['code'] == 'W6':
            self.parse_return()
        elif self.current['code'] == 'W7':
            self.parse_for()
        elif self.current['code'] == 'W9':
            self.parse_while()
        elif self.current['code'] == 'R10':
            self.advance()
        elif self.current['class'] == 'IDENTIFIER':
            if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1]['code'] == "R5":
                self.parse_function_call()
            elif self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1]['code'] == "W1":
                self.parse_declaration()
            else:
                self.parse_expression()
        else:
            raise SyntaxError(f"Неизвестная конструкция: {self.current}")

    def parse_declaration(self):
        self.expect_class("IDENTIFIER")
        while self.current and self.current["code"] == "R7":
            self.advance()
            self.parse_expression()
            if self.current and self.current["code"] == "R8":
                self.advance()
        if self.accept("W1"):
            if self.current and self.current["code"] == "R7":
                self.parse_list()
            else:
                self.parse_expression()
        if self.current: self.expect("R1")  # ;

    def parse_function(self):
        self.expect("W5")
        self.expect_class("FUNCTION")
        self.expect("R5")
        if self.current['class'] == "IDENTIFIER":
            self.expect_class("IDENTIFIER")
            while self.accept("R2"):
                self.expect_class("IDENTIFIER")
        self.expect("R6")
        self.expect("R4")
        self.expect("R1")
        self.expect("R9")
        while self.current and self.current['code'] != "R10":
            self.parse_statement()
        if self.current: self.expect("R10")

    def parse_if(self):
        self.expect("W2")
        self.parse_expression()
        self.expect("R4")
        self.expect("R1")
        self.expect("R9")
        while self.current and self.current["code"] != "R10":
            self.parse_statement()
        if self.current: self.expect("R10")
        if self.current and self.current["code"] == "W4":
            self.expect("W4")
            self.expect("R4")
            self.expect("R1")
            self.expect("R9")
            while self.current and self.current["code"] != "R10":
                self.parse_statement()
            if self.current: self.expect("R10")

    def parse_return(self):
        self.expect("W6")
        self.parse_expression()
        self.expect("R1")
        if self.current: self.expect("R10")

    def parse_expression(self):
        node_started = False
        while self.current:
            if self.current["class"] in {"IDENTIFIER", "NUMBER", "REAL_NUMBER", "STRING", "FUNCTION"} or self.current["code"] in {"R5", "R7"}:
                if self.current["code"] == "R7":
                    self.parse_list()
                elif self.current["class"] == "FUNCTION":
                    self.parse_function_call()
                else:
                    self.parse_factor()
                    node_started = True
            elif self.current["class"] == "OPERATOR" and node_started:
                self.advance()
            else:
                break

    def parse_function_call(self):
        self.expect_class("FUNCTION")
        self.expect("R5")
        if self.current and self.current["code"] != "R6":
            self.parse_expression()
            while self.accept("R2"):
                self.parse_expression()
        self.expect("R6")

    def parse_factor(self):
        if self.current["class"] == "IDENTIFIER":
            self.advance()
            if self.current and self.current["code"] == "R5":
                self.expect("R5")
                if self.current and self.current["code"] != "R6":
                    self.parse_expression()
                    while self.accept("R2"):
                        self.parse_expression()
                self.expect("R6")
        elif self.current["class"] in {"NUMBER", "REAL_NUMBER", "STRING"}:
            self.advance()
        elif self.current[0] == "R5":
            self.advance()
            self.parse_expression()
            self.expect("R6")
        else:
            raise SyntaxError(f"Недопустимый термин: {self.current}")

    def parse_list(self):
        self.expect("R7")
        if self.current and self.current["code"] != "R8":
            self.parse_expression()
            while self.accept("R2"):
                self.parse_expression()
        self.expect("R8")

    def parse_for(self):
        self.expect("W7")
        self.expect_class("IDENTIFIER")
        self.expect("W8")
        if self.current["value"] == "range":
            self.expect_class("FUNCTION")
            self.expect("R5")
            if self.current and self.current["code"] != "R6":
                self.parse_expression()
                while self.accept("R2"):
                    self.parse_expression()
            self.expect("R6")  # )    
        elif self.current and self.current["code"] == "R7":
            self.parse_list()
        else:
            raise SyntaxError("Неверная конструкция for: отсутствует список или range")
        self.expect("R4")
        self.expect("R1")
        self.expect("R9")
        while self.current and self.current["code"] != "R10":
            self.parse_statement()
        if self.current: self.expect("R10")

    def parse_while(self):
        self.expect("W9")
        self.parse_expression()
        self.expect("R4")
        self.expect("R1")
        self.expect("R9")
        while self.current and self.current["code"] != "R10":
            self.parse_statement()
        if self.current: self.expect("R10")


def load_lexeme_table(filepath):
    lexeme_table = {}
    current_section = None
    class_mapping = {
        'IDENTIFIERS': 'IDENTIFIER',
        'FUNCTIONS': 'FUNCTION',
        'NUMBERS': 'NUMBER',
        'REAL_NUMBERS': 'REAL_NUMBER',
        'STRINGS': 'STRING',
        'OPERATORS': 'OPERATOR',
        'DIVIDERS': 'DIVIDER',
        'KEYWORDS': 'KEYWORD'
    }
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('===') and line.endswith('==='):
                section_name = line[4:-4].strip()
                current_section = section_name
            else:
                if current_section and line:
                    parts = line.split(': ')
                    if len(parts) == 2:
                        code, value = parts[0].strip(), parts[1].strip()
                        lex_class = class_mapping.get(current_section, 'UNKNOWN')
                        lexeme_table[code] = {'class': lex_class, 'value': value}
    lexeme_table['R9'] = {'class': 'DIVIDER', 'value': 'INDENT'}
    lexeme_table['R10'] = {'class': 'DIVIDER', 'value': 'DEINDENT'}
    lexeme_table['R1'] = {'class': 'DIVIDER', 'value': 'NEWLINE'}
    return lexeme_table

def parse_input_lines(input_lines, lexeme_table):
    tokens = []
    for line in input_lines:
        if not line.strip():
            continue
        codes = line.strip().split()
        for code in codes:
            if code not in lexeme_table:
                raise ValueError(f"Неизвестный код лексемы: {code}")
            token_info = lexeme_table[code]
            tokens.append({
                'code': code,
                'class': token_info['class'],
                'value': token_info['value']
            })
        tokens.append({'code': 'R1', 'class': 'DIVIDER', 'value': 'NEWLINE'})
    return tokens

def read_lexeme_lines(file_path):
    lexeme_lines = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:
                    lexeme_lines.append(line)
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    except Exception as e:
        raise Exception(f"Ошибка при чтении файла: {e}")
    
    return lexeme_lines

def load_lexeme_file():
    filepath = filedialog.askopenfilename(title="Выберите файл с таблицей лексем")
    if filepath:
        try:
            global lexeme_table
            lexeme_table = load_lexeme_table(filepath)
            messagebox.showinfo("Успех", "Таблица лексем успешно загружена")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")

def run_parser():
    input_text = input_area.get("1.0", tk.END).strip()
    if not input_text:
        messagebox.showwarning("Предупреждение", "Введите набор лексем для анализа")
        return
    
    if 'lexeme_table' not in globals():
        messagebox.showerror("Ошибка", "Сначала загрузите таблицу лексем")
        return
    
    try:
        input_lines = [line for line in input_text.split('\n') if line.strip()]
        tokens = parse_input_lines(input_lines, lexeme_table)
        parser = Parser(tokens)
        parser.parse_program()
        output_area.delete("1.0", tk.END)
        output_area.insert(tk.END, "Синтаксический анализ завершён. Ошибок не обнаружено.")
    except SyntaxError as e:
        output_area.delete("1.0", tk.END)
        output_area.insert(tk.END, f"Ошибка синтаксического анализа: {e}")
    except Exception as e:
        output_area.delete("1.0", tk.END)
        output_area.insert(tk.END, f"Ошибка: {e}")

root = tk.Tk()
root.title("Синтаксический анализатор")

input_label = tk.Label(root, text="Введите набор лексем:")
input_label.pack(pady=(5, 0))
input_area = scrolledtext.ScrolledText(root, width=80, height=15)
input_area.pack(padx=10, pady=5)

button_frame = tk.Frame(root)
button_frame.pack(pady=5)

load_btn = tk.Button(button_frame, text="Загрузить таблицу лексем", command=load_lexeme_file)
load_btn.pack(side=tk.LEFT, padx=5)

parse_btn = tk.Button(button_frame, text="Выполнить анализ", command=run_parser)
parse_btn.pack(side=tk.LEFT, padx=5)

output_label = tk.Label(root, text="Результат анализа:")
output_label.pack(pady=(5, 0))
output_area = scrolledtext.ScrolledText(root, width=80, height=15)
output_area.pack(padx=10, pady=(0, 10))

root.mainloop()