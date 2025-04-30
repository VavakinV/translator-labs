import tkinter as tk
from tkinter import scrolledtext

def convert_rpn_to_r(rpn_code):
    stack = []
    r_code = []
    tokens = rpn_code.split()
    i = 0

    while i < len(tokens):
        token = tokens[i]

        if token == '=':
            val = stack.pop()
            var = stack.pop()
            r_code.append(f"{var} <- {val}")
        elif token in ('+', '-', '*', '/', '%', '**', '==', '!=', '<', '>', '<=', '>='):
            b = stack.pop()
            a = stack.pop()
            if token == "%":
                token = "%%"
            stack.append(f"({a} {token} {b})")
        elif token.endswith('Ф'):
            if i + 1 < len(tokens) and tokens[i+1] == 'НП':
                n = int(token[:-1])
                args = [stack.pop() for _ in range(n-1)][::-1]
                func_name = stack.pop()
                i += 1
                
                body_tokens = []
                depth = 1
                i += 1
                while i < len(tokens) and depth > 0:
                    if tokens[i] == 'НП':
                        depth += 1
                    elif tokens[i] == 'КП':
                        depth -= 1
                        if depth == 0:
                            break
                    body_tokens.append(tokens[i])
                    i += 1
                
                return_stmt = []
                if 'return' in body_tokens:
                    return_idx = body_tokens.index('return')
                    return_body = convert_rpn_to_r(' '.join(body_tokens[return_idx+1:]))
                    return_stmt = [f"return({return_body[0]})"] if return_body else []

                return_stmt = return_stmt[0]

                if return_idx:
                    body_r = convert_rpn_to_r(' '.join(body_tokens[:return_idx]))
                else:
                    body_r = convert_rpn_to_r(' '.join(body_tokens))

                full_body = body_r + "\n" + return_stmt
                r_code.append(f"{func_name} <- function({', '.join(args)}) {{\n" + full_body + "\n}")
                
            else:
                n = int(token[:-1])
                elements = []
                for _ in range(n):
                    elements.append(stack.pop())
                func_name = elements[-1]
                args = elements[:-1][::-1]
                stack.append(f"{func_name}({', '.join(args)})")

        elif token == '[':
            out = 'list('
            curr_element = []
            i += 1
            while (i < len(tokens)) and (tokens[i] != ']'):
                if tokens[i] == ',':
                    out += convert_rpn_to_r(' '.join(curr_element)).strip()+', '
                    curr_element = []
                else:
                    curr_element.append(tokens[i])
                i += 1
            out += convert_rpn_to_r(' '.join(curr_element).strip())+')'
            stack.append(out)
        
        elif token.endswith('АЭМ'):
            n = int(token[:-3])
            elements = []
            for _ in range(n):
                elements.append(stack.pop())
            list_name = elements[-1]
            args = elements[:-1][::-1]
            
            def adjust_index(arg):
                if arg.isdigit():
                    return str(int(arg) + 1)
                else:
                    return f"({arg}) + 1"
            
            adjusted_args = [adjust_index(arg) for arg in args]
            stack.append(f"{list_name}[[{']][['.join(adjusted_args)}]]")

        elif token == 'УПЛ':
            label = stack.pop()
            condition = stack.pop()
            if_body = []
            has_else = False
            i += 1
            if_result = ''
            while tokens[i] != f"{label}:":
                if tokens[i] == 'БП':
                    else_label = if_body.pop()
                    has_else = True
                else:
                    if_body.append(tokens[i])
                i += 1
            if_result = f"if {condition}" + "{\n" + f"{convert_rpn_to_r(' '.join(if_body).strip())}" + "}"
            if has_else:
                i += 1
                else_body = []
                while tokens[i] != f"{else_label}:":
                    else_body.append(tokens[i])
                    i += 1
                if_result += f" else " + "{\n" + f"{convert_rpn_to_r(' '.join(else_body).strip())}" + "}"
            
            stack.append(if_result)

        elif token == 'КП' or token == '\n':
            i += 1
            continue

        else:
            stack.append(token)

        i += 1

    # print(stack)

    while stack:
        r_code.append(stack.pop(0))
        # r_code.append("\n")
    
    return '\n'.join(r_code)
    
def convert():
    rpn = text_input.get("1.0", tk.END)
    try:
        code = convert_rpn_to_r(rpn)
        text_output.delete("1.0", tk.END)
        text_output.insert(tk.END, code)
    except Exception as e:
        text_output.delete("1.0", tk.END)
        text_output.insert(tk.END, f"Ошибка: {str(e)}")

root = tk.Tk()
root.title("Конвертер ОПЗ в R")
root.geometry("800x600")
root.minsize(500, 300)

main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

tk.Label(main_frame, text="Введите ОПЗ:").pack(anchor=tk.W)
text_input = scrolledtext.ScrolledText(main_frame, height=10, wrap=tk.WORD)
text_input.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

tk.Button(
    main_frame, 
    text="Конвертировать", 
    command=convert
).pack(pady=5)

tk.Label(main_frame, text="R:").pack(anchor=tk.W)
text_output = scrolledtext.ScrolledText(main_frame, height=10, wrap=tk.WORD)
text_output.pack(fill=tk.BOTH, expand=True)

root.mainloop()