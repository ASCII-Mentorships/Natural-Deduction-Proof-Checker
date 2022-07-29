from sly import Parser
from lexer import proofChecker
import pickle, sys

class PCParser(Parser):

    cnt = 1
    
    tokens = proofChecker.tokens
    g_scp = 0
    t_scp = 0
    stmt_no = 1
    dict..

    @_('stmt_list stmt')
    def stmt_list(self,p):
        evaluated_stmt = p.stmt
        
        return p

    @_('stmt')
    def stmt_list(self, p):
        return p

    @_('SCOPE stmt')
    def stmt(self,p):
        t_scp += 1
        return p
    
    @_('expr SQUARE_OPEN reason SQUARE_CLOSE')
    def stmt(self,p):
        if abs(self.t_scp-self.g_scp)>1:
            print("\nMore than 1 scope changed in a single statement")
            raise Exception("Scope Error")
        
        resolved_expr = p.expr
        reason_list = p.reason
        ["p", ">", "q"]
        return []

        evltd = p.expr
        self.g_scp = self.t_scp
        self.t_scp = 0
        self.stmt_no += 1


    @_('EOL')
    def stmt(self,p):
        return p
	
    @_('COMMENT')
    def stmt(self,p):
        return p

    #########################

