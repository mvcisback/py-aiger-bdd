# py-aiger-bdd
[![Build Status](https://travis-ci.org/mvcisback/py-aiger-bdd.svg?branch=master)](https://travis-ci.org/mvcisback/py-aiger-bdd)
[![codecov](https://codecov.io/gh/mvcisback/py-aiger-bdd/branch/master/graph/badge.svg)](https://codecov.io/gh/mvcisback/py-aiger-bdd)
[![Updates](https://pyup.io/repos/github/mvcisback/py-aiger-bdd/shield.svg)](https://pyup.io/repos/github/mvcisback/py-aiger-bdd/)

[![PyPI version](https://badge.fury.io/py/py-aiger-bdd.svg)](https://badge.fury.io/py/py-aiger-bdd)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Installation

`$ pip install py-aiger-bdd`

# Usage

This tutorial assumes familiarity with [py-aiger](https://github.com/mvcisback/py-aiger) and [py-aiger-bv](https://github.com/mvcisback/py-aiger-bv).

```python
import aigerbv
from aiger_bdd import to_bdd, from_bdd, count

x = aigerbv.atom(3, 'x', signed=False) 

expr = x < 5  # Could be an AIG or AIGBV or BoolExpr.
bdd = to_bdd(expr)  # Convert circuit encoded by expr into a BDD.
expr2 = from_bdd(bdd)  # Creates an Aiger Expression from a BDD.

assert count(expr) == 5/8
assert count(expr, fraction=False) == 5
```
