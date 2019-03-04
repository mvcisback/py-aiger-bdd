import hypothesis.strategies as st
from aiger import hypothesis as aigh
from aigerbv import atom
from hypothesis import given, settings

from aiger_bdd import to_bdd, from_bdd, count


@given(aigh.Circuits, st.data())
def test_bdd_transform(circ, data):
    circ = circ.unroll(3)
    out = list(circ.outputs)[0]
    f, manager, relabel = to_bdd(circ, output=out)
    expr = from_bdd(f)
    circ2 = expr.aig['i', relabel.inv]['o', {expr.output: out}]

    assert not circ2.latches
    assert circ2.inputs <= circ.inputs
    assert out in circ2.outputs

    test_input = {i: data.draw(st.booleans()) for i in circ.inputs}
    assert circ(test_input)[0][out] == circ2(test_input)[0][out]

    # TEST BDD version agrees.
    f2 = manager.let({relabel[k]: v for k, v in test_input.items()}, f)
    assert (f2 == manager.true) == (circ(test_input)[0][out])


@settings(max_examples=4, deadline=None)
@given(st.integers(0, 7))
def test_count_le(i):
    expr = atom(4, 'x', signed=False) < atom(4, i, signed=False)
    assert count(expr.aigbv.aig) == i
