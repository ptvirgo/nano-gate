#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
from datetime import datetime, timedelta
import requests
import json

from xno_gate.entities import Key, LockState, Received, Receivable

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

    @abc.abstractmethod
    def save_lock_state(self, unlocked, until=None):
        """The gate is unlocked. Save a future datetime for when it might close again, so we don't need to query the RPC servers when we already know that the gate is unlocked.

        Arguments:
            unlocked: boolean, True if the gate is unlocked, False otherwise.
            until: datetime, a future time. The saved state is valid until this time.
        """
        pass

    @abc.abstractmethod
    def load_lock_state(self):
        """Check the cache to see if the gate is still unlocked from a previously saved lookup."""
        pass


class DefaultRPCInterface(XnoInterface):

    def __init__(self, proxy, cache_file, lookback=25, rate_limit=60):
        """Provide an interface to the nano Node RPC protocol.

        Arguments:
            proxy: str, url for an RPC node.
            cache_file: pathlib.Path to a json file that will be used to cache unlocked/locked lookup results.
            lookback: maximum number of transaction records to review for the account_history, per RPC spec.
            rate_limit: int, default number of seconds to apply on cached unlocked/locked lookup results.
        """
        self.proxy = proxy
        self.lookback = lookback
        self._cache_file = cache_file
        self._rate_limit = rate_limit

    @staticmethod
    def _history_to_received(history):
        """Convert an RPC acount_history transaction record into a Received object, or None as appropriate.

        Arguments:
            history: transaction json, per the [RPC spec](https://docs.nano.org/commands/rpc-protocol/#account_history)

        Output:
            payment.Received, or None
        """

        if history["type"] == "receive":
            return Received(int(history["amount"]), datetime.fromtimestamp(int(history["local_timestamp"])))

        return

    def received(self, account):
        rpc_call = \
            {
                "action": "account_history",
                "account": account,
                "count": self.lookback
            }

        result = requests.post(self.proxy, json=rpc_call)
        jsr = result.json()

        if "history" not in jsr:
            raise ValueError(f"RPC call unable to acquire history. status: {result.status_code}")

        return filter(None, [self._history_to_received(h) for h in jsr["history"]])

    def receivable(self, account, threshold=10 ** 30):
        rpc_call = \
            {
                "action": "receivable",
                "account": account,
                "threshold": str(threshold)
            }

        result = requests.post(self.proxy, json=rpc_call)
        jsr = result.json()

        if "blocks" not in jsr:
            raise ValueError(f"RPC call unable to acquire receivable blocks. status: {result.status_code}")

        if type(jsr["blocks"]) is dict:
            return [Receivable(int(amount)) for amount in jsr["blocks"].values()]

        return

    def save_lock_state(self, unlocked, until=None):

        if until is None:
            until = datetime.now() + timedelta(seconds=self._rate_limit)

        data = {"unlocked": unlocked, "until": until.timestamp()}

        with open(self._cache_file, "w") as f:
            json.dump(data, f)

        return

    def load_lock_state(self):

        if not self._cache_file.exists():
            return

        with open(self._cache_file, "r") as f:
            data = json.load(f)

        return LockState(data["unlocked"], datetime.fromtimestamp(data["until"]))


class Gate():

    def __init__(self, xno_interface):
        """Use the interface to verify payments, for the purposes of being unlocked or locked.

        Arguments:
            xno_interface: an XnoInterface
        """

        self.xno_interface = xno_interface
        self.keys = dict()

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

    def add_key(self, account, amount, timeout, receivable=False):
        """Add a Key that can make the gate "unlocked."

        Arguments:
            account: str, the nano public address to check
            amount: int, amount in raw
            timout: int, number of seconds gate should unlocked after a payment to the account is made
            receivable: boolean, do we care about payments that are receivable but not yet received?
        """
        self.keys[account] = Key(account, amount, timeout, receivable)

    def unlocked(self):
        """Is the gate unlocked?
            Output: a future datetime (when it will be locked again) if unlocked, or None if locked.
        """
        now = datetime.now()
        lock_state = self.xno_interface.load_lock_state()

        # Defer to cache
        if lock_state and lock_state.until > now:

            if lock_state.unlocked:
                return lock_state.until

            return

        # Check keys
        for key in sorted(self.keys.values(), key=lambda k: k.timeout, reverse=True):
            timeout = timedelta(seconds=key.timeout)
            cutoff = now - timeout

            if key.receivable and self.has_receivable(key.account, key.amount):
                self.xno_interface.save_lock_state(True, now + timeout)
                return now + timeout

            payment = self.been_paid(key.account, key.amount)
            if payment and payment > cutoff:
                self.xno_interface.save_lock_state(True, payment + timeout)
                return payment + timeout

        self.xno_interface.save_lock_state(False)
        return

    @staticmethod
    def to_raw(x):
        "Convert nano units to raw units."
        return x * 10 ** 30
