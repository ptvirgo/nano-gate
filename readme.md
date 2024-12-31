# Nano-Gate

This is for [nano-currency](https://nano.org/en).

A **pay-gate** is similar to a pay-wall, with one key distinction. A *pay-wall* requires that every individual pay for access to content. A *pay-gate* allows everyone to access content for a period of time, provided that a payment has been delivered. Exactly as the name implies - when a gate is closed, no one gets in. As long as it's omen, *everyone can come in.*

This plays to the strengths of digital content - it is duplicable and can be delivered anonymously, rather than trying to fight it by imposing artificial scarcity.

## So ... make one

Function should accept a string account identifier, an integer representing an amount of nano, an integer representing seconds, and a node rpc url. It should produce a boolean: true if the account has been sent at least as many nano as requested within the given time frame. Essentially allowing questions like - "has account X received at least 2 nano in the past 300 seconds?"


## Use cases - answer these questions

- Has a single payment of {amount} been made to {nano address} within the past {number of seconds}?
    - When was the last time a payment of {amount} was made to {nano address}?
- What's the total amount of raw received by {nano address} within the past {number of seconds}?

- Is a single payment of {amount} pending to {nano address}?
- What's the total amount pending to {nano address}?
