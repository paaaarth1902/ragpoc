---
id: RB-001
title: Restoring a Paused SLA Clock
doc_type: runbook
version: 1
---

## Purpose
This runbook covers the procedure for resuming an SLA timer that was paused during an incident. It should be used any time a ticket has been paused for longer than 30 minutes without an active work note.

## When to use this runbook
Use this when a ticket shows "SLA paused" for more than 30 minutes without an active work note, and the pause reason is no longer valid. Do not use this if the incident is still in escalation review.

## Procedure

### Step 1 — Confirm the pause reason
Open the ticket and verify the last pause reason is still valid. If the reason references an external dependency that has since resolved, proceed to Step 2. Otherwise, escalate to the incident commander.

### Step 2 — Resume the timer
Click "Resume SLA" in the ticket actions menu. Confirm the resume action in the dialog. The SLA badge should turn green within 30 seconds.

### Step 3 — Add a work note
Add a work note describing why the timer was resumed, referencing the change ticket or incident number that resolved the pause condition.