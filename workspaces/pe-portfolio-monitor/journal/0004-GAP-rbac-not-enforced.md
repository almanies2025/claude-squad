---
type: GAP
date: 2026-04-20
created_at: 2026-04-20T00:00:00Z
author: agent
session_id: redteam-round-1
session_turn: 1
project: pe-portfolio-monitor
topic: RBAC role guards missing from all API endpoints
phase: redteam
tags: [security, rbac, api, authentication]
---

## Summary

The `UserRole` enum defined 6 roles (`pe_admin`, `pe_partner`, `pe_operator`, `pe_ops`, `portco_admin`, `portco_viewer`) but **no API endpoint enforced any role check**. Any authenticated user within a firm could create companies, delete companies, acknowledge alerts, or trigger alert evaluations — regardless of their role.

## Root Cause

Role definitions existed in the schema (`models.py`) but no authorization middleware or dependency existed to enforce them at the route level.

## Fix Applied

Added `require_role(allowed_roles: list[str])` dependency in `app/dependencies.py`. Protected:

- `POST /companies` → `["pe_admin", "pe_ops"]`
- `DELETE /companies/{id}` → `["pe_admin"]`
- `PATCH /alerts/{id}` → `["pe_admin", "pe_ops", "pe_operator", "pe_partner"]`
- `POST /alerts/evaluate` → `["pe_admin", "pe_ops", "pe_operator", "pe_partner"]`

## For Discussion

1. Should `PATCH /companies/{id}` (update company details) also require a role guard, or is any authenticated firm user allowed to update company metadata?
2. The `portco_admin` and `portco_viewer` roles are for portfolio company users — do their permissions need to be enforced on API endpoints, or are they excluded from the API entirely for v1?
3. Should `POST /companies/{id}/upload-csv` have a role guard, or is any authenticated user allowed to upload financial data?
