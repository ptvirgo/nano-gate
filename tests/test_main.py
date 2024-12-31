#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from tests.factories import ReceivedFactory, ReceivableFactory
import gate.gate as xno_gate

import pytest


class FakeInterface(xno_gate.XnoInterface):

    def __init__(self, received, receivable):
        self._received = received
        self._receivable = receivable


    def received(self, _, count=10):
        return self._received[:count]


    def receivable(self, _, threshold=10 ** 30):
        return [rec for rec in self._receivable if rec.amount >= threshold]

standard_payments = \
    [
        ReceivedFactory(amount=1500, time=datetime(2024, 2, 27, 10, 33, 19, 0)),
        ReceivedFactory(amount=3500, time=datetime(2023, 8, 2, 13, 4, 7, 0)),
        ReceivedFactory(amount=5500, time=datetime(2022, 6, 15, 10, 33, 19, 0)),
    ]



@pytest.fixture
def standard_gate():
    receivables = [ReceivableFactory(amount=500), ReceivableFactory(amount=1000)]
    iface = FakeInterface(standard_payments, receivables)
    return xno_gate.Gate(iface)

def test_been_paid(standard_gate):
    """Test recent payment amounts."""
    [p1, p2, p3] = standard_payments

    assert standard_gate.been_paid("arbitrary for testing purposes", 1000) == p1.time
    assert standard_gate.been_paid("...", 2000) == p2.time
    assert standard_gate.been_paid("...", 4000) == p3.time
    assert standard_gate.been_paid("nah", 6000) == None


def test_total_paid(standard_gate):
    """Test total recent payment amounts."""
    [p1, p2, p3] = standard_payments

    assert standard_gate.total_received_since("hi", datetime(2020, 1, 1, 12, 0, 0, 0)) == p1.amount + p2.amount + p3.amount
    assert standard_gate.total_received_since("hi", datetime(2023, 1, 1, 12, 0, 0, 0)) == p1.amount + p2.amount
    assert standard_gate.total_received_since("hi", datetime(2024, 1, 1, 12, 0, 0, 0)) == p1.amount
    assert standard_gate.total_received_since("hi", datetime(2024, 8, 1, 12, 0, 0, 0)) == 0


def test_has_receivable(standard_gate):
    """Validate receivables"""

    assert standard_gate.has_receivable("mine", 200)
    assert standard_gate.has_receivable("mine", 1000)
    assert not standard_gate.has_receivable("mine", 1001)


def test_total_receivable(standard_gate):
    assert standard_gate.total_receivable("arbitrary") == 1500
