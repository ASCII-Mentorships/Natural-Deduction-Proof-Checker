from sly import Lexer

class proofChecker(Lexer):
    
    # Set of token names.   
    tokens = {COMMA, VAR, COMMENT, EOL, ROUND_OPEN, ROUND_CLOSE, CURLY_OPEN, CURLY_CLOSE, SQUARE_OPEN, SQUARE_CLOSE, NOT, OR, AND, THEN, IFF, SCOPE, RULE, BY, USING, ASSN, HYPO, QED, COLON, INFERS, PROVE, ADMIT}

    # String containing ignored characters between tokens
    ignore = ' \t'

    # Regular expression rules for tokens
    COMMA = r','
    # LABEL = r'[0-9]+'

    VAR = r'[a-zA-Z0-9_]+' #change
    
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
    INFERS = r'\|-'
    OR = r'\|'
    AND = r'\&'
    THEN = r'\>'
    IFF = r'\<\>'
    SCOPE = r'-'
    COLON = r':'
    # Base ID rule
    

    # Special cases
    VAR['by'] = BY
    VAR['using'] = USING
    VAR['Assumption'] = ASSN
    VAR['Hypothesis'] = HYPO
    VAR['Qed'] = QED
    VAR['Prove'] = PROVE
    VAR['Admit'] = ADMIT
    
