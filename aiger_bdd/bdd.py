import aiger
import funcy as fn
from aiger import common as cmn
from bidict import bidict
from fractions import Fraction

try:
    from dd.cudd import BDD
except ImportError:
    from dd.autoref import BDD


def to_bdd(circ_or_expr, output=None, manager=None, renamer=None, levels=None):
    if renamer is None:
        _count = 0

        def renamer(*_):
            nonlocal _count
            _count += 1
            return f"x{_count}"

    if not isinstance(circ_or_expr, aiger.AIG):
        circ = circ_or_expr.aig
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
    if levels is not None:
        manager.reorder(levels)
        manager.configure(reordering=False)

    gate_nodes = {}
    for gate in cmn.eval_order(circ):
        if isinstance(gate, aiger.aig.ConstFalse):
            gate_nodes[gate] = manager.add_expr('False')
        elif isinstance(gate, aiger.aig.Inverter):
            gate_nodes[gate] = ~gate_nodes[gate.input]
        elif isinstance(gate, aiger.aig.Input):
            gate_nodes[gate] = manager.var(input_refs_to_var[gate.name])
        elif isinstance(gate, aiger.aig.AndGate):
            gate_nodes[gate] = gate_nodes[gate.left] & gate_nodes[gate.right]

    return gate_nodes[output], manager, bidict(input_refs_to_var)


def from_bdd(node, manager=None):
    if manager is None:
        manager = node.bdd

    name = node.var
    if name is None:  # Must be a leaf True xor False node.
        return aiger.atom(node == manager.true)

    test = aiger.atom(name)
    low, high = [from_bdd(c, manager) for c in (node.low, node.high)]
    expr = aiger.ite(test, high, low)
    return ~expr if node.negated else expr


def count(circ_or_expr, fraction=False, output=None):
    f, *_ = to_bdd(circ_or_expr, output)
    if not isinstance(circ_or_expr, aiger.AIG):
        circ_or_expr = circ_or_expr.aig

    n_inputs = len(circ_or_expr.inputs)
    num_models = int(f.count(n_inputs))
    return Fraction(num_models, (2**n_inputs)) if fraction else num_models
