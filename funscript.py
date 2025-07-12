import re
import sys
from keystone import Ks, KS_ARCH_X86, KS_MODE_32
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EBX

# === Lexer ===
TOKEN_SPECIFICATION = [
    ('DEF',      r'def\b'),
    ('THEN',     r'then\b'),
    ('END',      r'end\b'),
    ('RETURN',   r'return\b'),
    ('PRINT',    r'print\b'),
    ('UNSAFE',   r'unsafe\b'),
    ('ASM',      r'asm\b'),
    ('IREAD',    r'iread\b'),
    ('LET',      r'let\b'),
    ('ASSIGN',   r':='),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('MULTILINE_STRING', r'"""(?:.|\n)*?"""'),
    ('STRING',   r'"([^"\\]|\\.)*"'),
    ('IDENT',    r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('SKIP',     r'[ \t\r\n]+'),
    ('MISMATCH', r'.'),
]

Token = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPECIFICATION))

class Lexer:
    def __init__(self, code):
        self.code = code
        self.tokens = self.tokenize()
        self.pos = 0

    def tokenize(self):
        tokens = []
        for mo in Token.finditer(self.code):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                raise RuntimeError(f"Unexpected token: {value}")
            else:
                tokens.append((kind, value))
        return tokens

    def next(self):
        if self.pos < len(self.tokens):
            tok = self.tokens[self.pos]
            self.pos += 1
            return tok
        return ('EOF', '')

# === Parser ===
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current = self.lexer.next()

    def eat(self, kind):
        if self.current[0] == kind:
            self.current = self.lexer.next()
        else:
            raise RuntimeError(f"Expected {kind} but got {self.current}")

    def parse_program(self):
        functions = []
        while self.current[0] == 'DEF':
            functions.append(self.parse_function())
        return functions

    def parse_function(self):
        self.eat('DEF')
        name = self.current[1]
        self.eat('IDENT')

        # قبول کردن پرانتز باز و بسته حتی اگر پارامتر نداشته باشیم
        if self.current[0] == 'LPAREN':
            self.eat('LPAREN')
        # می‌توان اینجا پارامترها را هم پردازش کرد اما الان ساده می‌گیریم
        self.eat('RPAREN')

        self.eat('THEN')

        body = []
        while self.current[0] != 'END':
            stmt = self.parse_statement()
            body.append(stmt)
        self.eat('END')

        return ('function', name, body)


    def parse_statement(self):
        if self.current[0] == 'PRINT':
            self.eat('PRINT')
            if self.current[0] == 'STRING':
                val = self.current[1]
                self.eat('STRING')
                return ('print', val.strip('"'))
            elif self.current[0] == 'IDENT':
                varname = self.current[1]
                self.eat('IDENT')
                return ('print_var', varname)
            else:
                raise RuntimeError(f"Expected STRING or IDENT after print but got {self.current}")

        elif self.current[0] == 'IREAD':
            self.eat('IREAD')
            prompt = self.current[1]
            self.eat('STRING')
            return ('iread', prompt.strip('"'))

        elif self.current[0] == 'LET':
            self.eat('LET')
            varname = self.current[1]
            self.eat('IDENT')
            self.eat('ASSIGN')
            if self.current[0] == 'IDENT':
                val = self.current[1]
                self.eat('IDENT')
                return ('let_var', varname, ('var', val))
            elif self.current[0] == 'STRING':
                val = self.current[1]
                self.eat('STRING')
                return ('let_var', varname, ('str', val.strip('"')))
            else:
                raise RuntimeError(f"Expected IDENT or STRING after := but got {self.current}")

        elif self.current[0] == 'UNSAFE':
            return self.parse_asm_block()

        elif self.current[0] == 'RETURN':
            self.eat('RETURN')
            return ('return',)

        else:
            raise RuntimeError(f"Unknown statement {self.current}")

    def parse_asm_block(self):
        self.eat('UNSAFE')
        self.eat('ASM')
        asm_code = self.current[1]
        self.eat('MULTILINE_STRING')
        return ('asm', asm_code.strip('"""').strip())

# === Interpreter ===
class Interpreter:
    def __init__(self, functions):
        self.functions = {f[1]: f for f in functions}
        self.env = {}  # متغیرهای محیط اجرایی

    def run(self):
        if 'main' not in self.functions:
            raise RuntimeError("No main function defined.")
        self.execute_function('main')

    def execute_function(self, name):
        func = self.functions[name]
        for stmt in func[2]:
            result = self.execute_statement(stmt)
            if result == 'return':
                break

    def execute_statement(self, stmt):
        kind = stmt[0]
        if kind == 'print':
            print(stmt[1])
        elif kind == 'print_var':
            varname = stmt[1]
            val = self.env.get(varname, '')
            print(val)
        elif kind == 'iread':
            prompt = stmt[1]
            val = input(prompt)
            self.env['_'] = val
        elif kind == 'let_var':
            varname = stmt[1]
            vtype, value = stmt[2]
            if vtype == 'var':
                val = self.env.get(value, '')
            else:
                val = value
            self.env[varname] = val
        elif kind == 'asm':
            self.execute_asm_block(stmt[1])
        elif kind == 'return':
            return 'return'
        else:
            raise RuntimeError(f"Unknown statement type: {kind}")

    def execute_asm_block(self, asm_code):
        print("Running asm block:")
        try:
            asm_lines = asm_code.strip().split('\n')
            asm_bytes = b''
            ks = Ks(KS_ARCH_X86, KS_MODE_32)
            for line in asm_lines:
                line = line.strip()
                if line:
                    encoding, _ = ks.asm(line)
                    asm_bytes += bytes(encoding)

            ADDRESS = 0x1000000
            mu = Uc(UC_ARCH_X86, UC_MODE_32)
            mu.mem_map(ADDRESS, 2 * 1024 * 1024)
            mu.mem_write(ADDRESS, asm_bytes)
            mu.reg_write(UC_X86_REG_EAX, 0)
            mu.reg_write(UC_X86_REG_EBX, 0)
            mu.emu_start(ADDRESS, ADDRESS + len(asm_bytes))
            result = mu.reg_read(UC_X86_REG_EAX)
            print(f"EAX after execution = {result}")
        except Exception as e:
            print(f"ASM execution failed: {e}")

# === Entry Point ===
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python funscript.py <file>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        source = f.read()

    lexer = Lexer(source)
    parser = Parser(lexer)
    functions = parser.parse_program()
    interpreter = Interpreter(functions)
    interpreter.run()
