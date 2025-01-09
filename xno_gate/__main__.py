#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import xno_gate.gate as xno_gate

"""
This file is part of xno-gate.

xno-gate is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

xno-gate is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with xno-gate. If not, see <https://www.gnu.org/licenses/>.
"""


"""Minimal CLI demo of the gate."""


class CachelessRPCInterface(xno_gate.DefaultRPCInterface):
    """CLI only - RPC interface with null caching operations."""

    def __init__(self, proxy):
        super().__init__(proxy, None)

    def save_lock_state(*args, **kwargs):
        return

    def load_lock_state(*args, **kwargs):
        return


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
    rpc = CachelessRPCInterface(args.proxy)
    gate = xno_gate.Gate(rpc)

    amount = gate.to_raw(args.amount)

    result = gate.been_paid(args.account, amount)

    if result is None:
        print("Never")
        return

    print(result.isoformat())
