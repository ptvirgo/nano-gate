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
