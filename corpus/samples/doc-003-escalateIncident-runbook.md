---
id: RB-003
title: Escalate a P1 Incident
doc_type: runbook
version: 1
---

## Overview
This runbook defines the escalation procedure for a P1 (Priority 1) major
incident — a critical, business-wide outage with no workaround. P1 incidents
require immediate major incident management (MIM) engagement.

## When to Use
Trigger this runbook when an incident meets P1 criteria:
- Business-critical service fully unavailable (impact code IMP-001).
- Affects more than 500 users or a revenue-generating system.
- No acceptable workaround exists.

## Escalation Procedure
1. Set the incident priority to P1 and the category to "Major Incident".
2. Page the on-call Major Incident Manager via the MIM-ONCALL rotation in
   PagerDuty. Use escalation policy EP-P1-CRITICAL.
3. Open a dedicated bridge: dial 1-800-MIM-BRIDGE and post the conference link
   in the #major-incidents Slack channel.
4. Assign the incident to assignment group "MIM-Command" and set the
   communication lead.
5. Send the first stakeholder update within 15 minutes using template
   TMPL-P1-INITIAL.

## SLA Targets for P1
- Acknowledge: 5 minutes.
- First update: 15 minutes.
- Update cadence: every 30 minutes until resolved.

## Deescalation
Downgrade from P1 only when a workaround is confirmed and impact drops below
P1 thresholds. Record the downgrade reason with code DG-REASON.
