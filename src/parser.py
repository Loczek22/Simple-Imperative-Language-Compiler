import sys
from sly import Parser
from lexer import MajLexer

class MajParser(Parser):
    tokens = MajLexer.tokens

    def __init__(self):
        self.names = {}
    
    
    # Program rules
    @_('procedures main')
    def program_all(self, p):
        return ('program_all', p.procedures, p.main)

    # Procedure rules
    @_('procedures PROCEDURE proc_head IS declarations BEGIN commands END')
    def procedures(self, p):
        return ('procedures', *p.procedures[1:], ('procedure', p.proc_head, p.declarations, p.commands))

    @_('procedures PROCEDURE proc_head IS BEGIN commands END')
    def procedures(self, p):
        return ('procedures', *p.procedures[1:], ('procedure', p.proc_head, None, p.commands))

    @_('')
    def procedures(self, p):
        return ('procedures',)

    # Main program rules
    @_('PROGRAM IS declarations BEGIN commands END')
    def main(self, p):
        return ('main', p.declarations, p.commands)

    @_('PROGRAM IS BEGIN commands END')
    def main(self, p):
        return ('main', None, p.commands)

    # Command rules
    @_('commands command')
    def commands(self, p):
        if isinstance(p.commands, tuple) and p.commands[0] == 'commands':
            return ('commands', *p.commands[1:], p.command)
        else:
            return ('commands', *p.commands[1:], p.command)

    @_('command')
    def commands(self, p):
        return ('commands', p.command)

    @_('identifier ASSIGN expression SEMI')
    def command(self, p):
        return ('assign', p.identifier, p.expression)

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, p):
        return ('if_else', p.condition, p.commands0, p.commands1)

    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        return ('if', p.condition, p.commands)

    @_('WHILE condition DO commands ENDWHILE')
    def command(self, p):
        return ('while', p.condition, p.commands)

    @_('REPEAT commands UNTIL condition SEMI')
    def command(self, p):
        return ('repeat', p.commands, p.condition)

    @_('FOR PID FROM value TO value DO commands ENDFOR')
    def command(self, p):
        return ('for_to', p.PID, p.value0, p.value1, p.commands)

    @_('FOR PID FROM value DOWNTO value DO commands ENDFOR')
    def command(self, p):
        return ('for_downto', p.PID, p.value0, p.value1, p.commands)

    @_('proc_call SEMI')
    def command(self, p):
        return ('proc_call', p.proc_call)

    @_('READ identifier SEMI')
    def command(self, p):
        return ('read', p.identifier)

    @_('WRITE value SEMI')
    def command(self, p):
        return ('write', p.value)

    # Procedure head rules
    @_('PID LPN args_decl RPN')
    def proc_head(self, p):
        return ('proc_head', p.PID, p.args_decl)

    # Procedure call rules
    @_('PID LPN args RPN')
    def proc_call(self, p):
        return ('proc_call', p.PID, p.args)

    # Declaration rules
    @_('declarations COMMA PID')
    def declarations(self, p):
        return ('declarations', *p.declarations[1:], ('var', p.PID))

    @_('declarations COMMA PID LBR NUM COLON NUM RBR')
    def declarations(self, p):
        return ('declarations', *p.declarations[1:], ('array', p.PID, p.NUM0, p.NUM1))

    @_('PID')
    def declarations(self, p):
        return ('declarations', ('var', p.PID))

    @_('PID LBR NUM COLON NUM RBR')
    def declarations(self, p):
        return ('declarations', ('array', p.PID, p.NUM0, p.NUM1))

    # Argument declaration rules
    @_('args_decl COMMA PID')
    def args_decl(self, p):
        return ('args_decl', *p.args_decl[1:], ('arg', p.PID))

    @_('args_decl COMMA T PID')
    def args_decl(self, p):
        return ('args_decl', *p.args_decl[1:], ('arg', 'T', p.PID))

    @_('PID')
    def args_decl(self, p):
        return ('args_decl', ('arg', p.PID))

    @_('T PID')
    def args_decl(self, p):
        return ('args_decl', ('arg', 'T', p.PID))

    # Argument rules
    @_('args COMMA PID')
    def args(self, p):
        return ('args', *p.args[1:], p.PID)

    @_('PID')
    def args(self, p):
        return ('args', p.PID)

    # Expression rules
    @_('value')
    def expression(self, p):
        return ('expression', p.value)

    @_('value ADD value')
    def expression(self, p):
        return ('add', p.value0, p.value1)

    @_('value SUB value')
    def expression(self, p):
        return ('sub', p.value0, p.value1)

    @_('value MUL value')
    def expression(self, p):
        return ('mul', p.value0, p.value1)

    @_('value DIV value')
    def expression(self, p):
        return ('div', p.value0, p.value1)

    @_('value MOD value')
    def expression(self, p):
        return ('mod', p.value0, p.value1)

    # Condition rules
    @_('value EQ value')
    def condition(self, p):
        return ('eq', p.value0, p.value1)

    @_('value NEQ value')
    def condition(self, p):
        return ('neq', p.value0, p.value1)

    @_('value GT value')
    def condition(self, p):
        return ('gt', p.value0, p.value1)

    @_('value LT value')
    def condition(self, p):
        return ('lt', p.value0, p.value1)

    @_('value GEQ value')
    def condition(self, p):
        return ('geq', p.value0, p.value1)

    @_('value LEQ value')
    def condition(self, p):
        return ('leq', p.value0, p.value1)

    # Value rules
    @_('NUM')
    def value(self, p):
        return ('num', p.NUM)

    @_('identifier')
    def value(self, p):
        return ('identifier', *p.identifier[1:])

    # Identifier rules
    @_('PID')
    def identifier(self, p):
        return ('identifier', p.PID)

    @_('PID LBR PID RBR')
    def identifier(self, p):
        return ('array_access', p.PID0, p.PID1)

    @_('PID LBR NUM RBR')
    def identifier(self, p):
        return ('array_access', p.PID, p.NUM)
    
    def error(self, token):
        if token:
            print(f"Błąd składni: Nieoczekiwany token '{token.value}' w linii {token.lineno}", file=sys.stderr)
        else:
            print(f"Błąd składni: Nieoczekiwany koniec wejścia", file=sys.stderr)
        sys.exit(1)