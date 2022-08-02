from sly import Parser
from lexer import proofChecker
import pickle, sys

class PCParser(Parser):

    cnt = 1
    
    tokens = proofChecker.tokens
    g_scp = 0
    t_scp = 0
   
    dict1 = {}
    @_('LABEL stmt')
    def lab_stmt(self,p):
        
     
        return [p.LABEL , p.stmt]

    @_('stmt_list stmt')
    def stmt_list(self,p):
        # print("1")        
        return [p.stmt_list,p.stmt]

   

    @_('stmt')
    def stmt_list(self,p):
        # print("2") 
        return p.stmt

   

    @_(' SCOPE stmt')
    def stmt(self,p):
        # print("3") 
        # dict1[p.LABEL].append(p.stmt)       
        return p.stmt

    @_('expr SQUARE_OPEN reason SQUARE_CLOSE') # When it sees reason it finds where is def reason and then only checks @_
    def stmt(self,p):
        # print("4")        
        return [p.expr, p.reason]
       

    @_('EOL')
    def stmt(self,p):
        self.cnt += 1
        return p

    @_('COMMENT')
    def stmt(self,p):
        return p


    #############expr###############

    @_('NOT expr')
    def expr(self,p):
        return['NOT' , p.expr]

    @_('expr OR expr')
    def expr(self,p):
        return[ p.expr0, 'OR' , p.expr1]
    
    @_('expr AND expr')
    def expr(self,p):
        return[ p.expr0, 'AND' , p.expr1]

    @_('expr THEN expr')
    def expr(self,p):
        return[ p.expr0, 'THEN' , p.expr1]
    
    @_('expr IFF expr')
    def expr(self,p):
        return[ p.expr0, 'IFF' , p.expr1]

    @_('VAR')
    def expr(self,p):
        # print("5")
        return  p.VAR
    
    @_('ROUND_OPEN expr ROUND_CLOSE')
    def expr(self,p):
        return p.expr 

    ####################################


    #################### Reason ##################

    @_('reason_list')
    def reason(self,p):
        # print("6")
        return p.reason_list

    # @_('SQUARE_OPEN reason_list SQUARE_CLOSE ')
    # def reason(self,p):
    #     return p.reason_list


    ################# reason_list #########

    @_('ASSN')
    def reason_list(self,p):
        return p.ASSN


    @_('HYPO')
    def reason_list(self,p):
        return  p.HYPO

    @_(' BY RULE COMMA USING CURLY_OPEN expr_list CURLY_CLOSE')
    def reason_list(self,p):
        return [ p.RULE,p.expr_list]


    @_('  BY RULE COMMA USING CURLY_OPEN expr_list CURLY_CLOSE COMMA CANCEL NUM')
    def reason_list(self,p):
        return [p.RULE,p.expr_list,p.NUM]

    ###############expr_list###############

    @_('expr_list COMMA NUM')
    def expr_list(self,p):
        return [p.expr_list, p.NUM]

    
    @_('NUM')
    def expr_list(self,p):
        return p.NUM

if __name__ == '__main__':
    lexer = proofChecker()
    parser = PCParser()
    env = {}
    while True:
        try:
            text = input('basic > ')
        except EOFError:
            break
        if text:
           
            for tok in lexer.tokenize(text):
                print(tok)
            tree = parser.parse(lexer.tokenize(text))
            print(tree)
