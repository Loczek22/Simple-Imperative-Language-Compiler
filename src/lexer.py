from sly import Lexer

class MajLexer(Lexer):
    # Define tokens
    tokens = {
        PROCEDURE, ENDWHILE, PROGRAM, ENDFOR, REPEAT, DOWNTO, WRITE, BEGIN, WHILE, ENDIF,
        UNTIL, THEN, READ, ELSE, FROM, END, FOR, DO, IS, IF, TO, T, PID, NUM, ASSIGN, NEQ,
        GEQ, LEQ, ADD, SUB, MUL, DIV, MOD, COMMA, SEMI, COLON, LPN, RPN, LBR, RBR, EQ, LT, GT
    }

    # Define regex patterns for tokens
    PID = r'[_a-zA-Z][_a-zA-Z0-9]*'  # Updated to include uppercase letters and numbers
    
    # Operators and symbols
    NEQ = r'!='
    GEQ = r'>='
    LEQ = r'<='
    ASSIGN = r':='
    ADD = r'\+'
    SUB = r'-'
    MUL = r'\*'
    DIV = r'/'
    MOD = r'%'
    COMMA = r','
    SEMI = r';'
    COLON = r':'
    LPN = r'\('
    RPN = r'\)'
    LBR = r'\['
    RBR = r'\]'
    EQ = r'='
    LT = r'<'
    GT = r'>'

    NUM = r'-?\d+'

    # Ignore whitespace and tabs
    ignore = ' \t\r'

    # Ignore comments (starting with #)
    @_(r'#.*')
    def ignore_comment(self, t):
        pass

    # Track line numbers
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    # Convert NUM tokens to integers
    @_(r'-?\d+')
    def NUM(self, t):
        t.value = int(t.value)
        return t

    # Map keywords to tokens
    PID['PROCEDURE'] = PROCEDURE
    PID['ENDWHILE'] = ENDWHILE
    PID['PROGRAM'] = PROGRAM
    PID['ENDFOR'] = ENDFOR
    PID['REPEAT'] = REPEAT
    PID['DOWNTO'] = DOWNTO
    PID['WRITE'] = WRITE
    PID['BEGIN'] = BEGIN
    PID['WHILE'] = WHILE
    PID['ENDIF'] = ENDIF
    PID['UNTIL'] = UNTIL
    PID['THEN'] = THEN
    PID['READ'] = READ
    PID['ELSE'] = ELSE
    PID['FROM'] = FROM
    PID['END'] = END
    PID['FOR'] = FOR
    PID['DO'] = DO
    PID['IS'] = IS
    PID['IF'] = IF
    PID['TO'] = TO
    PID['T'] = T

    # Error handling
    def error(self, t):
        raise Exception(f"\033[31mError in line: {self.lineno}\033[31m")
