---
id: RB-002
title: Pause a running SLA timer
doc_type: runbook
version: 1
---

## Overview
This runbook describes how to pause an active SLA timer when a ticket is
legitimately blocked and waiting on an external party. Pausing stops the SLA
clock so the team is not penalized for delays outside its control.

## Preconditions
- You have the Service Desk Agent role or higher.
- The ticket SLA is currently "Running" (green badge).
- A valid blocking condition exists (awaiting customer, vendor, or change window).

## Procedure
1. Open the ticket and confirm the blocking reason. Common reasons include
   "Awaiting customer response", "Awaiting vendor", and "Pending change window".
2. Click "Pause SLA" in the ticket actions menu. Select the correct pause reason
   from the dropdown. The SLA badge should turn amber within 30 seconds.
3. Add a work note stating the pause reason and the expected unblock date. Set a
   follow-up reminder so the ticket is not forgotten while paused.

## Verification
- The SLA badge shows "Paused" (amber).
- The SLA clock stops incrementing on refresh.

## Common Mistakes
- Pausing without a valid reason inflates SLA metrics and may be flagged in audit.
- Forgetting to resume after the blocker clears — see runbook_resume_sla.