import aiger
import funcy as fn
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

    if not isinstance(circ_or_expr, aiger.BoolExpr):
        circ = aiger.to_aig(circ_or_expr, allow_lazy=True)
        assert len(circ.latches) == 0

        if output is None:
            assert len(circ.outputs) == 1
            output = fn.first(circ.outputs)

        expr = aiger.BoolExpr(circ)
    else:
        expr = circ_or_expr

    manager = BDD() if manager is None else manager
    input_refs_to_var = {
        ref: renamer(i, ref) for i, ref in enumerate(expr.inputs)
    }

    manager.declare(*input_refs_to_var.values())
    if levels is not None:
        assert set(manager.vars) <= set(levels.keys())
        levels = fn.project(levels, manager.vars.keys())
        levels = fn.walk_keys(input_refs_to_var.get, levels)

        manager.reorder(levels)
        manager.configure(reordering=False)

    def lift(obj):
        if isinstance(obj, bool):
            return manager.true if obj else manager.false
        return obj

    inputs = {i: manager.var(input_refs_to_var[i]) for i in expr.inputs}
    out = expr(inputs, lift=lift)
    return out, out.bdd, bidict(input_refs_to_var)


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
