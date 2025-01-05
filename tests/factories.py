#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

import factory
from xno_gate.entities import Key, LockState, Received, Receivable


class ReceivedFactory(factory.Factory):

    class Meta:
        model = Received

    amount = factory.Faker("random_int", min=0.5 * 10 ** 30, max=5 * 10 ** 30)
    time = factory.Faker("past_datetime", start_date=datetime.now() - timedelta(days=7))


class ReceivableFactory(factory.Factory):

    class Meta:
        model = Receivable

    amount = factory.Faker("random_int", min=10 ** 30, max=5 * 10 ** 30)


class KeyFactory(factory.Factory):

    class Meta:
        model = Key

    account = factory.Faker("lexify", text="nano_??????????")
    amount = factory.Faker("random_int", min=0.5 * 10 ** 30, max=5 * 10 ** 30)
    timeout = factory.Faker("random_int", min=300, max=3600)
    receivable = False


class LockStateFactory(factory.Factory):

    class Meta:
        model = LockState

    unlocked = factory.Faker("boolean")
    until = factory.Faker("date_time_between", start_date=datetime.now() - timedelta(days=1), end_date=datetime.now() + timedelta(days=1))
