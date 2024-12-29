#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import tests.factories as factories

import xno_gate.core as xno
import xno_gate.nano_rpc as rpc


def test_to_raw_runs():
    "Can computers do numbers though?"

    for x in range(10):
        assert xno.to_raw(x) == x * (10 ** 30)


def test_sum():
    "Do a basic check on sum payments."

    set_one = [factories.PaymentFactory(amount=500), factories.PaymentFactory(amount=10000), factories.PaymentFactory(amount=7500)]

    assert xno.sum_recent(set_one) == (500 + 10000 + 7500)

    set_two = \
        [
            factories.PaymentFactory(amount=5000, when=datetime(2020, 6, 15, 14, 48, 22, 0)),
            factories.PaymentFactory(amount=270, when=datetime(2023, 3, 12, 22, 9, 7, 84628)),
            factories.PaymentFactory(amount=6781, when=datetime(2024, 2, 4, 17, 22, 3, 0))
        ]

    assert xno.sum_recent(set_two, after=datetime(2020, 1, 1, 12, 0, 0, 0)) == 5000 + 270 + 6781
    assert xno.sum_recent(set_two, after=datetime(2022, 1, 1, 12, 0, 0, 0)) == 270 + 6781
    assert xno.sum_recent(set_two, after=datetime(2024, 1, 1, 12, 0, 0, 0)) == 6781
    assert xno.sum_recent(set_two, after=datetime(2024, 6, 1, 12, 0, 0, 0)) == 0


def test_history_to_payment():
    "Verify account history transaction record as a Payment object."

    payment = rpc.history_to_payment(
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
    assert payment.when == datetime(2024, 9, 23, 1, 42, 18)

    sent = rpc.history_to_payment(
        {
            'type': 'send',
            'account': 'nano_1iroza4zsyt95uk6ucwhe1nwbe5q7g87gxfhcyuoetfkz5jmac8mtfwwoac4',
            'amount': '1000000000000000000000000000000',
            'local_timestamp': '1726641467',
            'height': '15',
            'hash': '695C51F6FC9E3F2DF2F60F90969DB99AA84A6A528C2BBD37365E795090DE7F02',
            'confirmed': 'true'
        })

    assert sent == None
