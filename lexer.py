from sly import Lexer

class proofChecker(Lexer):
    # Set of token names
    tokens = {EOS, COMMA, NUM, VAR, COMMENT, EOL, ROUND_OPEN, ROUND_CLOSE, CURLY_OPEN, CURLY_CLOSE, SQUARE_OPEN, SQUARE_CLOSE, NOT, OR, AND, THEN, IFF, SCOPE, RULE}

    # String containing ignored characters between tokens
    ignore = ' \t'

    # Regex rules for tokens
    EOS = r';'
    COMMA = r','
    NUM = r'[0-9]+'
    VAR = r'[a-zA-Z][a-zA-Z0-9_]*'
    COMMENT = r'//.*'
    EOL = r'\n'
    ROUND_OPEN = r'('
    ROUND_CLOSE = r')'
    CURLY_OPEN = r'{'
    CURLY_CLOSE = r'}'
    SQUARE_OPEN = r'['
    SQUARE_CLOSE = r']'
    NOT = r'(\~|\!)'
    OR = r'\|'
    AND = r'\&'
    THEN = r'\>'
    IFF = r'\<\>'
    SCOPE = r'-'
    RULE = r'(~E|~I|&E|&I|\|E|\|I|>E|>I|<>E|<>I)'
    BY = r'by'
    USING = r'using'
    CANCEL = r'cancel'
    ASSN = r'Assumption'
    HYPO = r'Hypothesis'
