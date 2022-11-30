from sly import Parser
from lexer import proofChecker

class PCParser(Parser):

    # def parse(self, p):
    #     print(type(p))
    #     for tok in p:
    #         print(tok)
    
    tokens = proofChecker.tokens
    
    thm_list = {}
    g_scp = 0
    t_scp = 0

    to_prove = []
    lab_expr = {}
    valid_expr = []
    is_assn = {}

    is_assn_bool = False
    is_cancel_bool = False

    ############# start ###############

    @_('line')
    def stmt_list(self,p):
        p.line
        return p

    ################################ types of lines ################################
    
    @_('ADMIT thm')
    def line(self,p): # admit_thm
        resolved_thm = p.thm
        self.thm_list[resolved_thm[0]] = resolved_thm[1:]
        return p
    
    @_('PROVE thm')
    def line(self,p): # prove_thm
        resolved_thm = p.thm
        self.to_prove = resolved_thm
        return p
    
    @_('VAR stmt')
    def line(self,p):
        self.lab_expr[p.VAR] = p.stmt

        # print("enter VAR stmt, scope...", self.t_scp, self.g_scp)
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

        self.is_assn[p.VAR] = self.is_assn_bool
        self.is_assn_bool = False
        self.is_cancel_bool = False
        self.valid_expr.append(p.VAR)
        self.g_scp = self.t_scp
        self.t_scp = 0
        # print("exit VAR stmt, scope...", self.t_scp, self.g_scp)
    
    @_('QED EOL')
    def line(self,p): # proof_end
        if (self.g_scp > 0 or (True in parser.is_assn.values())):
            print("Not all assumptions are cancelled")
            raise Exception
        if (self.lab_expr[self.valid_expr[-1]] != self.to_prove[2]):
            print("Incorrect inference derived")
            raise Exception
        self.thm_list[self.to_prove[0]] = self.to_prove[1:]
        print("Successfully derived and admitted theorem {}\n".format(self.to_prove[0]))
        
        self.to_prove = []
        self.lab_expr = {}
        self.valid_expr = []
        self.is_assn = {}
        
        return p

    @_('COMMENT EOL')
    def line(self,p):
        return p
    
    @_('EOL')
    def line(self,p):
        return p

    ############# thm ###############

    @_('RULE COLON hypo_list INFERS expr EOL')
    def thm(self,p):
        return [p.RULE, p.hypo_list, p.expr]

    @_('VAR COLON hypo_list INFERS expr EOL')
    def thm(self,p):
        return [p.VAR, p.hypo_list, p.expr]

    @_('RULE COLON INFERS expr EOL')
    def thm(self,p):
        return [p.RULE, {}, p.expr]

    @_('VAR COLON INFERS expr EOL')
    def thm(self,p):
        return [p.VAR, {}, p.expr]
    
    @_('hypo_list COMMA VAR COLON expr')    # hypo: "VAR COLON expr"
    def hypo_list(self,p):
        hypo_dict = p.hypo_list
        hypo_dict[p.VAR] = p.expr
        return hypo_dict
    
    @_('VAR COLON expr')
    def hypo_list(self,p):
        return {p.VAR: p.expr}
    
    ################################ decoding stmt ################################
    
    @_('SCOPE stmt')
    def stmt(self,p):
        self.t_scp += 1
        return p.stmt
    
    @_('expr SQUARE_OPEN reason SQUARE_CLOSE EOL')
    def stmt(self,p):
        curr_expr = p.expr
        reason_list = p.reason

        if (len(reason_list) == 1 and reason_list[0] == "Assumption"):
            self.is_assn_bool = True

        elif (len(reason_list) == 2 and reason_list[0] == "Hypothesis"):
            if (self.to_prove[1].get(reason_list[1]) == None):
                print("Not a valid hypothesis")
                raise Exception

        else:            
            def match(hypo, rsn, assignment):
                if (len(hypo) == 1):
                    if (assignment.get(hypo[0]) == None):
                        assignment[hypo[0]] = rsn
                    return (assignment[hypo[0]] == rsn)

                if(len(hypo) != len(rsn)):  # different lengths
                    return False

                if (len(hypo) == 2):
                    return ((hypo[0] == rsn[0]) and match(hypo[1], rsn[1], assignment))

                return ((hypo[1] == rsn[1]) and match(hypo[0], rsn[0], assignment) and match(hypo[2], rsn[2], assignment))
            
            thm_lab = reason_list[0]
            if (self.thm_list.get(reason_list[0]) == None):
                print("Invalid theorem name")
                raise Exception
            if (len(reason_list[1]) != len(self.thm_list[thm_lab][0])):
                print("Incorrect number of reasons")
                raise Exception

            assignment = {}

            for hypo_lab in reason_list[1]:
                rsn_lab = reason_list[1][hypo_lab]
                hypo_expr = self.thm_list[thm_lab][0].get(hypo_lab)     # p
                rsn_expr = self.lab_expr.get(rsn_lab)                   # (a<>b)
                if (hypo_expr == None):
                    print("Invalid hypothesis label", hypo_lab, "for theorem", thm_lab)
                    raise Exception
                if (rsn_expr == None):
                    print("Invalid reason label", rsn_lab)
                    raise Exception
                if (match(hypo_expr, rsn_expr, assignment) == False):
                    print("Expression of", rsn_lab, "doesn't match with expression of", hypo_lab)
                    raise Exception
            
            inference = self.thm_list[thm_lab][1]
            if (match(inference, curr_expr, assignment) == False):
                print("Wrong conclusion from theorem")
                raise Exception
            
            if (thm_lab == "~I" or thm_lab == ">I"):
                while len(self.valid_expr) != 0 and not self.is_cancel_bool:
                    if self.is_assn[self.valid_expr[-1]]:
                        if self.valid_expr[-1] == reason_list[1]['h1']: # "h1" is hard-coded...
                            self.is_cancel_bool = True
                            print("Successfully cancelled: ", self.valid_expr[-1])
                        else:
                            print("Only the most recent active assumption can be cancelled")
                            raise Exception("")
                    self.is_assn.pop(self.valid_expr[-1])
                    self.lab_expr.pop(self.valid_expr[-1])
                    self.valid_expr.pop()

                if self.is_cancel_bool == False:
                    print("Invalid cancellation")
                    raise Exception("")

        return curr_expr
    
    #################### reason ##################

    @_('ASSN')
    def reason(self,p):
        return [p.ASSN]

    @_('HYPO VAR')
    def reason(self,p):
        return  [p.HYPO, p.VAR]

    @_('BY VAR COMMA USING CURLY_OPEN assign_list CURLY_CLOSE')
    def reason(self,p):
        return [p.VAR, p.assign_list]

    @_('BY RULE COMMA USING CURLY_OPEN assign_list CURLY_CLOSE')
    def reason(self,p):
        return [p.RULE, p.assign_list]
   
    @_('assign_list COMMA VAR COLON VAR')      # Assignment: "VAR COLON VAR"
    def assign_list(self,p):
        assign_dict = p.assign_list
        assign_dict[p.VAR0] = p.VAR1
        return assign_dict
    
    @_('VAR COLON VAR')
    def assign_list(self,p):
        return {p.VAR0: p.VAR1}

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
        return [p.VAR]
    
    @_('ROUND_OPEN expr ROUND_CLOSE')
    def expr(self,p):
        return p.expr 
    
    ############# error ###############
    
    def error(self, p):
        raise Exception("")
    
###################################################################
    

if __name__ == '__main__':
    lexer = proofChecker()
    parser = PCParser()
    fname = "sample.ndp"
    with open(fname, 'r') as fileh:
        lines = fileh.readlines()
        line_count = 1
        for line in lines:
            try:
                result = parser.parse(lexer.tokenize(line))
            except:
                print("[syntax error] in line #{0}: {1}".format(line_count,line))
                break
            line_count+=1
