#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xno_gate.core as xno
import tests.factories as factories

def test_to_raw_runs():
    "Can computers do numbers though?"

    for x in range(10):
        assert xno.to_raw(x) == x * (10 ** 30)


def test_factory_runs():
    "Make sure it runs."

    factories.HistoryFactory()
