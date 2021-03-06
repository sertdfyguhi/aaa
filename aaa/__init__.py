from .interpreter import Interpreter
from .lexer import Lexer
from .parser import Parser
from .context import Context
from .symbol_table import SymbolTable

glob_sym_table = SymbolTable()

def run(fn, code):
    lexer = Lexer(fn, code)
    tok, error = lexer.make_tokens()
    if error: return error

    # Generate abstract syntax tree.
    parser = Parser(tok)
    ast = parser.parse()
    if ast.error: return ast.error

    # Run program using interpreter
    interpreter = Interpreter()
    context = Context('<program>')
    context.sym_table = glob_sym_table
    res = interpreter.visit(ast.node, context)

    if res.error: return res.error
    return res.value