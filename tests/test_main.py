#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from tests.factories import KeyFactory, LockStateFactory, ReceivedFactory, ReceivableFactory
from xno_gate.entities import LockState
import xno_gate.gate as xno_gate

import pytest


class FakeInterface(xno_gate.XnoInterface):

    def __init__(self, received, receivable):
        self._received = received
        self._receivable = receivable
        self._lock_state = None

    def received(self, _, count=10):
        return self._received[:count]

    def receivable(self, _, threshold=10 ** 30):
        return [rec for rec in self._receivable if rec.amount >= threshold]

    def save_lock_state(self, unlocked, until):
        self._lock_state = LockState(unlocked, until)

    def load_lock_state(self):
        return self._lock_state


standard_payments = \
    [
        ReceivedFactory(amount=1500, time=datetime(2024, 2, 27, 10, 33, 19, 0)),
        ReceivedFactory(amount=3500, time=datetime(2023, 8, 2, 13, 4, 7, 0)),
        ReceivedFactory(amount=5500, time=datetime(2022, 6, 15, 10, 33, 19, 0)),
    ]


class UnlockableInterface(xno_gate.XnoInterface):

    def __init__(self):
        self._received = dict()
        self._receivable = dict()
        self._lock_state = None

    def add_received(self, account, received):
        self._received[account] = received

    def add_receivable(self, account, receivable):
        self._receivable[account] = receivable

    def received(self, account, threshold=10 ** 30):

        if account in self._received:
            return [self._received[account]]

        return []

    def receivable(self, account, threshold=10 ** 30):

        if account in self._receivable and self._receivable[account].amount >= threshold:
            return [self._receivable[account]]

        return []

    def save_lock_state(self, unlocked, until):
        self._lock_state = LockState(unlocked, until)

    def load_lock_state(self):
        return self._lock_state


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


def test_history_to_payment(tmp_path):
    "Verify account history transaction record as a Payment object."

    cache = tmp_path / "rpc_cache.json"
    rpc = xno_gate.DefaultRPCInterface("not a proxy lol", cache)

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


def test_gate_unlocks():
    """Make sure a gate can be locked or unlocked."""

    iface = UnlockableInterface()
    gate = xno_gate.Gate(iface)

    key = KeyFactory()
    gate.add_key(key.account, key.amount, key.timeout)

    assert gate.unlocked() is None

    received = ReceivedFactory(amount=key.amount + 1, time=datetime.now() - timedelta(seconds=key.timeout + 1))
    iface.add_received(key.account, received)

    assert gate.unlocked() is None

    received = ReceivedFactory(amount=key.amount - 1, time=datetime.now())
    iface.add_received(key.account, received)

    assert gate.unlocked() is None

    received = ReceivedFactory(amount=key.amount + 1, time=datetime.now() - timedelta(seconds=key.timeout - 1))
    iface = iface.add_received(key.account, received)
    difference = gate.unlocked() - datetime.now()

    assert difference >= timedelta(seconds=0) and difference < timedelta(seconds=2)


def test_gate_stays_unlocked():
    """When a gate is unlocked, it should stay unlocked for the longest available time period."""

    iface = UnlockableInterface()
    gate = xno_gate.Gate(iface)

    short_key = KeyFactory(timeout=5 * 60)
    long_key = KeyFactory(timeout=15 * 60)

    gate.add_key(short_key.account, short_key.amount, short_key.timeout)
    gate.add_key(long_key.account, long_key.amount, long_key.timeout)

    received = ReceivedFactory(amount=max(short_key.amount, long_key.amount) + 1, time=datetime.now())

    iface.add_received(short_key.account, received)
    iface.add_received(long_key.account, received)

    difference = gate.unlocked() - datetime.now()

    assert difference > timedelta(seconds=short_key.timeout) and difference <= timedelta(seconds=long_key.timeout)


def test_gate_handles_receivables():
    """When we accept receivables, the gate unlocked."""
    iface = UnlockableInterface()
    gate = xno_gate.Gate(iface)

    key = KeyFactory()

    gate.add_key(key.account, key.amount, key.timeout, receivable=False)
    assert gate.unlocked() is None

    receivable = ReceivableFactory(amount=key.amount)
    iface.add_receivable(key.account, receivable)

    assert gate.unlocked() is None

    gate.add_key(key.account, key.amount, key.timeout, receivable=True)
    assert gate.unlocked() >= datetime.now() + timedelta(seconds=key.timeout - 1)


def test_default_rpc_save_lock_state(tmp_path):
    """Make sure the default RPC can save and "unlocked" load dates for the cache."""

    cache = tmp_path / "rpc_cache.json"

    saver = xno_gate.DefaultRPCInterface("Not a real proxy.", cache)
    loader = xno_gate.DefaultRPCInterface("Still not a proxy.", cache)

    assert loader.load_lock_state() is None

    expect = LockStateFactory()

    saver.save_lock_state(expect.unlocked, expect.until)
    result = loader.load_lock_state()

    assert result.unlocked == expect.unlocked
    assert result.until == expect.until


def test_gate_prefers_cache():
    """Make sure the gate will prefer a cache to a lookup if an unexpired cache exists."""

    received = [ReceivedFactory(time=datetime.now())]
    iface = FakeInterface(received, [])
    gate = xno_gate.Gate(iface)

    assert False
