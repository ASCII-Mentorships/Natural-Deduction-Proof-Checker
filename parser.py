# from cProfile import VAR
# from platform import java_ver
from turtle import bye
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
    infer = []
    is_assn_bool = False
    is_cancel_bool = False
    is_assn = {}
    assign_l = {}

    thmList = {}
    hypo_list_dict = {}

    thmList["~E"] = [{"h1":["NOT", ["NOT", "p"]]},["p"]]
    thmList["~I"] = [{"h1":["p"], "h2":["q"], "h3":["NOT", "q"]},["NOT", "p"]]
    thmList["&E"] = [{"h1":["p","AND","q"]},["p"]]
    thmList["&I"] = [{"h1":["p"], "h2":["q"]},["p","AND","q"]]
    thmList["|E"] = [{"h1":["p","OR","q"], "h2":["p","THEN","r"], "h3":["q","THEN","r"]},["r"]]
    thmList["|I"] = [{"h1":["p"]},["p","OR","q"]]
    thmList[">E"] = [{"h1":["p","THEN","q"], "h2":["p"]},["q"]]
    thmList[">I"] = [{"h1":["p"], "h2":["q"]},["p","THEN","q"]]
    thmList["<>E"] = [{"h1":["p<>q"]},["p","THEN","q"]]
    thmList["<>I"] = [{"h1":["p>q"], "h2":["q>p"]},["p","IFF","q"]]

    

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

    @_('VAR stmt')
    def lab_stmt(self,p):
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

    @_('BY RULE COMMA USING CURLY_OPEN expr_list CURLY_CLOSE COMMA CANCEL VAR')
    def reason(self,p):
        return [p.RULE, p.expr_list, p.VAR]

    @_('BY VAR COMMA USING CURLY_OPEN expr_list CURLY_CLOSE COMMA WITH CURLY_OPEN assign_list CURLY_CLOSE')
    def reason(self,p):
        self.assign_l[p.VAR] = p.assign_list
        return [p.VAR, p.expr_list, p.assign_list]

    @_('assign_list COMMA assign')
    def assign_list(self,p):
        assign_dict = p.assign_list
        resolved_assign = p.assign
        assign_dict[resolved_assign[0]] = resolved_assign[1]
        return assign_dict
    
    @_('assign')
    def assign_list(self,p):
        return p.assign

    @_('VAR COLON expr')
    def assign(self,p):
        return [p.VAR, p.expr]

    ############### expr_list ###############

    @_('expr_list COMMA VAR')
    def expr_list(self,p):
        lab_list = p.expr_list
        lab_list.append(p.VAR)
        return lab_list

    @_('VAR')
    def expr_list(self,p):
        return [p.VAR]

    

    @_('thm PROOF EOL')
    def thm_list(self,p):
        return p

    @_('thm thm_list')
    def thm_list(self,p):
        theorem_list = p.thm_list
        theorem_list.append(p.thm)
        return theorem_list 

    @_('THM VAR COLON hypo_list INFERS expr EOL')
    def thm(self,p):
        self.thmList[p.VAR] = [p.hypo_list,p.expr]
        return [p.hypo_list, p.infr]


    @_('hypo_list COMMA hypo')
    def hypo_list(self,p):
        hypo_dict = p.hypo_list
        resolved_hypo = p.hypo
        hypo_dict[resolved_hypo[0]] = resolved_hypo[1]
        self.hypo_list_dict[resolved_hypo[1]] = True
        return hypo_dict


    @_('hypo')
    def hypo_list(self,p):
        return p.hypo

    @_('VAR COLON expr')
    def hypo(self,p):
        return [p.VAR, p.expr]
    
    @_('infr_list COMMA infr')
    def infr_list(self,p):
        return [p.infr_list]

    @_('infr')
    def infr_list(self,p):
        return p.infr

    @_('VAR COLON expr')
    def infr(self,p):
        return [p.VAR, p.expr]
    
    ################################ LOGIC ################################
    
    @_('expr SQUARE_OPEN reason SQUARE_CLOSE')
    def stmt(self,p):
        
        curr_expr = p.expr
        reason_list = p.reason


########################################################
        def assignment(cur_hypo, cur_assign, m):
            if(len(cur_hypo) == 1):        
                if(m.get(cur_hypo[0]) == None):
                    m[cur_hypo[0]] = cur_assign
                elif(m.get(cur_hypo[0]) != cur_assign):
                    return False
                return True

            if(len(cur_hypo) == 2):
                if(cur_hypo[0] != cur_assign[0]):
                    return False
                else:
                    return assignment(cur_hypo[1], cur_assign[1])

            if(len(cur_hypo) == 3):
                if(cur_hypo[1] != cur_assign[1]):
                    return False
                else:
                    return assignment(cur_hypo[0], cur_assign[0]) or assignment(cur_hypo[2], cur_assign[2])
        
            return False # due to different lengths

        def inference(cur_infer, cur_expr, m):
            if(len(cur_infer) == 1):        
                if(m.get(cur_infer[0]) == None or m.get(cur_infer[0]) != cur_expr):
                    return False
                return True

            if(len(cur_infer) == 2):
                if(cur_infer[0] != cur_expr[0]):
                    return False
                else:
                    return assignment(cur_infer[1], cur_expr[1])

            if(len(cur_infer) == 3):
                if(cur_infer[1] != cur_expr[1]):
                    return False
                else:
                    return assignment(cur_infer[0], cur_expr[0]) or assignment(cur_infer[2], cur_expr[2])

            return False

        def theoremChecks():
            cur_thm = reason_list[0]
            if(len(reason_list[1]) != len(self.thmList[cur_thm][0])):
                print("Incorrect number of reasons")
            
            if(len(reason_list[1]) != len(self.assign_l[cur_thm])):
                print("Incorrect number of Assignments")

            m={}
            
            for x in self.assign_l[cur_thm][0] : # for each theorem key
                if(self.thmList[cur_thm][0].get(x)==None): # thm[cur_thm][0] gives first element of list which is dict
                    raise Exception
                    print("Hypo does not exist")
                cur_hypo = self.thmList[cur_thm][0].get(x) # p>q
                cur_assign = self.assign_l[cur_thm].get(x) #(a<>b)>(c>d)

                if(assignment(cur_hypo, cur_assign, m) == False):
                    raise Exception
                    print("Wrong assignment")
                    return False

            cur_infer = self.thmList[cur_thm][1]   # q
            if(inference(cur_infer, curr_expr, m) == False): # curr_expr = c > d
                    raise Exception
                    print("Wrong inference")
            
            return True

        try:
        
            # IF LEN = 1
            if (reason_list[0] == "Assumption"):
                self.is_assn_bool = True

            if (reason_list[1] == "Hypothesis"):
                if self.hypo_list_dict[curr_expr] == None:
                    print("Not a valid hypothesis")
                    raise Exception

            ########################################################

            if(theoremChecks() == False):
                print("Wrong Theorem Usage")
                raise Exception
                

            return curr_expr

        except:
            raise Exception

if __name__ == '__main__':
    lexer = proofChecker()
    parser = PCParser()
    fname = "test2.txt"
    with open(fname, 'r') as fileh:
        lines = fileh.readlines()
        line_count = 1
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
