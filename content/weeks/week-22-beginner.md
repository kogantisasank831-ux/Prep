---
layout: week
week: 22
phase: 5
status: review
version: 1.0.0
last_reviewed: 2026-11-11
estimated_hours: 8
permalink: /weeks/week-22/beginner/
title: "Give an AI application a small, labelled toolbox"
description: Learn MCP hosts, clients, servers, tools, resources and prompts with one read-only supplier example.
summary: A common protocol helps applications discover capabilities, while ordinary permission checks keep those capabilities safe.
kicker_primary: Beginner path
kicker_secondary: One tool, one resource, one prompt and no real supplier action
current_label: Beginner version
alternate_label: Production version
alternate_url: /weeks/week-22/
---

## Before you start

You need basic Python functions and the idea of an API request. The
[production route]({{ '/weeks/week-22/' | relative_url }}) adds the current
protocol revision, token audience rules, confused-deputy risks and transport
testing.

The [Week 22 assessment]({{ '/assessments/week-22/' | relative_url }}) uses ten
balanced questions.

## Think of a labelled toolbox

An AI application can connect to many systems. Without a common shape, every
integration needs different code. MCP gives clients and servers a shared way to
describe and call capabilities.

- The **host** is the application the user sees.
- The **client** inside the host speaks MCP to one server.
- The **server** offers a small set of capabilities.

MCP does not give the model unlimited access. The host and server still decide
what is permitted.

## Three capability types

| Type | Who normally chooses it? | Lab example |
| --- | --- | --- |
| tool | model, under application policy | look up a supplier |
| resource | application | read a static lookup policy |
| prompt | user | choose a supplier-review template |

A prompt is not a permission token. A resource should not quietly expose an
entire private database. A tool must validate its inputs and permissions.

## The safest tenant argument is no tenant argument

The model supplies `supplier_id`. It cannot supply `tenant_id` or claim the
`supplier:read` scope. Those facts come from a trusted identity layer before the
server is created.

If tenant A requests tenant B's supplier, the answer is simply `not_found`, the
same as an unknown ID. This prevents the model from changing the tenant and
reduces information leakage.

## Discover, then authorize

Discovery lists available tools, resources and prompts. It is like reading the
labels on a toolbox. The server still checks permission when a tool is actually
called.

The lookup annotation says the tool is read-only and non-destructive. That helps
clients display it correctly, but an annotation cannot stop a malicious caller.
The server's permission check is the control.

## Run it

~~~shell
python -m labs.week_22.demo describe
python -m labs.week_22.demo call --supplier-id supplier-101
python -m labs.week_22.demo smoke
python -m pytest tests/test_week22_mcp.py -q
~~~

Try `supplier-909`. It belongs to another synthetic tenant and should look
exactly like an ID that does not exist.

## What the demo does not include

There is no login system, OAuth server, remote API, model, secret or real
supplier. Tests call the registered capabilities inside one Python process.
Production needs authenticated connections, audience-bound tokens, separate
downstream credentials, rate limits, audit records and an independent client
test.

## Completion checklist

- Explain host, client and server.
- Tell tools, resources and prompts apart.
- Keep tenant and scope outside model arguments.
- Say why discovery is not authorization.
- Run allowed, denied and cross-tenant checks.
- State that the local test does not prove transport security.
