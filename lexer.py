class Lexer:
    def __init__(self):
        self.reset_counters()
        
    def reset_counters(self):
        self.lexeme_table = {
            '+': 'O1', '-': 'O2', '*': 'O3', '/': 'O4', '**': 'O5',
            '<': 'O6', '>': 'O7', '==': 'O8', '!=': 'O9', '>=': 'O10', '<=': 'O11',
            ' ': 'R1', ',': 'R2', '.': 'R3', ':': 'R4', '(': 'R5', ')': 'R6', '[': 'R7', ']': 'R8', 'INDENT': 'R9', 'DEINDENT': 'R10',
            '=': 'W1', 'if': 'W2', 'elif': 'W3', 'else': 'W4', 'def': 'W5', 'return': 'W6',
            'for': 'W7', 'in': 'W8', 'while': 'W9', 'input': 'W10', 'print': 'W11',
            'int': 'W12', 'float': 'W13', 'str': 'W14', 'True': 'W15', 'False': 'W16', 'None': 'W17'
        }
        self.identifiers = {}
        self.functions = {}
        self.numbers = {}
        self.real_numbers = {}
        self.strings = {}
        self.id_count = 0
        self.func_count = 0
        self.num_count = 0
        self.real_count = 0
        self.str_count = 0
        self.indent_stack = [0]
        self.current_line_indent = 0

    def process_text(self, text):
        result = []
        for line in text.split('\n'):
            if not line.strip():
                continue
            translated_line = self.process_line(line)
            if translated_line:
                result.append(translated_line)
        return '\n'.join(result)

    def process_line(self, line):
        # Обработка отступов
        leading_spaces = len(line) - len(line.lstrip())
        self.current_line_indent = leading_spaces
        indent_diff = self.current_line_indent - self.indent_stack[-1]
        
        translated = []
        
        # Обработка изменения отступа
        if indent_diff > 0:
            translated.append('R9')
            self.indent_stack.append(self.current_line_indent)
        elif indent_diff < 0:
            while self.indent_stack and self.current_line_indent < self.indent_stack[-1]:
                translated.append('R10')
                self.indent_stack.pop()
            if self.current_line_indent != self.indent_stack[-1]:
                raise ValueError("Некорректные отступы")
        
        line = line.strip()
        if not line:
            return None
        
        state = 'default'
        buffer = ''
        i = 0
        
        while i < len(line):
            char = line[i]
            
            if state == 'default':
                if char.isspace():
                    i += 1
                    continue
                
                elif char == '#':
                    break  # Комментарий
                
                # Проверка двойных символов
                elif char == '=' and i + 1 < len(line) and line[i+1] == '=':
                    translated.append('O8')
                    i += 1
                elif char == '!' and i + 1 < len(line) and line[i+1] == '=':
                    translated.append('O9')
                    i += 1
                elif char == '>' and i + 1 < len(line) and line[i+1] == '=':
                    translated.append('O10')
                    i += 1
                elif char == '<' and i + 1 < len(line) and line[i+1] == '=':
                    translated.append('O11')
                    i += 1
                elif char == '*' and i + 1 < len(line) and line[i+1] == '*':
                    translated.append('O5')
                    i += 1
                
                elif char in self.lexeme_table:
                    translated.append(self.lexeme_table[char])
                
                elif char.isdigit():
                    state = 'number'
                    buffer += char
                
                elif char.isalpha() or char == '_':
                    state = 'identifier'
                    buffer += char
                
                elif char == "'" or char == '"':
                    state = 'string'
                    buffer += char
                
                else:
                    raise ValueError(f'Неизвестный символ: {char}')
            
            elif state == 'number':
                if char.isdigit():
                    buffer += char
                elif char == '.':
                    state = 'real_number'
                    buffer += char
                else:
                    if buffer not in self.numbers:
                        self.num_count += 1
                        self.numbers[buffer] = f'N{self.num_count}'
                    translated.append(self.numbers[buffer])
                    buffer = ''
                    state = 'default'
                    continue
            
            elif state == 'real_number':
                if char.isdigit():
                    buffer += char
                else:
                    if buffer not in self.real_numbers:
                        self.real_count += 1
                        self.real_numbers[buffer] = f'D{self.real_count}'
                    translated.append(self.real_numbers[buffer])
                    buffer = ''
                    state = 'default'
                    continue
            
            elif state == 'identifier':
                if char.isalnum() or char == '_':
                    buffer += char
                else:
                    if buffer in self.lexeme_table:
                        translated.append(self.lexeme_table[buffer])
                    else:
                        if i < len(line) and char == '(':
                            if buffer not in self.functions:
                                self.func_count += 1
                                self.functions[buffer] = f'F{self.func_count}'
                            translated.append(self.functions[buffer])
                        elif i < len(line) and char == '[':
                            if buffer not in self.identifiers:
                                self.id_count += 1
                                self.identifiers[buffer] = f'X{self.id_count}'
                            translated.append(self.identifiers[buffer])
                        else:
                            if buffer not in self.identifiers:
                                self.id_count += 1
                                self.identifiers[buffer] = f'I{self.id_count}'
                            translated.append(self.identifiers[buffer])
                    buffer = ''
                    state = 'default'
                    continue
            
            elif state == 'string':
                buffer += char
                if char == buffer[0] and len(buffer) > 1 and buffer[-2] != '\\':
                    if buffer not in self.strings:
                        self.str_count += 1
                        self.strings[buffer] = f'C{self.str_count}'
                    translated.append(self.strings[buffer])
                    buffer = ''
                    state = 'default'
            
            i += 1

        if state == 'number':
            if buffer not in self.numbers:
                self.num_count += 1
                self.numbers[buffer] = f'N{self.num_count}'
            translated.append(self.numbers[buffer])
        elif state == 'real_number':
            if buffer not in self.real_numbers:
                self.real_count += 1
                self.real_numbers[buffer] = f'D{self.real_count}'
            translated.append(self.real_numbers[buffer])
        elif state == 'identifier':
            if buffer in self.lexeme_table:
                translated.append(self.lexeme_table[buffer])
            else:
                if buffer not in self.identifiers:
                    self.id_count += 1
                    self.identifiers[buffer] = f'I{self.id_count}'
                translated.append(self.identifiers[buffer])
        elif state == 'string':
            raise ValueError("Незакрытая строковая константа")
        
        return ' '.join(translated)
    
    def get_full_lexeme_info(self, text):
        sequence = self.process_text(text)
    
        tables = {
            'identifiers': {v: k for k, v in self.identifiers.items()},
            'functions': {v: k for k, v in self.functions.items()},
            'numbers': {v: k for k, v in self.numbers.items()},
            'real_numbers': {v: k for k, v in self.real_numbers.items()},
            'strings': {v: k for k, v in self.strings.items()},
            'operators': {v: k for k, v in self.lexeme_table.items() if v.startswith("O")},
            'dividers': {v: k for k, v in self.lexeme_table.items() if v.startswith("R")},
            'keywords': {v: k for k, v in self.lexeme_table.items() if v.startswith("W")}
        }
        
        return {
            'sequence': sequence,
            'tables': tables
        }
    

