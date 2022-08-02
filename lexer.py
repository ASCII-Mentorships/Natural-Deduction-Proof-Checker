from sly import Lexer

class proofChecker(Lexer):
    
    # Set of token names.   
    tokens = {EOS, COMMA, NUM, VAR, COMMENT, EOL, ROUND_OPEN, ROUND_CLOSE, CURLY_OPEN, CURLY_CLOSE, SQUARE_OPEN, SQUARE_CLOSE, NOT, OR, AND, THEN, IFF, SCOPE, RULE,BY,USING,CANCEL,ASSN,HYPO, LABEL}

    # String containing ignored characters between tokens
    ignore = ' \t'

    # Regular expression rules for tokens
    EOS = r';'
    COMMA = r','
    LABEL = r'^l\d+'
    NUM = r'[0-9]+'

    VAR = r'[a-zA-Z][a-zA-Z0-9_]*'
    
    COMMENT = r'//.*'
    EOL = r'\n'
    ROUND_OPEN = r'\('
    ROUND_CLOSE = r'\)'
    CURLY_OPEN = r'\{'
    CURLY_CLOSE = r'\}'
    SQUARE_OPEN = r'\['
    SQUARE_CLOSE = r'\]'
    RULE = r'(~E|~I|&E|&I|\|E|\|I|>E|>I|<>E|<>I)'
    NOT = r'(\~|\!)'
    OR = r'\|'
    AND = r'\&'
    THEN = r'\>'
    IFF = r'\<\>'
    SCOPE = r'-'
   
     # Base ID rule
    

    # Special cases
    VAR['by'] = BY
    VAR['using'] = USING
    VAR['cancel'] = CANCEL
    VAR['Assumption'] = ASSN
    VAR['Hypothesis'] = HYPO
    # VAR['[a-n]'] = LABEL
