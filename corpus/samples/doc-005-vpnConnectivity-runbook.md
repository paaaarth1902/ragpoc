---
id: RB-004
title: VPN FAQs
doc_type: runbook
version: 1
---

## Overview
This FAQ answers common questions about corporate VPN access using the
GlobalConnect client. It covers enrollment, common errors, and connectivity
troubleshooting for remote employees.

## How do I request VPN access?
Submit a request through the service catalog item "VPN Access Request". Approval
is granted by your line manager and provisioned within one business day. Access
requires an active MFA enrollment.

## Why do I get error VPN-619 when connecting?
Error code VPN-619 means the VPN gateway rejected your credentials. Common causes:
- Your MFA token expired — re-enroll in the MFA portal.
- Your account password was recently reset — wait 15 minutes for replication.
- You are using an outdated GlobalConnect client (below version 7.2).

## Why is my VPN connection slow?
Slow VPN usually indicates split-tunneling is disabled or you are routed through
a distant gateway. Switch to the nearest regional gateway in client settings:
US-EAST, EU-WEST, or AP-SOUTH. Restart the client after changing the gateway.

## Who do I contact for persistent VPN issues?
If error VPN-619 persists after the above steps, raise a ticket to the
"Network-VPN" assignment group with your client version and the exact error code.