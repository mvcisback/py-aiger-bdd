import aiger
import funcy as fn

from aiger import common as cmn
from bidict import bidict
from parsimonious import Grammar, NodeVisitor
try:
    from dd.cudd import BDD
except ImportError:
    from dd.autoref import BDD


def to_bdd(circ_or_expr, output=None, manager=None, renamer=None):
    if renamer is None:
        _count = 0

        def renamer(*_):
            nonlocal _count
            _count += 1
            return f"x{_count}"

    if isinstance(circ_or_expr, aiger.BoolExpr):
        circ, output = circ_or_expr.aig, circ_or_expr.output
    else:
        circ = circ_or_expr

    node_map = dict(circ.node_map)

    assert len(circ.latches) == 0
    if output is None:
        assert len(circ.outputs) == 1
        output = node_map[fn.first(circ.outputs)]
    else:
        output = node_map[output]  # By name instead.

    manager = BDD() if manager is None else manager

    input_refs_to_var = {
        ref: renamer(i, ref) for i, ref in enumerate(circ.inputs)
    }
    manager.declare(*input_refs_to_var.values())

    gate_nodes = {}
    for gate in cmn.eval_order(circ):
        if isinstance(gate, aiger.aig.ConstFalse):
            gate_nodes[gate] = manager.add_expr('False')
        elif isinstance(gate, aiger.aig.Inverter):
            gate_nodes[gate] = ~gate_nodes[gate.input]
        elif isinstance(gate, aiger.aig.Input):
            gate_nodes[gate] = manager.add_expr(input_refs_to_var[gate.name])
        elif isinstance(gate, aiger.aig.AndGate):
            gate_nodes[gate] = gate_nodes[gate.left] & gate_nodes[gate.right]

    return gate_nodes[output], manager, bidict(input_refs_to_var)


BDDEXPR_GRAMMAR = Grammar(u'''
bdd_expr = neg / ite / id / const
ite = "ite(" id ", " bdd_expr ", " bdd_expr ")"
neg = "(~ " bdd_expr ")"
id = ~r"[a-z\d]+"
const = "TRUE" / "FALSE"
''')


class BDDExprVisitor(NodeVisitor):
    def generic_visit(self, _, children):
        return children

    def visit_id(self, node, _):
        return aiger.atom(node.text)

    def visit_ite(self, _, children):
        return children[1].select(children[3], children[5])

    def visit_neg(self, _, children):
        return ~children[1]

    def visit_bdd_expr(self, _, children):
        return children[0]

    def visit_const(self, node, _):
        return aiger.atom(node.text == "TRUE")


def _parse_bddexpr(ite_str: str):
    return BDDExprVisitor().visit(BDDEXPR_GRAMMAR.parse(ite_str))


def from_bdd(bdd_func, manager=None):
    if manager:
        return _parse_bddexpr(manager.to_expr(bdd_func))
    return _parse_bddexpr(bdd_func.to_expr())
