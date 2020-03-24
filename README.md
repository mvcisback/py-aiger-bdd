# py-aiger-bdd
[![Build Status](https://cloud.drone.io/api/badges/mvcisback/py-aiger-bdd/status.svg)](https://cloud.drone.io/mvcisback/py-aiger-bdd)
[![codecov](https://codecov.io/gh/mvcisback/py-aiger-bdd/branch/master/graph/badge.svg)](https://codecov.io/gh/mvcisback/py-aiger-bdd)

[![PyPI version](https://badge.fury.io/py/py-aiger-bdd.svg)](https://badge.fury.io/py/py-aiger-bdd)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Installation

`$ pip install py-aiger-bdd`

For developers, note that this project uses the
[poetry](https://poetry.eustace.io/) python package/dependency
management tool. Please familarize yourself with it and then
run:

`$ poetry install`

# Usage

This tutorial assumes familiarity with [py-aiger](https://github.com/mvcisback/py-aiger) and [py-aiger-bv](https://github.com/mvcisback/py-aiger-bv).

```python
import aiger_bv as BV
from aiger_bdd import to_bdd, from_bdd, count

x = BV.atom(3, 'x', signed=False) 

expr = x < 5  # Could be an AIG or AIGBV or BoolExpr.
bdd, manager, input2var = to_bdd(expr)  # Convert circuit encoded by expr into a BDD.
expr2 = from_bdd(bdd)  # Creates an Aiger Expression from a BDD.

assert count(expr, fraction=True) == 5/8
assert count(expr, fraction=False) == 5
```
