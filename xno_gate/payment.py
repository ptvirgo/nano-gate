#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Entities

class Received:

    def __init__(self, amount, time):
        """Represent a *received* payment.

        Args:
            amount: int, amount in nano raw
            when: date time object converted from the block 'local timestamp.'

        """

        self.amount = amount
        self.time = time

    def __iter__(self):
        yield ("amount", self.amount)
        yield ("time", self.time.timestamp())


class Receivable:

    def __init__(self, amount):
        """Represent a pending payment.

        Args:
            amount: int, amount in nano raw
        """
        self.amount = amount

    def __iter__(self):
        yield ("amount", self.amount)


class Key:

    def __init__(self, account, amount, timeout, receivable):
        """If this account has been paid, how long should the gate be open?

        Args:
            account: str, xno address / public account id
            amount: int, required minimum payment
            timeout: int, seconds for the gate to remain open upon payment
            receivable: boolean, do we care about payments that are receivable but not yet received?
        """

        self.account = account
        self.amount = amount
        self.timeout = timeout
        self.receivable = receivable
