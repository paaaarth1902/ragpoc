---
id: RB-004
title: Reset a User Active Directory Password
doc_type: runbook
version: 1
---

## Overview
This runbook covers resetting a locked or forgotten Active Directory (AD)
password for an end user. Use it when a user reports they cannot sign in and
self-service password reset (SSPR) is unavailable.

## Preconditions
- You have Service Desk Tier 1 access and the AD Helpdesk role.
- The user's identity has been verified per the ID-VERIFY-02 policy.
- The user's account is not disabled (disabled accounts require Tier 2).

## Procedure
1. Locate the user account in the admin console by their corporate email or
   employee ID.
2. Confirm the account is "Locked" or "Password expired", not "Disabled".
3. Reset the password using the standard command:
   `Set-ADAccountPassword -Identity jdoe -Reset`
   then force a change at next logon:
   `Set-ADUser -Identity jdoe -ChangePasswordAtLogon $true`
4. Communicate the temporary password to the user through a secure channel only
   (never over plain email). Follow policy SEC-COMM-01.

## Verification
- The user confirms they can sign in with the temporary password.
- The user is prompted to set a new password at first logon.

## Security Notes
- Never reuse temporary passwords across users.
- Log every reset in the audit trail with ticket number and verification method.