from cProfile import label
from platform import java_ver
from sly import Parser
from lexer import proofChecker
import pickle, sys

class PCParser(Parser):

    # def parse(self, p):
    #     print(type(p))
    #     for tok in p:
    #         print(tok)
    
    tokens = proofChecker.tokens
    g_scp = 0
    t_scp = 0

    lab_expr = {}
    valid_expr = []
    hypo = {}
    is_assn_bool = False
    is_cancel_bool = False
    is_assn = {}

    @_('stmt_list lab_stmt')
    def stmt_list(self,p):
        stmts = p.stmt_list
        stmts.append(p.lab_stmt)
        return stmts

    @_('lab_stmt EOL')
    def stmt_list(self,p):
        return p

    @_('EOL')
    def lab_stmt(self,p):
        return p

    @_('COMMENT EOL')
    def lab_stmt(self,p):
        return p

    @_('LABEL stmt')
    def lab_stmt(self,p):
        self.lab_expr[p.LABEL] = p.stmt

        # print("enter label stmt, scope...", self.t_scp, self.g_scp)
        if self.is_assn_bool:
            if self.t_scp != self.g_scp+1:
                print("Scope of assumption should be one more than scope of prev. statement")
                raise Exception("Scope Error")
        elif self.is_cancel_bool:
            if self.t_scp != self.g_scp-1:
                print("Scope while cancelling assumption should be one less than scope of prev. statement")
                raise Exception("Scope Error")
        elif self.t_scp != self.g_scp:
            print("Scope of non-assumption-related statement should be same as scope of prev. statement")
            raise Exception("Scope Error")

        self.is_assn[p.LABEL] = self.is_assn_bool
        self.is_assn_bool = False
        self.is_cancel_bool = False
        self.valid_expr.append(p.LABEL)
        self.g_scp = self.t_scp
        self.t_scp = 0
        # print("exit label stmt, scope...", self.t_scp, self.g_scp)

    @_('SCOPE stmt')
    def stmt(self,p):
        self.t_scp += 1
        return p.stmt

    ############# expr ###############

    @_('NOT expr')
    def expr(self,p):
        return ['NOT' , p.expr]

    @_('expr OR expr')
    def expr(self,p):
        return [p.expr0, 'OR' , p.expr1]
    
    @_('expr AND expr')
    def expr(self,p):
        return [p.expr0, 'AND' , p.expr1]

    @_('expr THEN expr')
    def expr(self,p):
        return [p.expr0, 'THEN' , p.expr1]
    
    @_('expr IFF expr')
    def expr(self,p):
        return [p.expr0, 'IFF' , p.expr1]

    @_('VAR')
    def expr(self,p):
        return p.VAR
    
    @_('ROUND_OPEN expr ROUND_CLOSE')
    def expr(self,p):
        return p.expr 

    #################### reason ##################

    @_('ASSN')
    def reason(self,p):
        return [p.ASSN]

    @_('HYPO')
    def reason(self,p):
        return  [p.HYPO]

    @_('BY RULE COMMA USING CURLY_OPEN expr_list CURLY_CLOSE')
    def reason(self,p):
        return [p.RULE, p.expr_list]

    @_('BY RULE COMMA USING CURLY_OPEN expr_list CURLY_CLOSE COMMA CANCEL LABEL')
    def reason(self,p):
        return [p.RULE, p.expr_list, p.LABEL]

    ############### expr_list ###############

    @_('expr_list COMMA LABEL')
    def expr_list(self,p):
        lab_list = p.expr_list
        lab_list.append(p.LABEL)
        return lab_list

    @_('LABEL')
    def expr_list(self,p):
        return [p.LABEL]
    
    ################################ LOGIC ################################
    
    @_('expr SQUARE_OPEN reason SQUARE_CLOSE')
    def stmt(self,p):
        
        curr_expr = p.expr
        reason_list = p.reason
        
        # FUNCTION DEFINITIONS

        def notElimination(curr_expr,reason_i):
            return (curr_expr == reason_i)

        def andElimination(curr_expr,reason_i):
            return (curr_expr == reason_i)

        def andIntroduction(curr_expr,reason_1,reason_2):
            return ((reason_1 == curr_expr[0]) and (reason_2 == curr_expr[2]))
            
        def orElimination(curr_expr,reason_1,reason_2,reason_3):
            if not (reason_1[1] == 'OR' and reason_2[1] == 'THEN' and reason_3[1] == 'THEN') and \
                   (reason_2[0] == reason_1[0] and reason_3[0] == reason_1[2] and reason_2[2] == reason_3[2]):
                return 0
            return (1 + int(reason_3[2] == curr_expr))

        def orIntroduction(curr_expr,reason_1):
            return (reason_1 == curr_expr[0] or reason_1 != curr_expr[2])

        def thenElimination2(curr_expr,reason_1,reason_2):
            if not (len(reason_1) == 1 and len(reason_2) == 3 and \
                    reason_2[1] == 'THEN' and reason_1[0] == reason_2[0]):
                return 0
            return (1 + int(curr_expr == reason_2[2]))

        def iffElimination(curr_expr,reason_1):
            if not (reason_1[1] == 'IFF'):
                return 0
            return 1 + int(curr_expr[1] == 'THEN' and \
                        ((curr_expr[0] == reason_1[0] and curr_expr[2] == reason_1[2]) or \
                         (curr_expr[2] == reason_1[0] and curr_expr[0] == reason_1[2])))

        def iffIntroduction(curr_expr, reason_1, reason_2):
            if not (reason_1[1] == 'THEN' and reason_2[1] != 'THEN' and \
                    reason_1[0] == reason_2[2] and reason_1[2] == reason_2[0]):
                return 0
            return (1 + int(curr_expr[0] == reason_1[0] and curr_expr[2] == reason_1[2] and \
                    curr_expr[0] == reason_2[2] and curr_expr[2] == reason_2[0]))

        def thenIntroduction(curr_expr, reason_1, reason_2, assn_lab):
            return int(self.is_assn[assn_lab] and curr_expr[0] == reason_1 and curr_expr[2] == reason_2)
            
        def notIntroduction(curr_expr, reason_1, reason_2, reason_3, assn_lab):
            if not (self.is_assn[assn_lab] and len(reason_3) == 2 and reason_3[0] == 'NOT' and reason_2 == reason_3[1]):
                return 0
            return (1 + int(len(curr_expr) == 2 and curr_expr[0] == 'NOT' and reason_1 == curr_expr[1]))

        try:
        
            # IF LEN = 1
            if (len(reason_list) == 1):

                # if (reason_list[0] == "Hypothesis"):
                    # if curr_expr not in self.hypo:
                    #     print("Expression not a hypothesis")
                    #     raise Exception("Invalid Hypothesis")
            
                if (reason_list[0] == "Assumption"):
                    self.is_assn_bool = True

            #IF LEN=2
            if (len(reason_list) == 2):

                if (reason_list[0] == "~E"):

                    if (len(reason_list[1]) != 1):
                        print("Incorrect number of reasons")
                        raise Exception("reason error")

                    reason_1 = self.lab_expr[reason_list[1][0]]
                
                    if (reason_1[0] != 'NOT' or reason_1[1][0] != 'NOT'):
                        print("Wrong expr(s) used")
                        raise Exception("")
                    
                    if not notElimination(curr_expr,reason_1[1][1]):
                        print("Wrong inference from reason")
                        raise Exception("")
    
                if (reason_list[0] == "&E"):
                    
                    if (len(reason_list[1]) != 1):
                        print("Incorrect number of reasons")
                        raise Exception("")

                    reason_1 = self.lab_expr[reason_list[1][0]]

                    if (reason_1[1] != 'AND'):
                        print("Wrong expr(s) used")
                        raise Exception("")
                    
                    if not (andElimination(curr_expr,reason_1[0]) or andElimination(curr_expr,reason_1[2])):
                        print("Wrong inference from reason")
                        raise Exception("")
    
                if (reason_list[0] == "&I"):

                    if (len(reason_list[1]) != 2):
                        print("Incorrect number of reasons")
                        raise Exception("")

                    if (curr_expr[1] != 'AND'):
                        print("Wrong Introduction symbol")
                        raise Exception("")
                    
                    reason_1 = self.lab_expr[reason_list[1][0]]
                    reason_2 = self.lab_expr[reason_list[1][1]]

                    if not (andIntroduction(curr_expr,reason_1,reason_2) or andIntroduction(curr_expr,reason_2,reason_1)):
                        print("Wrong inference from reason")
                        raise Exception("")

                if (reason_list[0] == "|E"):

                    if (len(reason_list[1]) != 3):
                        print("Incorrect number of reasons")
                        raise Exception("")
                    
                    reason_1 = self.lab_expr[reason_list[1][0]]
                    reason_2 = self.lab_expr[reason_list[1][1]]
                    reason_3 = self.lab_expr[reason_list[1][2]]

                    ma = max(orElimination(curr_expr,reason_1,reason_2,reason_3),
                             orElimination(curr_expr,reason_1,reason_3,reason_2),
                             orElimination(curr_expr,reason_2,reason_1,reason_3),
                             orElimination(curr_expr,reason_2,reason_3,reason_1),
                             orElimination(curr_expr,reason_3,reason_2,reason_1),
                             orElimination(curr_expr,reason_3,reason_1,reason_2))

                    if ma == 0:
                        print("Wrong reason list")
                        raise Exception("")
                    elif ma == 1:
                        print(" Wrong inference from reason")
                        raise Exception("")

                if (reason_list[0] == "|I"):

                    if (len(reason_list[1]) != 1):
                        print("Incorrect number of reasons")
                        raise Exception("")

                    if (curr_expr[1] != 'OR'):
                        print("Wrong introduction symbol")
                        raise Exception("")
                    
                    reason_1 = self.lab_expr[reason_list[1][0]]
                    
                    if not (orIntroduction(curr_expr,reason_1)):
                        print(" Wrong inference from reason")
    
                if (reason_list[0] == ">E"):

                    if (len(reason_list[1]) != 2):
                        print("Incorrect number of reasons")
                        raise Exception("")
                    
                    reason_1 = self.lab_expr[reason_list[1][0]]
                    reason_2 = self.lab_expr[reason_list[1][1]]
                        
                    ma = max(thenElimination2(curr_expr,reason_1,reason_2),
                             thenElimination2(curr_expr,reason_2,reason_1))
                    
                    if ma == 0:
                        print("Wrong reason list")
                        raise Exception("")
                    elif ma == 1:
                        print("Wrong inference from reason")
                        raise Exception("")
    
                if (reason_list[0]=="<>E"):

                    if (len(reason_list[1]) != 1):
                        print("Incorrect number of reasons")
                        raise Exception("")

                    reason_1 = self.lab_expr[reason_list[1][0]]
                    
                    ma = (iffElimination(curr_expr,reason_1))

                    if ma == 0:
                        print("Wrong reason list")
                        raise Exception("")
                    elif ma == 1:
                        print(" Wrong inference from reason")
                        raise Exception("")
            
                if (reason_list[0]=="<>I"):

                    if (len(reason_list[1]) != 2):
                        print("Incorrect number of reasons")
                        raise Exception("")

                    if (curr_expr[1] != 'THEN'):
                        print("Wrong introduction symbol")
                        raise Exception("")

                    reason_1 = self.lab_expr[reason_list[1][0]]
                    reason_2 = self.lab_expr[reason_list[1][1]]

                    ma = max(iffIntroduction(curr_expr,reason_1,reason_2),
                             iffIntroduction(curr_expr,reason_2,reason_1))
                    
                    if ma == 0:
                        print("Wrong reason type")
                        raise Exception("")
                    elif ma == 1:
                        print("Wrong inference from reason")
                        raise Exception("")

            # IF LEN=3
            if (len(reason_list) == 3):

                if (reason_list[0]==">I"):
                    if (len(reason_list[1]) != 2):
                        print("Incorrect number of reasons")
                        raise Exception("")

                    if (curr_expr[1] != 'THEN'):
                        print("Wrong introduction symbol")
                        raise Exception("")
                    
                    reason_1 = self.lab_expr[reason_list[1][0]]
                    reason_2 = self.lab_expr[reason_list[1][1]]

                    ma = max(thenIntroduction(curr_expr,reason_1,reason_2,reason_list[1][0]),
                             thenIntroduction(curr_expr,reason_2,reason_1,reason_list[1][1]))
                    if ma == 0:
                        print("Wrong inference from reason")
                        raise Exception("")

                if (reason_list[0]=="~I"):

                    if (len(reason_list[1]) != 3):
                        print("Incorrect number of reasons")
                        raise Exception("")
                    
                    if (curr_expr[0] != 'NOT'):
                        print("Wrong introduction symbol")
                        raise Exception("")
                    
                    reason_1 = self.lab_expr[reason_list[1][0]]
                    reason_2 = self.lab_expr[reason_list[1][1]] 
                    reason_3 = self.lab_expr[reason_list[1][2]]

                    ma = max(notIntroduction(curr_expr,reason_1,reason_2,reason_3,reason_list[1][0]),
                             notIntroduction(curr_expr,reason_1,reason_3,reason_2,reason_list[1][0]),
                             notIntroduction(curr_expr,reason_2,reason_3,reason_1,reason_list[1][1]),
                             notIntroduction(curr_expr,reason_2,reason_1,reason_3,reason_list[1][1]),
                             notIntroduction(curr_expr,reason_3,reason_2,reason_1,reason_list[1][2]),
                             notIntroduction(curr_expr,reason_3,reason_1,reason_2,reason_list[1][2]))
                    if ma == 0:
                        print("Wrong reason type")
                        raise Exception("")
                    elif ma == 1:
                        print("Wrong inference from reason")
                        raise Exception("")

                while len(self.valid_expr) != 0 and not self.is_cancel_bool:
                    if self.is_assn[self.valid_expr[-1]]:
                        if self.valid_expr[-1] == reason_list[2]:
                            self.is_cancel_bool = True
                        else:
                            print("Only the most recent active assumption can be cancelled")
                            raise Exception("")
                    self.is_assn.pop(self.valid_expr[-1])
                    self.lab_expr.pop(self.valid_expr[-1])
                    self.valid_expr.pop()

            return curr_expr

        except KeyError:
            print("Invalid Label referenced")
            raise Exception("Invalid LABEL")

if __name__ == '__main__':
    lexer = proofChecker()
    parser = PCParser()
    fname = "sample.txt"
    with open(fname, 'r') as fileh:
        lines = fileh.readlines()
        line_count = 1;
        for line in lines:
            try:
                result = parser.parse(lexer.tokenize(line))
            except:
                print("[syntax error] in line #",line_count,":",line)
                break
            line_count+=1
        
        if parser.g_scp > 0 or (True in parser.is_assn.values()):
            print("Not all assumptions are cancelled")
        else:
            print("Success\n", parser.lab_expr[list(parser.is_assn.keys())[-1]])