import tkinter as tk
from tkinter import scrolledtext

priority = {
    '(': 0, '[': 0, 'АЭМ': 0, 'Ф': 0, 'if': 0,
    ',': 1, ')': 1, ']': 1, ':': 1, 'else': 1, 'INDENT': 1, 'DEINDENT': 1, 
    '=': 2,
    '!=': 4, '>': 4, '<': 4, '==': 4,
    '+': 5, '-': 5,
    '*': 6, '/': 6, '%': 6,
    '**': 7
}

def is_identifier(token):
    return not(token in priority.keys())

def tokenize(code):
    tokens = []
    i = 0
    indent_stack = [0]

    while i < len(code):
        if i == 0 or code[i-1] == '\n':
            current_indent = abs(len(code[i:]) - len(''.join(code[i:]).lstrip()))
            if current_indent > indent_stack[-1]:
                indent_stack.append(current_indent)
                i += current_indent
                tokens.append('INDENT')
            else:
                while current_indent < indent_stack[-1]:
                    tokens.append('DEINDENT')
                    indent_stack.pop()
                if current_indent != indent_stack[-1]:
                    raise IndentationError("Несогласованные отступы")

        ch = code[i]

        if ch.isspace():
            i += 1
            continue

        if i + 1 < len(code):
            two_char = code[i:i+2]
            if two_char in ['!=', '==', '**']:
                tokens.append(two_char)
                i += 2
                continue

        if ch in '()[]=+*/%<>,:':
            tokens.append(ch)
            i += 1
            continue

        current = ''
        while i < len(code) and not code[i].isspace() and code[i] not in '()[]=+*/%<>,:':
            if i + 1 < len(code) and code[i:i+2] in ['!=', '==', '**']:
                break
            current += code[i]
            i += 1
        if current:
            tokens.append(current)
    
    while len(indent_stack) > 1:
        tokens.append('DEINDENT')
        indent_stack.pop()
    
    return tokens

def to_rpn(code):
    tokens = tokenize(code)
    stack, output = [], []
    i = 0
    label_counter = 1
    if_stack = []
    else_labels = []

    while i < len(tokens):
        token = tokens[i]
        if is_identifier(token):
            if (i + 1 < len(tokens)) and (tokens[i+1] == '('):
                stack.append(('Ф', token, 1))
                stack.append('(')
                i += 1
            elif (i + 1 < len(tokens)) and (tokens[i+1] == '['):
                stack.append(('АЭМ', 2))
                stack.append('[')
                output.append(token)
                i += 1
            else:
                output.append(token)

        elif (token == '=') and (i + 1 < len(tokens)) and (tokens[i+1] == '['):
            i += 2
            init_values = []
            output.append('[')
            while (i < len(tokens)) and (tokens[i] != ']'):
                if tokens[i] != ',':
                    init_values.append(tokens[i])
                else:
                    output.append(to_rpn(init_values))
                    output.append(',')
                    init_values = []
                i += 1
            output.append(to_rpn(init_values) + ']')
            init_values = []
            output.append('=')
            i += 1


        elif (token == ',') and stack and (stack[-1] == '('):
            while stack and (stack[-1] != '('):
                curr_token = stack.pop()
                if isinstance(curr_token, tuple):
                    if curr_token[0] == 'Ф':
                        output.append(f"{curr_token[1]} {curr_token[2]}Ф")
                    elif curr_token[0] == 'АЭМ':
                        output.append(f"{curr_token[1]}АЭМ")
                    elif curr_token[0] == "if":
                        output.append(f"{curr_token[1]} УПЛ")
                else:
                    output.append(curr_token)
            for j in range(len(stack)):
                if isinstance(stack[j], tuple) and stack[j][0] == 'Ф':
                    name, count = stack[j][1], stack[j][2] + 1
                    stack[j] = ('Ф', name, count)
                    break
        
        elif (token == ']') and stack and (stack[-1] == '[') and (i + 1 < len(tokens)) and (tokens[i+1] == '['):
            i += 2
            for j in range(len(stack)-1, -1, -1):
                if isinstance(stack[j], tuple) and stack[j][0] == 'АЭМ':
                    count = stack[j][1] + 1
                    stack[j] = ('АЭМ', count)
                    break 

        elif token == ')':
            while stack and stack[-1] != '(':
                curr_token = stack.pop()
                if isinstance(curr_token, tuple):
                    if curr_token[0] == 'Ф':
                        output.append(f"{curr_token[1]} {curr_token[2]}Ф")
                    elif curr_token[0] == 'АЭМ':
                        output.append(f"{curr_token[1]}АЭМ")
                    elif curr_token[0] == "if":
                        output.append(f"{curr_token[1]} УПЛ")
                else:
                    output.append(curr_token)
            if stack:
                stack.pop()
                if stack and isinstance(stack[-1], tuple) and (stack[-1][0] == 'Ф'):
                    _, name, count = stack.pop()
                    output.append(f"{name} {count}Ф")

        elif token == ']':
            while stack and (stack[-1] != '['):
                output.append(stack.pop())
            if stack:
                stack.pop()
                if stack and isinstance(stack[1], tuple) and (stack[-1][0]) == 'АЭМ':
                    count = stack.pop()[1]
                    output.append(f"{count}АЭМ")
        
        elif token == 'if':
            current_label = f"М{label_counter}"
            label_counter += 1
            if_stack.append(current_label)
            stack.append(("if", current_label))

        elif token == 'else':
            if if_stack:
                else_label = f"М{label_counter}"
                label_counter += 1
                output.append(f"{if_stack[-1]} УПЛ")
                else_labels.append(else_label)
                output.append(else_label)
        
        elif token == 'INDENT':
            output.append('НП')
            stack.append(token)
        
        elif token == 'DEINDENT':
            while stack and stack[-1] != 'INDENT':
                top = stack.pop()
                if isinstance(top, tuple) and top[0] == 'if':
                    output.append(f"{top[1]} УПЛ")
                elif isinstance(top, str):
                    output.append(top)
            if stack:
                stack.pop()
            output.append('КП')
            if else_labels:
                output.append(else_labels.pop())

        elif token in priority:
            while (stack and not isinstance(stack[-1], tuple)) and not (stack[-1] in ['(', '[', 'INDENT']) and (priority.get(stack[-1], 0) >= priority[token]):
                output.append(stack.pop())
            stack.append(token)
        
        i += 1


    while stack:
        curr_token = stack.pop()
        if isinstance(curr_token, tuple):
            if curr_token[0] == 'Ф':
                output.append(f"{curr_token[1]} {curr_token[2]}Ф")
            elif curr_token[0] == 'АЭМ':
                output.append(f"{curr_token[1]}АЭМ")
            elif curr_token[0] == "if":
                output.append(f"{curr_token[1]} УПЛ")
        else:
            output.append(curr_token)
        
    return ' '.join(output)

def convert():
    code = text_input.get("1.0", tk.END).strip()
    lines = code.split('\n')
    filtered_lines = []
    for line in lines:
        if not line.strip().startswith('#') and line:
            filtered_lines.append(line)
    filtered_code = '\n'.join(filtered_lines)

    try:
        rpn = to_rpn(filtered_code)
        text_output.delete("1.0", tk.END)
        text_output.insert(tk.END, rpn)
    except Exception as e:
        text_output.delete("1.0", tk.END)
        text_output.insert(tk.END, f"Ошибка: {str(e)}")

root = tk.Tk()
root.title("Конвертер в ОПЗ")
root.geometry("800x600")
root.minsize(500, 300)

main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

tk.Label(main_frame, text="Введите код:").pack(anchor=tk.W)
text_input = scrolledtext.ScrolledText(main_frame, height=10, wrap=tk.WORD)
text_input.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

tk.Button(
    main_frame, 
    text="Конвертировать", 
    command=convert
).pack(pady=5)

tk.Label(main_frame, text="ОПЗ:").pack(anchor=tk.W)
text_output = scrolledtext.ScrolledText(main_frame, height=10, wrap=tk.WORD)
text_output.pack(fill=tk.BOTH, expand=True)

root.mainloop()
