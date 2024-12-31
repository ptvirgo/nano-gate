#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from tests.factories import ReceivedFactory, ReceivableFactory
import xno_gate.gate as xno_gate

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
    assert standard_gate.been_paid("nah", 6000) is None


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
    """Verify that computers can do basic arithmatic."""
    assert standard_gate.total_receivable("arbitrary") == 1500


def test_history_to_payment():
    "Verify account history transaction record as a Payment object."

    rpc = xno_gate.DefaultRPCInterface("not a proxy lol")

    payment = rpc._history_to_received(
        {
            'type': 'receive',
            'account': 'nano_1iroza4zsyt95uk6ucwhe1nwbe5q7g87gxfhcyuoetfkz5jmac8mtfwwoac4',
            'amount': '2700000000000000000000000000000',
            'local_timestamp': '1727070138',
            'height': '16',
            'hash': 'CEE35D7EB15AC306BC5861391653EFFFE697D708D72C759C4398990637DCA8F4',
            'confirmed': 'true'
        }
    )

    assert payment.amount == 2700000000000000000000000000000
    assert payment.time == datetime(2024, 9, 23, 1, 42, 18)

    sent = rpc._history_to_received(
        {
            'type': 'send',
            'account': 'nano_1iroza4zsyt95uk6ucwhe1nwbe5q7g87gxfhcyuoetfkz5jmac8mtfwwoac4',
            'amount': '1000000000000000000000000000000',
            'local_timestamp': '1726641467',
            'height': '15',
            'hash': '695C51F6FC9E3F2DF2F60F90969DB99AA84A6A528C2BBD37365E795090DE7F02',
            'confirmed': 'true'
        })

    assert sent is None
