#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from random import random, randint

import factory
import factory.fuzzy as fuzzy

from gate.payment import Received, Receivable


class ReceivedFactory(factory.Factory):
    
    class Meta:
        model = Received

    amount = factory.Faker("random_int", min=0.5 * 10 ** 30, max=5 * 10 ** 30)
    time = factory.Faker("past_datetime", start_date=datetime.now() - timedelta(days=7))


class ReceivableFactory(factory.Factory):

    class Meta:
        model = Receivable

    amount = factory.Faker("random_int", min=10 ** 30, max=5 * 10 ** 30)
