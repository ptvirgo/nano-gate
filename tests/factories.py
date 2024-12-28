#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from random import random, randint
import factory
import factory.fuzzy as fuzzy


class FakeHistory():
    """Fake the output of a nano history response message, per the RPC protocol spec."""

    def __init__(self, history_type, account, amount, local_timestamp, hsh, confirmed):

        self.history_type = history_type,
        self.account = account,
        self.amount = amount,
        self.local_timestamp = local_timestamp,
        self.hsh = hsh,
        self.confirmed = confirmed

    def __iter__(self):

        yield ("history", self.history_type)
        yield ("account", self.account)
        yield ("amount", self.amount)
        yield ("local_timestamp", self.local_timestamp)
        yield ("hash", self.hsh)
        yield ("confirmed", self.confirmed)


class FakeReceive():
    """Fake the output of a nano receivable response message, per the protocol spec."""

    def __init__(self, block, amount=None):
        self.block = block
        self.amount = amount

    def __iter__(self):

        if self.amount:
            yield (self.block, self.amount)

        else:
            yield self.block


def fake_hash():
    i = 0
    
    while True:
        i += 1
        yield f"FAKE_HASH_DUMB_{i:03}"


class HistoryFactory(factory.Factory):

    class Meta:
        model = FakeHistory

    history_type = fuzzy.FuzzyChoice(["send", "receive"])
    account = fuzzy.FuzzyChoice(["nano_1ipx847tk8o46pwxt5qjdbncjqcbwcc1rrmqnkztrfjy5k7z4imsrata9est", "nano_3qgtign8zoehkhdt1atf1qm6m7ui5kgwin8tjnjrzdidtgjy1xr7d156ib5q"])

    amount = factory.LazyAttribute(lambda o: random() * (10 ** 30))

    @factory.lazy_attribute
    def local_timestamp(self):
        before = randint(60, 600)
        when = datetime.now() - timedelta(seconds=before)
        return when.timestamp()

    hsh = factory.Faker("sentence")
    confirmed = factory.Faker("boolean")


class ReceiveFactory(factory.Factory):

    class Meta:
        model = FakeReceive
        exclude = ("with_amount",)

    with_amount = True
    block = factory.Iterator(fake_hash())

    @factory.lazy_attribute
    def amount(self):

        if self.with_amount:
            return random() * (10 ** 30)
        else:
            return
