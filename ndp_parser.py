import sys
from sly import Parser
from ndp_lexer import NDPLexer

class NDPParser(Parser):

    tokens = NDPLexer.tokens    # Tokens list from Lexer
    
    thm_list = {}               # Dictionary that maps thm_name/rule_name to theorem
    g_scp = 0                   # Global Scope - scope of the previous statement
    t_scp = 0                   # Temporary Scope - scope of the current statement

    to_prove = []               # The theorem to be proven
    lab_expr = {}               # Dictionary that maps label to the expression in each statement
    valid_expr = []             # List of labels of statements valid in the current scope
    is_assn = {}                # Dict that maps a label to a bool telling whether the it is an assumption stmt

    is_assn_bool = False        # Boolean value that tells whether the current statement is an assumption
    is_cancel_bool = False      # Bool value that tells if the last assumption is cancelled in the current stmt

    ############# start ###############

    @_('line')
    def stmt_list(self,p):
        """
            Starting point, calls the right type of line:
            1. Admit theorem
            2. Prove theorem
            3. Line in a proof 
            4. Qed
            5. Comment
            6. Blank line
        """
        return p.line

    ################################ types of lines ################################
    
    @_('ADMIT thm')
    def line(self,p):
        """
            admit thm to thm_list for future use as reason in proof
            map thm_name to theorem: [hypo_dict, inference_expr]
            eg.
                Admit |E: h1: (p|q), h2: (p>r), h3: (q>r) |- r
        """
        
        resolved_thm = p.thm
        self.thm_list[resolved_thm[0]] = resolved_thm[1:]
        return p
    
    @_('PROVE thm')
    def line(self,p):
        """
            Start of proof from next line / Ques to be proven
            eg.
                Prove T4: h1: (a<>b), h2: (a<>b)>(c>p) |- (c>p)
        """

        self.to_prove = p.thm
        return p
    
    @_('VAR stmt')
    def line(self,p):
        """
            Store expressino, make scope related validations, prepare for next stmt
            Statement (stmt) in proof: 'label scope expr reason'
            eg.
                5 -- ~(p>q) [by ~I, using {h1: 1, h2: 3, h3: 4}]
        """

        # map statement label to expression
        self.lab_expr[p.VAR] = p.stmt

        # make appropriate validations for vals of g_scp and t_scp as per the type of stmt
        if self.is_assn_bool:
            # if stmt is assumption type, scope must increase by 1
            if self.t_scp != self.g_scp+1:
                print("Scope of assumption should be one more than scope of prev. statement")
                raise Exception("Scope Error")
        elif self.is_cancel_bool:
            # if last assn is cancelled in the stmt, scope must decrease by 1
            if self.t_scp != self.g_scp-1:
                print("Scope while cancelling assumption should be one less than scope of prev. statement")
                raise Exception("Scope Error")
        elif self.t_scp != self.g_scp:
            # if neither an assumption nor a cancellation is made in the stmt, scope must remain the same
            print("Scope of non-assumption-related statement should be same as scope of prev. statement")
            raise Exception("Scope Error")

        # current stmt: marked assumption/non-assumption, added to valid_expr list
        self.is_assn[p.VAR] = self.is_assn_bool
        self.valid_expr.append(p.VAR)

        # resetting the attributes in preparation for next stmt
        self.is_assn_bool = False
        self.is_cancel_bool = False
        self.g_scp = self.t_scp
        self.t_scp = 0
    
    @_('QED EOL')
    def line(self,p):
        """
            Make validations as the proof concludes (ends)
            In case of errors/mistakes, raise the apt exceptions 
            Otherwise, admit theorem and reset for next proof
        """

        # make validations at the end of proof
        if (self.g_scp > 0 or (True in self.is_assn.values())):
            # proof wrong/incomplete if not all assumptions are cancelled
            print("Not all assumptions are cancelled")
            raise Exception
        if (self.lab_expr[self.valid_expr[-1]] != self.to_prove[2]):
            # proof incorrect if last stmt does not match expected inference in 'to_prove'
            print("Incorrect inference derived")
            raise Exception
        
        # admit proven theorem to thm_list
        self.thm_list[self.to_prove[0]] = self.to_prove[1:]
        print("Successfully derived and admitted theorem {}\n".format(self.to_prove[0]))
        
        # reset attributes for next proof
        self.to_prove = []
        self.lab_expr = {}
        self.valid_expr = []
        self.is_assn = {}
        
        return p

    @_('COMMENT EOL')
    def line(self,p):
        # No action if line is a comment
        return p
    
    @_('EOL')
    def line(self,p):
        # No action on a blank line
        return p

    ############# thm ###############

    @_('VAR COLON hypo_list INFERS expr EOL')
    def thm(self,p):
        """
            Theorem syntax: 'thm_name: hypo_list |- inference'
            eg.
                T4: h1: (a<>b), h2: (a<>b)>(c>p) |- (c>p)
        """
        return [p.VAR, p.hypo_list, p.expr]

    @_('RULE COLON hypo_list INFERS expr EOL')
    def thm(self,p):
        """
            Rule: Theorem with thm_name limited to:
            ['~E', '~I', '&E', '&I', '|E', '|I', '>E', '>I', '<>E', '<>I']
            eg.
                |E: h1: (p|q), h2: (p>r), h3: (q>r) |- r 
        """
        return [p.RULE, p.hypo_list, p.expr]
    
    @_('RULE COLON INFERS expr EOL')
    def thm(self,p):
        # Rule with no hypothesis
        return [p.RULE, {}, p.expr]

    @_('VAR COLON INFERS expr EOL')
    def thm(self,p):
        """
            Thm with no hypothesis
            eg.
                T1: |- (~~p) > p
        """
        return [p.VAR, {}, p.expr]
    
    @_('hypo_list COMMA VAR COLON expr')
    def hypo_list(self,p):
        """
            admits hypos to hypo_dict: map hypo_label to hypo_expr
            hypo_list: comma separated hypos
            eg.
                h1: (p|q), h2: (p>r), h3: (q>r)
        """
        hypo_dict = p.hypo_list
        hypo_dict[p.VAR] = p.expr
        return hypo_dict
    
    @_('VAR COLON expr')
    def hypo_list(self,p):
        """
            Terminal of hypo_list (a single hypo)
            Hypo syntax: 'hypo_name: hypo_expr'
            eg.
                h1: (p|q)
        """
        return {p.VAR: p.expr}
    
    ################################ decoding stmt ################################
    
    @_('SCOPE stmt')
    def stmt(self,p):
        """
            t_scp increased by 1 for each SCOPE (-) symbol in the statement
            eg.
                -- ~(p>q) [by ~I, using {h1: 1, h2: 3, h3: 4}], t_scp: 0->1 and calls:
                - ~(p>q) [by ~I, using {h1: 1, h2: 3, h3: 4}],  t_scp: 1->2 and calls:
                ~(p>q) [by ~I, using {h1: 1, h2: 3, h3: 4}]
        """
        self.t_scp += 1
        return p.stmt
    
    @_('expr SQUARE_OPEN reason SQUARE_CLOSE EOL')
    def stmt(self,p):
        """
            Validates if the expression in the current statement is correctly derived
            There are 3 types of reasons: Assumption, Hypothesis, Deduction
            eg.
            Assumption:   p > q [Assumption]
            Hypothesis:   p [Hypothesis x1]
            Deduction:    ~(p>q) [by ~I, using {h1: 1, h2: 3, h3: 4}]
        """

        curr_expr = p.expr
        reason_list = p.reason

        if (len(reason_list) == 1 and reason_list[0] == "Assumption"):
            # If 'reason' is 'Assumption'
            self.is_assn_bool = True

        elif (len(reason_list) == 2 and reason_list[0] == "Hypothesis"):
            # If 'reason' is 'Hypothesis'
            # Verify if hypothesis label is valid for the thm to be proven
            if (self.to_prove[1].get(reason_list[1]) == None):
                print("Not a valid hypothesis")
                raise Exception

        else:
            # If expression is deduced using a rule/theorem
            def match(hypo, rsn, assignment):
                """
                    This function is used to assign a sub-expression from reason statement
                    ... to the atomic variables from hypothesis of theorem used
                    
                    hypo:       hypothesis expr in theorem
                    rsn:        reason expr from a prev stmt in proof that is assigned to hypo
                    assignment: dictionary that maintains the mapping      
                """

                if (len(hypo) == 1):
                    # Terminal (atomic variable) reached in function
                    if (assignment.get(hypo[0]) == None):
                        assignment[hypo[0]] = rsn
                    return (assignment[hypo[0]] == rsn)

                if(len(hypo) != len(rsn)):  # different lengths
                    return False

                if (len(hypo) == 2):
                    # Expression type is ['NOT', expr]. eg. !p is being assigned !(a>b),
                    # then first we check if [0] in both are 'NOT', and then match [1] of both.
                    return ((hypo[0] == rsn[0]) and match(hypo[1], rsn[1], assignment))

                # else expression type is [expr1, OPERATOR, expr2]. eg. (p > q) is being assigned ((a&b) > (c|d)),
                # then first we check equivalance of [1] (the operator '>') in both, and then recursively match [0] and match [2] of both
                return ((hypo[1] == rsn[1]) and match(hypo[0], rsn[0], assignment) and match(hypo[2], rsn[2], assignment))
            
            thm_lab = reason_list[0]

            # Validations for sanity check
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
                rsn_expr = self.lab_expr.get(rsn_lab)                   # (a&b)
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
                # Cancel stmt corresponding to h1 in ~I and >I
                # Statement to be cancelled must be the "RECENT-MOST" "ASSUMPTION"
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
                    # no more valid expressions left in scope and no expr cancelled yet
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
        # eg.
        #     by T1, using {h1: 1, h2: 3, h3: 4}
        return [p.VAR, p.assign_list]

    @_('BY RULE COMMA USING CURLY_OPEN assign_list CURLY_CLOSE')
    def reason(self,p):
        # eg.
        #     by ~I, using {h1: 1, h2: 3, h3: 4}
        return [p.RULE, p.assign_list]
   
    @_('assign_list COMMA VAR COLON VAR')      # Assignment: "VAR COLON VAR"
    def assign_list(self,p):
        # eg.
        #     h1: 1, h2: 3, h3: 4
        assign_dict = p.assign_list
        assign_dict[p.VAR0] = p.VAR1
        return assign_dict
    
    @_('VAR COLON VAR')
    def assign_list(self,p):
        # eg.
        #     h3: 4
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
    lexer = NDPLexer()
    parser = NDPParser()
    fname = sys.argv[1]
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
