#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

from datetime import datetime

import xno_gate.core as xno


def history(account, representative, count=3):
    """Produce a request for the history of a nano account.

    Args:
        account: str, the nana address
        count: how many transactions do you want to know about?
        representative: url for a nano rep.

    Output: requests.Response - if successful, the json will carry form:

    {
        "account": "nano_1ipx847tk8o46pwxt5qjdbncjqcbwcc1rrmqnkztrfjy5k7z4imsrata9est",
        "history": [
          {
            "type": "send",
            "account": "nano_38ztgpejb7yrm7rr586nenkn597s3a1sqiy3m3uyqjicht7kzuhnihdk6zpz",
            "amount": "80000000000000000000000000000000000",
            "local_timestamp": "1551532723",
            "height": "60",
            "hash": "80392607E85E73CC3E94B4126F24488EBDFEB174944B890C97E8F36D89591DC5",
            "confirmed": "true"
          }
        ],
        "previous": "8D3AB98B301224253750D448B4BD997132400CEDD0A8432F775724F2D9821C72"
    }

    """

    data = {"action": "account_history", "account": account, "count": str(count)}
    return requests.post(representative, json=data)


def history_to_payment(history):
    """Convert a history dict into a Payment object.

    Args:
        history: transaction dict, as found in the "history" section of the "account_history" rpc response.
    
    Output: Payments object or None if the transaction was a send
    """

    if history["type"] == "receive":
        amount = int(history["amount"])
        when = datetime.fromtimestamp(int(history["local_timestamp"]))

        return xno.Payment(amount, when)

    return


def receivable(account, representative, amount=1, count=3):
    """Produce a request for the unclaimed, receivable blocks for an account.

    Args:
        account: str, the nano address
        count: how many transactions do you want to know about?
        amount: minimum amount threshold, optional
        representative: url for a nano rep.

    Output: requests.Request - if successful, json will carry form:

    {
        "blocks':
            {"D76E92ACFB99E84280B8E428D9DC44811205D6CE122F30326557715DBCFF67A9": 2000000,
             ...
             },
        "requestsLimit": "5000",
        "requestsRemaining": "4969",
        "requestLimitReset": "Sun Dec 29 2024 03:46:30 GMT+0000 (Greenwich Mean Time)"
    }

    Blocks section will be a dict of hash -> amount.
    """

    data = {"action": "receivable", "account": account, "count": str(count), "threshold": amount}
    return requests.post(representative, json=data)
