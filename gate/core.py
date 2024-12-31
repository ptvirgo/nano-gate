#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Abbreviated clean arch

# Entities

class Payment:
    
    def __init__(self, amount, when):
    
        """The relevant parts of a payment for gateway purposes.

        Args:
            amount: int, amount in nano raw
            when: date time object converted from the block 'local timestamp.'

        """

        self.amount = amount
        self.when = when


# Use Case


def to_raw(x):
    "Convert nano units to raw units."
    return x * 10 ** 30


def sum_recent(payments, after=None):
    """Sum the amount of payments, optionally filtering for after a given date.

    Args:
        payments: list of payments
        after = date time cutoff
    """

    x = 0

    for payment in payments:

        if after is None or payment.when > after:
            x += payment.amount

    return x
