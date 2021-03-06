# Parser
from .nodes import *
from .token import *
from .error import InvalidSyntaxError
from .parse_result import ParseResult

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def parse(self):
        res = self.expr()
        if not res.error and self.curr.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.curr.pos_start,
                self.curr.pos_end,
                'Expected "+", "-", "*" or "/".')
            )

        return res

    def advance(self):
        '''Advance to next token.'''
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.curr = self.tokens[self.tok_idx]

        return self.curr

    def factor(self):
        '''Factor.'''
        res = ParseResult()
        tok = self.curr

        if tok.type in [TT_PLUS, TT_MINUS]:
            res.register_advance()
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def atom(self):
        '''Atom.'''
        res = ParseResult()
        tok = self.curr

        if tok.type in [TT_INT, TT_FLOAT]:
            res.register_advance()
            self.advance()
            return res.success(NumberNode(tok))
        elif tok.type == TT_IDENTIFIER:
            res.register_advance()
            self.advance()
            return res.success(VarAccessNode(tok))
        elif tok.type == TT_LPAREN:
            res.register_advance()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            
            if self.curr.type == TT_RPAREN:
                res.register_advance()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.curr.pos_start, self.curr.pos_end,
                    "Expected ')'."
                ))

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            'Expected int, float, identifier, "+", "-" or "("'))

    def power(self):
        '''Power.'''
        return self.bin_op(self.atom, [TT_POW], self.factor)

    def term(self):
        '''Term.'''
        return self.bin_op(self.factor, [TT_MUL, TT_DIV])

    def expr(self):
        '''Expression.'''
        res = ParseResult()
        if self.curr.equals(TT_KEYWORD, 'set'):
            res.register_advance()
            self.advance()

            if self.curr.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.curr.pos_start, self.curr.pos_end,
                    'Expected identifier.'
                ))

            name = self.curr
            res.register_advance()
            self.advance()

            if self.curr.type != TT_EQ:
                return res.failure(InvalidSyntaxError(
                    self.curr.pos_start, self.curr.pos_end,
                    'Expected "=".'
                ))

            res.register_advance()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            return res.success(VarAssignNode(name, expr))

        node = res.register(self.bin_op(self.term, [TT_PLUS, TT_MINUS]))
        if res.error:
            return res.failure(InvalidSyntaxError(
                self.curr.pos_start, self.curr.pos_end,
                'Expected "set", int, float, identifier, "+", "-" or "("'))

        return res.success(node)

    def bin_op(self, left_func, op_toks, right_func = None):
        '''Binary operation.'''
        if not right_func: right_func = left_func
        res = ParseResult()
        left = res.register(left_func())
        if res.error: return res

        while self.curr.type in op_toks:
            op_tok = self.curr
            res.register_advance()
            self.advance()
            right = res.register(right_func())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)
