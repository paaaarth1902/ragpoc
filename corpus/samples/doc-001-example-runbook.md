---
id: RB-001
title: Resume a Paused SLA Timer
doc_type: runbook
version: 1
---

## Overview
This runbook covers the procedure for resuming an SLA timer that was paused
during ticket handling. Use this when a ticket shows "SLA paused" for more than
30 minutes without an active hold reason, and the customer is awaiting response.

## Preconditions
- You have the Incident Manager or Service Desk Agent role.
- The ticket is in state "In Progress" or "On Hold".
- A valid pause reason is no longer applicable.

## Procedure
1. Open the ticket and verify the last pause reason is still valid. If the hold
   reason has cleared (e.g., customer responded), proceed to resume.
2. Click "Resume SLA" in the ticket actions menu. Confirm the resume action in
   the dialog. The SLA badge should turn green within 30 seconds.
3. Add a work note describing why the timer was resumed, referencing the pause
   reason that was cleared and the current ticket state.

## Verification
- The SLA badge shows "Running" (green).
- The SLA clock increments on page refresh.

## Rollback
If the SLA was resumed in error, click "Pause SLA" and select reason
"Resumed in error — reverting".