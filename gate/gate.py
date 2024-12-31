#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import requests

"Provide means for the admin to determine whether appropriate payments have been made or are pending."


class XnoInterface(abc.ABC):
    """Provide an external interface to the Nano block lattice, or simulate for testing, etc. as needed."""

    
    @abc.abstractmethod
    def received(self, account):
        """Produce Received payments to the given account. Note that it is up to this interface to handle the RPC transaction lookback count.

        Arguments:
            account: str, the nano public address to check.

        Output:
            Array of payment.Received
        """
        pass

    @abc.abstractmethod
    def receivable(self, account, threshold=10 ** 30):
        """Produce Reveivable payments for the given account, above a given threshold.

        Arguments:
            account: str, the nano public address to check.
            threshold: the minimum amount of raw we care about. Default is 10 ** 30 raw, aka 1 nano. 

        Output:
            Array of payment.Receivable
        """
        pass


class Gate():

    def __init__(self, xno_interface):
        """Use the interface to verify payments, for the purposes of being open or closed.

        Arguments:
            xno_interface: an XnoInterface
        """

        self.xno_interface = xno_interface

    def _received(self, account):
        """Produce the Received transactions for a given account, sorted in reverse date order."""
        return sorted(self.xno_interface.received(account), key=lambda x: x.time, reverse=True)

    def been_paid(self, account, amount):
        """When was the last time {account} got paid at least {amount}?

        Arguments:
            account: str, the nano public address to check
            amount: int, smallest relevant amount in raw

        Output:
            A datetime or None. As of this writing, the nano interface only produces local timestamps without timezone information, so the datetime should be considered naive regarding time zone.
        """

        for payment in self._received(account):
            if payment.amount >= amount:
                return payment.time

    def total_received_since(self, account, when):
        """How many raw have been received by {account} since {when}?

        Arguments:
            account: str, nano public address to check
            when: datetime in the past

        Output: Int - total raw received.
        """

        total = 0

        for payment in self._received(account):
            if payment.time >= when:
                total += payment.amount

        return total

    def has_receivable(self, account, amount):
        """Does the {account} have a receivable of at least {amount}?

        Arguments:
            account: str, the nano public address to check
            amount: int, smallest relevant amount in raw

        Output: Boolean
        """

        receivable = self.xno_interface.receivable(account, amount)
        return len(receivable) > 0

    def total_receivable(self, account):
        """What's the total receivable to {account}?

        Arguments:
            account: str, the nano public address to check

        Output: int - raw total
        """
        total = 0

        for payment in self.xno_interface.receivable(account, 1):
            total += payment.amount

        return total


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
