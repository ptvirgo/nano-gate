#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import xno_gate.gate as xno_gate

"""Minimal CLI demo of the Nane gate."""


def cli_args():
    """Get the arguments from the CLI."""

    parser = argparse.ArgumentParser(description="Ask the Nano RPC when the last time an account received some nano.")
    parser.add_argument("proxy", type=str, help="API proxy url. See https://docs.nano.org/integration-guides/#public-apis")
    parser.add_argument("account", type=str, help="Nano account (public address) to check.")
    parser.add_argument("amount", type=int, help="How many nano?", )

    return parser.parse_args()


def been_paid():
    "Ask the Nano RPC when the last time an account received some nano."

    args = cli_args()
    rpc = xno_gate.DefaultRPCInterface(args.proxy)
    gate = xno_gate.Gate(rpc)

    amount = gate.to_raw(args.amount)

    result = gate.been_paid(args.account, amount)

    if result is None:
        print("Never")
        return

    print(result.isoformat())
