import aiger
import hypothesis.strategies as st
from aiger import hypothesis as aigh
from aiger_bv import atom
from hypothesis import given, settings

from aiger_bdd import to_bdd, from_bdd, count


@given(aigh.Circuits)
def test_bdd_transform(circ):
    circ = circ.unroll(3)
    out = list(circ.outputs)[0]
    f, manager, relabel = to_bdd(circ, output=out)
    expr = from_bdd(f, manager=manager)

    circ2 = expr.aig['i', relabel.inv]['o', {expr.output: out}]
    assert not circ2.latches
    assert circ2.inputs <= circ.inputs
    assert out in circ2.outputs

    f2, _, relabel = to_bdd(
        expr.aig, manager=manager, output=expr.output, renamer=lambda *x: x[1]
    )
    assert f == f2


def test_bdd_transform_smoke():
    to_bdd(atom(3, 'x', signed=False) < 4)


@settings(max_examples=4, deadline=None)
@given(st.integers(0, 7))
def test_count_le(i):
    expr = atom(4, 'x', signed=False) < atom(4, i, signed=False)
    assert count(expr) == i
    assert count(expr, fraction=True) == i / (2**4)


def test_set_levels():
    a1, c1, a2, c2 = aiger.atoms('a1', 'c1', 'a2', 'c2')
    expr = (a1 == c1) & (a2 == c2)
    levels = {'c1': 0, 'a1': 1, 'c2': 2, 'a2': 3}

    bexpr, manager, relabels = to_bdd(
        expr, renamer=lambda _, x: x, levels=levels
    )

    assert all(k == v for k, v in relabels.items())
    assert bexpr.low.negated
    assert not bexpr.high.negated
