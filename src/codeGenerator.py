import sys


class CodeGenerator:
    def __init__(self):
        self.code = ["SET 1", "STORE 1", 'SUB 1', 'STORE 2']
        
        
        self.scopes = [{"variables":dict(), "arrays":dict(), "iterators":dict(), "procedures":list(), "initialized":list()}]
        self.next_free_address = 3



    
    def generate_all(self, ast):
        gen = "all"
        
        if ast[0] == 'program_all':
            _, procedures, main = ast
            
            self.procedures = procedures[1:]
            self.generate_main(main)
        self.code.append("HALT")
            
    
    def generate_commands(self, commands_arg):
        gen = "commands"
        _, *commands = commands_arg
        if commands:
            for command in commands:
                self.generate_command(command)
    
    def generate_proc_declarations(self, declarations_arg):
        gen = "procedure declarations"
        _, *declarations = declarations_arg
        if declarations:
            for declaration in declarations:
                match declaration[0]:
                    case "var":
                        var_name = declaration[1]
                        if var_name not in self.scopes[-1]["variables"].keys() and var_name not in self.scopes[-1]["arrays"].keys():
                            self.scopes[-1]["variables"][var_name] = self.next_free_address
                            self.next_free_address += 1
                        else:
                            self.error(f"Redeclaration of variable {var_name}")
                    case "array":
                        array_name, start, end = declaration[1:]
                        if start > end:
                            self.error("Cannot index array this way; start cant be higher than end")
                        if array_name not in self.scopes[-1]["arrays"].keys() and array_name not in self.scopes[-1]["variables"].keys():
                            self.scopes[-1]["arrays"][array_name] = [self.next_free_address, start, end]
                            self.next_free_address += end - start + 1
                        else:
                            self.error(f"Redeclaration of array {array_name}")
        
    
    
    
    def generate_main(self, main):
        gen = "main"
        _, declarations, commands = main
        
        if declarations:
            self.generate_main_declarations(declarations)
        self.generate_main_commands(commands)
        
        
    def generate_main_declarations(self, declarations_arg):
        gen = "main declarations"
        main_scope = {"variables": dict(), "arrays": dict(), "iterators":dict(), "procedures":[proc[1][1] for proc in self.procedures], "initialized":list()}
        _, *declarations = declarations_arg
        if declarations:
            for declaration in declarations:
                match declaration[0]:
                    case "var":
                        var_name = declaration[1]
                        if var_name not in main_scope["variables"].keys() and var_name not in main_scope["arrays"].keys():
                            main_scope["variables"][var_name] = self.next_free_address
                            self.next_free_address += 1
                        else:
                            self.error(f"Redeclaration of variable {var_name}")
                    case "array":
                        array_name, start, end = declaration[1:]
                        if start > end:
                            self.error("Cannot index array this way; start cant be higher than end")
                        if array_name not in main_scope["arrays"].keys() and array_name not in main_scope["variables"].keys():
                            main_scope["arrays"][array_name] = [self.next_free_address, start, end]
                            self.next_free_address += end - start + 1
                        else:
                            self.error(f"Redeclaration of array {array_name}")
        self.scopes.append(main_scope)
    
    def generate_main_commands(self, commands_arg):
        gen = "main commands"
        _, *commands = commands_arg
        if commands:
            for command in commands:
                self.generate_command(command)
    
    def generate_command(self, command):
        command_type, *rest = command
        gen = "command"
        match command_type:
            case "assign":
                self.generate_assign(*rest)
            case "if_else":
                self.generate_if_else(*rest)
            case "if":
                self.generate_if(*rest)
            case "while":
                self.generate_while(*rest)
            case "repeat":
                self.generate_repeat(*rest)
            case "for_to":
                self.generate_for_to(*rest)
            case "for_downto":
                self.generate_for_down_to(*rest)
            case "proc_call":
                self.generate_proc_call(*rest)
            case "read":
                self.generate_read(*rest)
            case "write":
                self.generate_write(*rest)
    def generate_assign(self, identifier, expression):
        match identifier[0]:
            case "identifier":
                if identifier[1] not in self.scopes[-1]["variables"]:
                    self.error("Wrong usage of assign expression")
            case "array_access":
                if identifier[1] not in self.scopes[-1]["arrays"]:
                    self.error("Wrong usage of assign expression")
        if identifier[1] in self.scopes[-1]["iterators"].keys():
            self.error("Cannot assign value to iterator")
        where_to_store = 0
        res = self.handle_expression(expression)
        match identifier[0]:
            case 'identifier':
                var_name = identifier[1]
                if identifier[1] in self.scopes[-1]["variables"].keys():
                    self.scopes[-1]["initialized"].append(self.scopes[-1]["variables"][identifier[1]])
                if self.scopes[-1]["variables"][identifier[1]] in self.scopes[-2]["variables"].values():
                    self.scopes[-2]["initialized"].append(self.scopes[-1]["variables"][identifier[1]])
                if self.handle_variable_access(var_name)  and var_name not in self.scopes[-1]["iterators"].keys():
                    where_to_store = self.scopes[-1]["variables"][identifier[1]]
                    res.append(f"STORE {where_to_store}")
                    
            case 'array_access':
                if identifier[1] not in self.scopes[-1]["arrays"].keys():
                    self.error(f"No array named {identifier[1]}")
                if identifier[2] in self.scopes[-1]["variables"] and self.scopes[-1]["variables"][identifier[2]] not in self.scopes[-1]["initialized"]:
                    self.error(f"Variable {identifier[2]} is not initialized")
                if identifier[2] in self.scopes[-1]["variables"].keys():
                    self.code.append(f"SET {self.scopes[-1]["arrays"][identifier[1]][0] - self.scopes[-1]["arrays"][identifier[1]][1]}")
                    self.code.append(f"ADD { self.scopes[-1]["variables"][identifier[2]]}")
                    self.code.append(f"STORE {self.next_free_address}")
                    where_to_store = self.next_free_address
                    res.append(f"STOREI {where_to_store}")
                else:    
                    array_name, index = identifier[1], identifier[2]
                    if self.handle_array_access(array_name, index):
                        where_to_store = self.get_memory_address_for_array(array_name, index)
                        res.append(f"STORE {where_to_store}")
        for i in res:
            self.code.append(i)
        
        
    def generate_if_else(self, condition, commands0, commands1):
        for i in self.handle_condition(condition):
            self.code.append(i)
        finish = len(self.code) - 1
        self.generate_commands(commands0)
        self.code.append("JUMP end")
        end = len(self.code)-1
        self.code[finish] = self.code[finish].replace("finish", str(len(self.code) - finish))
        self.generate_commands(commands1)
        self.code[end] = self.code[end].replace("end", str(len(self.code) - end))
        
    def generate_if(self, condition, commands):
        for i in self.handle_condition(condition):
            self.code.append(i)
        finish = len(self.code) - 1
        self.generate_commands(commands)
        self.code[finish] = self.code[finish].replace("finish", str(len(self.code) - finish))
        
    def generate_while(self, condition, commands):
        start = len(self.code)
        for i in self.handle_condition(condition):
            self.code.append(i)
        finish = len(self.code) - 1
        self.generate_commands(commands)
        self.code[finish] = self.code[finish].replace("finish", str(len(self.code) - finish + 1))
        self.code.append(f"JUMP {(len(self.code) - start) * -1}")
        
    def generate_repeat(self, commands, condition):
        start = len(self.code) + 1
        self.generate_commands(commands)
        for i in self.handle_condition(condition):
            self.code.append(i)
        finish = len(self.code) - 1
        
        self.code[finish] = self.code[finish].replace("finish", str((len(self.code) -start) * -1))
        
    def generate_for_to(self, iter, value0, value1, commands):
        if value0[0] == 'num':
            val0_num = self.get_value_num(value0)
        else:
            val0_address = self.get_value_address(value0)
        if value1[0] == 'num':
            val1_num = self.get_value_num(value1)
        else:
            val1_address = self.get_value_address(value1)
        if iter in self.scopes[-1]["variables"].keys():
            self.error(f"Redeclaration of variable {iter} as iterator")
        elif iter in self.scopes[-1]["arrays"].keys():
            self.error(f"Redeclaration of array {iter} as iterator")
        self.scopes[-1]["iterators"][iter] = [self.next_free_address]
        self.scopes[-1]["variables"][iter] = self.next_free_address
        self.scopes[-1]["initialized"].append(self.next_free_address)
        if value0[0] == 'num':
            self.code.append(f"SET {val0_num}")
            self.code.append(f"STORE {self.next_free_address}")
        else:
            self.code.append(f"LOAD {val0_address}")
            self.code.append(f"STORE {self.next_free_address}")
        self.next_free_address += 1
        
        if value1[0] == 'num':
            self.code.append(f"SET {val1_num}")
            self.code.append(f"STORE {self.next_free_address}")
        else:
            self.code.append(f"LOAD {val1_address}")
            self.code.append(f"STORE {self.next_free_address}")
        self.next_free_address += 1
        
        start = len(self.code)
        self.code.append(f"LOAD {self.scopes[-1]["iterators"][iter][0]}")
        self.code.append(f"SUB {self.scopes[-1]["iterators"][iter][0]+1}")
        self.code.append(f"JPOS finish")
        finish = len(self.code)
        self.generate_commands(commands)
        
        self.code.append(f"LOAD {self.scopes[-1]["iterators"][iter][0]}")
        self.code.append("ADD 1")
        self.code.append(f"STORE {self.scopes[-1]["iterators"][iter][0]}")
        self.code.append(f"JUMP {(len(self.code) - start - 1 ) * -1}")
        self.code[start+2] = self.code[start+2].replace("finish", str(len(self.code) - finish + 1))
        self.scopes[-1]["initialized"].remove(self.scopes[-1]["variables"][iter])
        self.scopes[-1]["iterators"].pop(iter)
        self.scopes[-1]["variables"].pop(iter)
        
        
    def generate_for_down_to(self, iter, value0, value1, commands):
        if value0[0] == 'num':
            val0_num = self.get_value_num(value0)
        else:
            val0_address = self.get_value_address(value0)
        if value1[0] == 'num':
            val1_num = self.get_value_num(value1)
        else:
            val1_address = self.get_value_address(value1)
        if iter in self.scopes[-1]["variables"].keys():
            self.error(f"Redeclaration of variable {iter} as iterator")
        elif iter in self.scopes[-1]["arrays"].keys():
            self.error(f"Redeclaration of array {iter} as iterator")
        self.scopes[-1]["iterators"][iter] = [self.next_free_address]
        self.scopes[-1]["variables"][iter] = self.next_free_address
        self.scopes[-1]["initialized"].append(self.next_free_address)
        
        if value0[0] == 'num':
            self.code.append(f"SET {val0_num}")
            self.code.append(f"STORE {self.next_free_address}")
        else:
            self.code.append(f"LOAD {val0_address}")
            self.code.append(f"STORE {self.next_free_address}")
        self.next_free_address += 1
        
        if value1[0] == 'num':
            self.code.append(f"SET {val1_num}")
            self.code.append(f"STORE {self.next_free_address}")
        else:
            self.code.append(f"LOAD {val1_address}")
            self.code.append(f"STORE {self.next_free_address}")
        self.next_free_address += 1
        
        start = len(self.code)
        self.code.append(f"LOAD {self.scopes[-1]["iterators"][iter][0]}")
        self.code.append(f"SUB {self.scopes[-1]["iterators"][iter][0]+1}")
        self.code.append(f"JNEG finish")
        finish = len(self.code)
        self.generate_commands(commands)
        
        self.code.append(f"LOAD {self.scopes[-1]["iterators"][iter][0]}")
        self.code.append("SUB 1")
        self.code.append(f"STORE {self.scopes[-1]["iterators"][iter][0]}")
        self.code.append(f"JUMP {(len(self.code) - start - 1 ) * -1}")
        self.code[start+2] = self.code[start+2].replace("finish", str(len(self.code) - finish + 1))
        self.scopes[-1]["initialized"].remove(self.scopes[-1]["variables"][iter])
        self.scopes[-1]["iterators"].pop(iter)
        self.scopes[-1]["variables"].pop(iter)
    def generate_proc_call(self, proc_call):
        
        if proc_call[1] not in self.scopes[-1]["procedures"]:
            self.error(f"Procedure {proc_call[1]} doesnt exist in this scope")
            
        new_procedures = self.scopes[-1]["procedures"].copy()
        new_procedures.remove(proc_call[1])
        if not new_procedures:
            new_procedures = list()
        new_scope = {"variables":dict(), "arrays":dict(), "iterators":dict(), "procedures":new_procedures, "initialized":list()}
        
        _, proc_name, args = proc_call
        
        for procedure in self.procedures:
            if procedure[1][1] == proc_name:
                if len(args) == len(procedure[1][2]):
                    args_decl = procedure[1][2]
                    for i in range(1, len(args)):
                        if len(args_decl[i]) > 2 and args[i] in self.scopes[-1]["arrays"].keys():
                            new_scope["arrays"][args_decl[i][2]] =  self.scopes[-1]["arrays"][args[i]]
                        elif len(args_decl[i]) == 2 and args[i] in self.scopes[-1]["variables"].keys():
                            
                            new_scope["variables"][args_decl[i][1]] =  self.scopes[-1]["variables"][args[i]]
                            if self.scopes[-1]["variables"][args[i]] in self.scopes[-1]["initialized"]:
                                new_scope["initialized"].append(self.scopes[-1]["variables"][args[i]])
                        elif len(args_decl[i]) == 2 and args[i] in self.scopes[-1]["iterators"].keys():
                            new_scope["iterators"][args_decl[i][1]] =  self.scopes[-1]["iterators"][args[i]]
                            new_scope["initialized"].append(self.scopes[-1]["iterators"][args[i]])
                        else:
                            self.error(f"Wrong type of arguments at procedure call {proc_name}{args[1:]}")
                else:
                    self.error(f"Wrong number of arguments for procedure call: {proc_name}{args[1:]}")
                self.scopes.append(new_scope)
                if procedure[2]:
                    self.generate_proc_declarations(procedure[2])
                self.generate_commands(procedure[3])
                self.scopes = self.scopes[:-1]
    def generate_read(self, var):
        var_type = var[0]
        if var_type == 'identifier':
            self.scopes[-1]["initialized"].append(self.scopes[-1]["variables"][var[1]])
            if self.handle_variable_access(var[1]) and var[1] not in self.scopes[-1]["iterators"].keys():
                self.code.append(f"GET {self.get_value_address(var)}")
        elif var_type == 'array_access':
            if self.handle_array_access(var[1], var[2]):
                self.code.append(f"GET {self.get_memory_address_for_array(var[1], var[2])}")
        
            
    def generate_write(self, var):
        if var[1] in self.scopes[-1]["variables"] and self.scopes[-1]["variables"][var[1]] not in self.scopes[-1]["initialized"]:
            self.error(f"Variable {var[1]} is not initialized")
        var_type = var[0]
        if var_type == 'num':
            self.code.append(f"SET {var[1]}")
            self.code.append(f"STORE {self.next_free_address}")
            self.code.append(f"PUT {self.next_free_address}")
        elif len(var) < 3:
            if var[1] in self.scopes[-1]["iterators"].keys():
                self.code.append(f"PUT {self.scopes[-1]["iterators"][var[1]][0]}")
            elif self.handle_variable_access(var[1]):
                self.code.append(f"PUT {self.get_value_address(var)}")
        else:
            if var[2] in self.scopes[-1]["variables"] and self.scopes[-1]["variables"][var[2]] not in self.scopes[-1]["initialized"]:
                self.error(f"Variable {var[2]} is not initialized")
            if self.handle_array_access(var[1], var[2]):
                if var[2] in self.scopes[-1]["variables"].keys():
                    self.code.append(f"SET {self.scopes[-1]["arrays"][var[1]][0] - self.scopes[-1]["arrays"][var[1]][1]}")
                    self.code.append(f"ADD { self.scopes[-1]["variables"][var[2]]}")
                    self.code.append(f"STORE {self.next_free_address}")
                    self.code.append(f"LOADI {self.next_free_address}")
                    self.code.append(f"STORE {self.next_free_address}")
                    where_to_store = self.next_free_address
                    self.code.append(f"PUT {where_to_store}")
                else:
                    self.code.append(f"PUT {self.get_memory_address_for_array(var[1], var[2])}")
        
        
    def handle_expression(self, expression):
        expression_type = expression[0]
        value1 = 0
        value0 = expression[1]
        if expression[0] != "expression":
            value1 = expression[2]
            
        if value0[0] == 'num':
            val0_num = self.get_value_num(value0)
        elif value0[1] in self.scopes[-1]["arrays"].keys() and value0[2] in self.scopes[-1]["variables"].keys():
            if value0[2] in self.scopes[-1]["variables"] and self.scopes[-1]["variables"][value0[2]] not in self.scopes[-1]["initialized"]:
                self.error(f"Variable {value0[2]} is not initialized")
            self.code.append(f"SET {self.scopes[-1]["arrays"][value0[1]][0] - self.scopes[-1]["arrays"][value0[1]][1]}")
            self.code.append(f"ADD { self.scopes[-1]["variables"][value0[2]]}")
            self.code.append(f"STORE {self.next_free_address}")
            self.code.append(f"LOADI {self.next_free_address}")
            self.code.append(f"STORE {self.next_free_address}")
            val0_address = self.next_free_address
            self.next_free_address += 1
        else:   
            val0_address = self.get_value_address(value0)
        if value1 != 0 and value1[0] == 'num':
            val1_num = self.get_value_num(value1)
        elif value1 != 0 and value1[1] in self.scopes[-1]["arrays"].keys() and value1[2] in self.scopes[-1]["variables"].keys():
            if value1[2] in self.scopes[-1]["variables"] and self.scopes[-1]["variables"][value1[2]] not in self.scopes[-1]["initialized"]:
                self.error(f"Variable {value1[2]} is not initialized")
            self.code.append(f"SET {self.scopes[-1]["arrays"][value1[1]][0] - self.scopes[-1]["arrays"][value1[1]][1]}")
            
            self.code.append(f"ADD { self.scopes[-1]["variables"][value1[2]]}")
            self.code.append(f"STORE {self.next_free_address}")
            self.code.append(f"LOADI {self.next_free_address}")
            self.code.append(f"STORE {self.next_free_address}")
            val1_address = self.next_free_address
            self.next_free_address += 1
            
        elif value1 != 0:
            val1_address = self.get_value_address(value1)
            
                    
        res = []
        match expression_type:
            case "expression":
                if value0[0] == 'num':
                    res.append(f"SET {val0_num}")
                else:
                    res.append(f"LOAD {val0_address}")
            case "add": 
                if value0[0] == 'num' and value1[0] == 'num':
                    res.append(f"SET {val0_num + val1_num}")
                elif value0[0] == 'num':
                    res.append(f"SET {val0_num}")
                    res.append(f"ADD {val1_address}")
                elif value1[0] == 'num':
                    res.append(f"SET {val1_num}")
                    res.append(f"ADD {val0_address}")
                else:
                    res.append(f"LOAD {val0_address}")
                    res.append(f"ADD {val1_address}")
            case "sub":
                if value0[0] == 'num' and value1[0] == 'num':
                    res.append(f"SET {val0_num - val1_num}")
                elif value0[0] == 'num':
                    res.append(f"SET {val0_num}")
                    res.append(f"ADD {val1_address}")
                elif value1[0] == 'num':
                    res.append(f"SET {val1_num * -1}")
                    res.append(f"ADD {val0_address}")
                else:
                    res.append(f"LOAD {val0_address}")
                    res.append(f"SUB {val1_address}")
            case "mul":
                A_mul = self.next_free_address
                B_mul = self.next_free_address + 1
                C_mul = self.next_free_address + 2
                Atmp_mul = self.next_free_address + 3
                Btmp_mul = self.next_free_address + 4
                self.next_free_address += 5
                if value0[0] == 'num':
                    res.append(f"SET {val0_num}")
                else:
                    res.append(f"LOAD {val0_address}")   
                res.append(f"STORE {A_mul}")
                
                if value1[0] == 'num':
                    res.append(f"SET {val1_num}")
                else:
                    res.append(f"LOAD {val1_address}")   
                res.append(f"STORE {B_mul}")
                to_res = f"""LOAD 2
STORE {C_mul}
LOAD {B_mul}
JPOS 9
SUB {B_mul}
SUB {B_mul}
STORE {B_mul}
LOAD {A_mul}
SUB {A_mul}
SUB {A_mul}
STORE {A_mul}
LOAD {B_mul}   
JZERO 18
STORE {Atmp_mul}
LOAD {B_mul}
HALF
STORE {B_mul}
LOAD {B_mul}
ADD {B_mul}
STORE {Btmp_mul}
LOAD {Atmp_mul}
SUB {Btmp_mul}
JZERO 4
LOAD {C_mul}
ADD {A_mul}
STORE {C_mul}
LOAD {A_mul}
ADD {A_mul}
STORE {A_mul}
JUMP -18
LOAD {C_mul}"""
                for i in to_res.split("\n"):
                    res.append(i)
            case "div":
                A = self.next_free_address
                B = self.next_free_address + 1
                RES = self.next_free_address + 2
                MOD = self.next_free_address + 3
                K = self.next_free_address + 4
                B_mult = self.next_free_address + 5
                SIGN = self.next_free_address + 6
                self.next_free_address += 7
                if value0[0] == 'num':
                    res.append(f"SET {val0_num}")
                else:
                    res.append(f"LOAD {val0_address}")   
                res.append(f"STORE {A}")
                
                if value1[0] == 'num':
                    res.append(f"SET {val1_num}")
                else:
                    res.append(f"LOAD {val1_address}")   
                res.append(f"STORE {B}")
                to_res = f"""LOAD 2
SUB 1
STORE {SIGN}
LOAD {A}
JNEG 4
LOAD {SIGN}
ADD 1
STORE {SIGN}
LOAD {B}
JZERO 70
JNEG 4
LOAD {SIGN}
ADD 1
STORE {SIGN}
LOAD {B}
JPOS 3
SUB {B}
SUB {B}
STORE{B_mult}
STORE{B}
LOAD 1
STORE {K}
LOAD 2
STORE {RES}
LOAD {A}
JPOS 3
SUB {A}
SUB {A}
STORE {MOD}
STORE {A}
LOAD {MOD}
SUB {B_mult}
JNEG 8
LOAD {B_mult}
ADD {B_mult}
STORE {B_mult}
LOAD {K}
ADD {K}
STORE {K}
JUMP -9
LOAD {K}
HALF
STORE {K}
LOAD {B_mult}
HALF
STORE {B_mult}
LOAD {MOD}
SUB {B}
JNEG 17
LOAD {MOD}
SUB {B_mult}
JNEG 7
LOAD {MOD}
SUB {B_mult}
STORE {MOD}
LOAD {RES}
ADD {K}
STORE {RES}
LOAD {K}
HALF
STORE {K}
LOAD {B_mult}
HALF
STORE {B_mult}
JUMP -18
LOAD {SIGN}
JPOS 13
JNEG 12
LOAD {MOD}
JZERO 6
LOAD {RES}
SUB {RES}
SUB {RES}
SUB 1
JUMP 8
LOAD {RES}
SUB {RES}
SUB {RES}
JUMP 4
LOAD {RES}
JUMP 2
LOAD 2"""
                for i in to_res.split("\n"):
                    res.append(i)
            case "mod":
                A = self.next_free_address
                B = self.next_free_address + 1
                RES = self.next_free_address + 2
                MOD = self.next_free_address + 3
                K = self.next_free_address + 4
                B_mult = self.next_free_address + 5
                SIGN = self.next_free_address + 6
                SAVED_B = self.next_free_address + 7
                SAVED_A = self.next_free_address + 8
                self.next_free_address += 9
                if value0[0] == 'num':
                    res.append(f"SET {val0_num}")
                else:
                    res.append(f"LOAD {val0_address}")   
                res.append(f"STORE {A}")
                
                if value1[0] == 'num':
                    res.append(f"SET {val1_num}")
                else:
                    res.append(f"LOAD {val1_address}")   
                res.append(f"STORE {B}")
                to_res = f"""LOAD 2
SUB 1
STORE {SIGN}
LOAD {A}
STORE {SAVED_A}
JNEG 4
LOAD {SIGN}
ADD 1
STORE {SIGN}
LOAD {B}
JZERO 71
JNEG 4
LOAD {SIGN}
ADD 1
STORE {SIGN}
LOAD {B}
STORE {SAVED_B}
JPOS 3
SUB {B}
SUB {B}
STORE{B_mult}
STORE{B}
LOAD 1
STORE {K}
LOAD 2
STORE {RES}
LOAD {A}
JPOS 3
SUB {A}
SUB {A}
STORE {MOD}
STORE {A}
LOAD {MOD}
SUB {B_mult}
JNEG 8
LOAD {B_mult}
ADD {B_mult}
STORE {B_mult}
LOAD {K}
ADD {K}
STORE {K}
JUMP -9
LOAD {K}
HALF
STORE {K}
LOAD {B_mult}
HALF
STORE {B_mult}
LOAD {MOD}
SUB {B}
JNEG 17
LOAD {MOD}
SUB {B_mult}
JNEG 7
LOAD {MOD}
SUB {B_mult}
STORE {MOD}
LOAD {RES}
ADD {K}
STORE {RES}
LOAD {K}
HALF
STORE {K}
LOAD {B_mult}
HALF
STORE {B_mult}
JUMP -18
LOAD {SIGN}
JPOS 13
JNEG 12
LOAD {MOD}
JZERO 6
LOAD {RES}
SUB {RES}
SUB {RES}
SUB 1
JUMP 8
LOAD {RES}
SUB {RES}
SUB {RES}
JUMP 4
LOAD {RES}
JUMP 2
LOAD 2
STORE {RES}
LOAD {SAVED_B}
STORE {B}
LOAD 2
STORE {K}
LOAD {B}
JPOS 9
SUB {B}
SUB {B}
STORE {B}
LOAD {RES}
SUB {RES}
SUB {RES}
STORE {RES}
LOAD {B}   
JZERO 18
STORE {MOD}
LOAD {B}
HALF
STORE {B}
LOAD {B}
ADD {B}
STORE {B_mult}
LOAD {MOD}
SUB {B_mult}
JZERO 4
LOAD {K}
ADD {RES}
STORE {K}
LOAD {RES}
ADD {RES}
STORE {RES}
JUMP -18
LOAD {K}
SUB {K}
SUB {K}
ADD {SAVED_A}"""
                for i in to_res.split("\n"):
                    res.append(i)
        return res
    def handle_condition(self, condition):
        condition_type = condition[0]
        value0 = condition[1]
        value1 = condition[2]
        
        if value0[0] == 'num':
            val0_num = self.get_value_num(value0)
        elif value0[1] in self.scopes[-1]["arrays"].keys() and value0[2] in self.scopes[-1]["variables"].keys():
            if value0[2] in self.scopes[-1]["variables"] and self.scopes[-1]["variables"][value0[2]] not in self.scopes[-1]["initialized"]:
                self.error(f"Variable {value0[2]} is not initialized")
            self.code.append(f"SET {self.scopes[-1]["arrays"][value0[1]][0] - self.scopes[-1]["arrays"][value0[1]][1]}")
            self.code.append(f"ADD { self.scopes[-1]["variables"][value0[2]]}")
            self.code.append(f"STORE {self.next_free_address}")
            self.code.append(f"LOADI {self.next_free_address}")
            self.code.append(f"STORE {self.next_free_address}")
            val0_address = self.next_free_address
            self.next_free_address += 1
        else:   
            val0_address = self.get_value_address(value0)
        if value1[0] == 'num':
            val1_num = self.get_value_num(value1)
        elif value1[1] in self.scopes[-1]["arrays"].keys() and value1[2] in self.scopes[-1]["variables"].keys():
            if value1[2] in self.scopes[-1]["variables"] and self.scopes[-1]["variables"][value1[2]] not in self.scopes[-1]["initialized"]:
                self.error(f"Variable {value1[2]} is not initialized")
            self.code.append(f"SET {self.scopes[-1]["arrays"][value1[1]][0] - self.scopes[-1]["arrays"][value1[1]][1]}")
            
            self.code.append(f"ADD { self.scopes[-1]["variables"][value1[2]]}")
            self.code.append(f"STORE {self.next_free_address}")
            self.code.append(f"LOADI {self.next_free_address}")
            self.code.append(f"STORE {self.next_free_address}")
            val1_address = self.next_free_address
            self.next_free_address += 1
        else:
            val1_address = self.get_value_address(value1)
                    
        res = []
        if value0[0] == 'num' and value1[0] == 'num':
            res.append(f"SET {val0_num - val1_num}")
        elif value0[0] == 'num':
            res.append(f"SET {val0_num}")
            res.append(f"SUB {val1_address}")
        elif value1[0] == 'num':
            res.append(f"SET {val1_num * -1}")
            res.append(f"ADD {val0_address}")
        else:
            res.append(f"LOAD {val0_address}")
            res.append(f"SUB {val1_address}")
            
        match condition_type:
            case "eq":
                res.append("JZERO 2")
                res.append("JUMP finish")
            case "neq":
                res.append("JNEG 3")
                res.append("JPOS 2")
                res.append("JUMP finish")
            case "gt":
                res.append("JPOS 2")
                res.append("JUMP finish")
            case "lt":
                res.append("JNEG 2")
                res.append("JUMP finish")
            case "geq":
                res.append("JPOS 3")
                res.append("JZERO 2")
                res.append("JUMP finish")
            case "leq":
                res.append("JNEG 3")
                res.append("JZERO 2")
                res.append("JUMP finish")
        return res
                
    def handle_variable_access(self, var_name):
        if var_name in self.scopes[-1]["variables"] and self.scopes[-1]["variables"][var_name] not in self.scopes[-1]["initialized"]:
            self.error(f"Variable {var_name} is not initialized")
        if var_name in self.scopes[-1]["variables"].keys():
            return True
        self.error(f"No variable named {var_name} in this scope")
    
    def handle_array_access(self, array_name, index):
        if type(index) != int:
            return True
        if array_name in self.scopes[-1]["arrays"].keys():
            if index >= self.scopes[-1]["arrays"][array_name][1] and index <= self.scopes[-1]["arrays"][array_name][2]:
                return True
            else:
                self.error(f"Index out of range for array {array_name}")
        self.error(f"No array named {array_name} in this scope")
    
    def get_memory_address_for_array(self, array_name, index):
        if index in self.scopes[-1]["variables"]:
            index = self.scopes[-1]["variables"][index]
        if index in self.scopes[-1]["variables"] and self.scopes[-1]["variables"][index] not in self.scopes[-1]["initialized"]:
                self.error(f"Variable {index} is not initialized")
        return self.scopes[-1]["arrays"][array_name][0] - self.scopes[-1]["arrays"][array_name][1] + index
    
    def get_value_num(self, value):
        return value[1]
    
    def get_value_address(self, value):
        if len(value) < 3:
            if self.handle_variable_access(value[1]):
                if value[1] in self.scopes[-1]["variables"] and self.scopes[-1]["variables"][value[1]] not in self.scopes[-1]["initialized"]:
                    self.error(f"Variable {value[1]} is not initialized")
                val_address = self.scopes[-1]["variables"][value[1]]
        else:
            if self.handle_array_access(value[1], value[2]):
                val_address = self.get_memory_address_for_array(value[1], value[2])
        return val_address
    
    def error(self, message):
        raise Exception(f"\033[91m{message}\033[0m")
