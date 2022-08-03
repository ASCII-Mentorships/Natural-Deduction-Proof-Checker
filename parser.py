from sly import Parser
from lexer import proofChecker
import pickle, sys

class PCParser(Parser):

    cnt = 1
    
    tokens = proofChecker.tokens
    g_scp = 0
    t_scp = 0
   
    dict2 = {}
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
        # dict2[p.LABEL].append(p.stmt)       
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


    ################# reason_list #########

    @_('ASSN')
    def reason_list(self,p):
        return p.ASSN


    @_('HYPO')
    def reason_list(self,p):
        return  p.HYPO

    @_('BY RULE COMMA USING CURLY_OPEN expr_list CURLY_CLOSE')
    def reason_list(self,p):
        return [ p.RULE,p.expr_list]


    @_('BY RULE COMMA USING CURLY_OPEN expr_list CURLY_CLOSE COMMA CANCEL NUM')
    def reason_list(self,p):
        return [p.RULE,p.expr_list,p.NUM]

    ###############expr_list###############

    @_('expr_list COMMA NUM')
    def expr_list(self,p):
        return [p.expr_list, p.NUM]

    
    @_('NUM')
    def expr_list(self,p):
        return p.NUM
    ###################################################### LOGIC ############################################################################
    #dict2={}
    
    def stmt(self,p):       
        list=[]
        reason_list=p.reason
        if(len(reason_list) == 1 and reason_list[0] == "Hypothesis"):
            pass
        if(len(reason_list) == 1 and reason_list[0] == "Assumption"):
            #check if scope increased
            pass

        if(len(reason_list) == 2):
            if(reason_list[0] == "~E"):
                if(len(reason_list[1]) != 1):
                    print("Incorrect number of reasons")
                    raise Exception("reason error")
                reason_1 = dict2[reason_list[1]]
                if(reason_1[0] != 'NOT' or reason_1[1][0] != 'NOT'):
                    print("Wrong reason type")
                    raise Exception("")
                if(p.expr != reason_1[1][1]):
                    print("Wrong inference from reason")
                    raise Exception("")
 
 
            if(reason_list[0] == "&E"):
                if(len(reason_list[1]) != 1):
                    print("Incorrect number of reasons")
                    raise Exception("")
                reason_1 = dict2[reason_list[1]]
                if(reason_1[1] != 'AND'):
                    print("Wrong reason type")
                    raise Exception("")
                if((p.expr != (reason_1[0] and reason_1[2]))):
                    print("Wrong inference from reason")
                    raise Exception("")
 
            if(reason_list[0] == "&I"):
                if(len(reason_list[1]) != 2):
                    print("Incorrect number of reasons")
                    raise Exception("")
                if(p.expr[1] != 'AND'):
                    print("Wrong introduction symbol")
                    raise Exception("")

                reason_1 = dict2[reason_list[1][0]]
                reason_2 = dict2[reason_list[1][1]]
                if((reason_1 == p.expr[0]) and (reason_2 == p.expr[2]) ):
                    pass
                elif((reason_1 == p.expr[2]) and (reason_2 == p.expr[0])):
                    pass
                else:
                    print("Wrong inference from reason")
                    raise Exception("")

               
 
            if(reason_list[0] == "|E"):
                if(len(reason_list[1]) != 3):           #
                    print("Incorrect number of reasons")
                    raise Exception("")
                reason_1 = dict2[reason_list[1][0]]
                reason_2 = dict2[reason_list[1][1]]
                reason_3 = dict2[reason_list[1][2]]
                if(reason_1[1] != 'OR'):
                    print("Wrong reason type")
                    raise Exception("") 
                if(reason_2[1] != 'THEN'):
                    print("Wrong reason type")
                    raise Exception("") 
                if(reason_3[1] != 'THEN'):
                    print("Wrong reason type")
                    raise Exception("") 
                if(reason_2[0] == reason_1[0] and reason_3[0] == reason_1[2]):
                    pass
                elif(reason_2[0] == reason_1[2] and reason_3[0] == reason_1[0]):
                    pass
                else:
                    print("Wrong reason type")
                    raise Exception("")     
                if(p.expr != (reason_2[2]) or reason_2[2] != reason_3[2]):
                    print("Wrong inference from reason")
                    raise Exception("")
 

            if(reason_list[0] == "|I"):
                if(len(reason_list[1]) != 1):
                    print("Incorrect number of reasons")
                    raise Exception("")
                if(p.expr[1] != 'OR'):
                    print("Wrong introduction symbol")
                    raise Exception("")
    
                reason_1 = dict2[reason_list[1]]
                if((reason_1 != p.expr[0]) and (reason_1 != p.expr[2])):
                    print("Wrong inference from reason")
                    raise Exception("")
 

            if(reason_list[0] == ">E"):
                if(len(reason_list[1])!=2):
                    print("Incorrect number of reasons")
                    raise Exception("")
                
                reason_1 = dict2[reason_list[1][0]]
                reason_2 = dict2[reason_list[1][1]]
                if(reason_2[1] != 'THEN'):
                    print("Wrong reason type")
                    raise Exception("")
                if(reason_1[0] != reason_2[0]):
                    print("Wrong reason type")
                    raise Exception("")
                if(p.expr != reason_2[2]):
                    print("Wrong inference from reason")
                    raise Exception("")
 
 
            if(reason_list[0]=="<>E"):
                if(len(reason_list[1]) != 1):
                    print("Incorrect number of reasons")
                    raise Exception("")
                if(p.expr[1] != 'THEN'):
                    print("Wrong expression introduction symbol")
                    raise Exception("")
                reason_1 = dict2[reason_list[1][0]]
                if(reason_2[1] != 'IFF'):
                    print("Wrong reason type")
                    raise Exception("")
                if(p.expr[0] == reason_1[0] and p.expr[2] == reason_1[2]):
                    pass
                elif(p.expr[2] == reason_1[0] and p.expr[0] == reason_1[0]):
                    pass
                else:
                    print("Wrong inference from reason")
                    raise Exception("") 

                    
            if(reason_list[0]=="<>I"):
                if(len(reason_list[1]) != 2):
                    print("Incorrect number of reasons")
                    raise Exception("")
                if(p.expr[1] != 'THEN'):
                    print("Wrong introduction symbol")
                    raise Exception("")
                reason_1 = dict2[reason_list[1][0]]
                reason_2 = dict2[reason_list[1][1]]
                if(reason_1[1] != 'THEN'):
                    print("Wrong reason type")
                    raise Exception("")  
                if(reason_2[1] != 'THEN'):
                    print("Wrong reason type")
                    raise Exception("") 

                if(p.expr[0] == reason_1[0] and p.expr[2] == reason_1[2]):
                    pass
                elif(p.expr[2] == reason_1[0] and p.expr[0] == reason_1[2]):
                    pass
                else:
                    print("Wrong inference from reason")
                    raise Exception("")  
                if(p.expr[0] == reason_2[0] and p.expr[2] == reason_2[2]):
                    pass
                elif(p.expr[2] == reason_2[0] and p.expr[0] == reason_2[2]):
                    pass
                else:
                    print("Wrong inference from reason")
                    raise Exception("")  

                

            

        if(len(reason_list)==3):
            if(reason_list[0]==">I"):
                if(p.expr[1] != 'THEN'):
                    print("Wrong introduction symbol")
                    raise Exception("")
                if(len(reason_list[1])!=2):
                    print("Incorrect number of reasons")
                    raise Exception("")
                reason_1 = dict2[reason_list[1][0]]
                reason_2 = dict2[reason_list[1][1]]
                if(p.expr[0] != reason_1 or p.expr[2] != reason_2):
                    print("Wrong inference from reason")
                    raise Exception("")
        
                #reduce scope
                #remove prev scope labels from dict2



            if(reason_list[0]=="~I"):
                if(p.expr[0] != 'NOT'):
                    print("Wrong introduction symbol")
                    raise Exception("")
                if(len(reason_list[1])!=3):
                    print("Incorrect number of reasons")
                    raise Exception("")
                
                reason_1 = dict2[reason_list[1][0]]
                reason_2 = dict2[reason_list[1][1]] 
                reason_3 = dict2[reason_list[1][2]] 

                if(reason_3[0] != 'NOT'):
                    print("Wrong reason type")
                    raise Exception("")
                if(reason_2 != reason_3[1]):
                    print("Wrong reason type")
                    raise Exception("")

                if(p.expr[1] != reason_1):
                    print("Wrong inference from reason")
                    raise Exception("")
                    
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
