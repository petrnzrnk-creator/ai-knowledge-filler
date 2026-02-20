---
title: "Python Production Deployment Security Checklist"
type: checklist
domain: security
level: intermediate
status: active
tags: [security, python, deployment, production, checklist, devops]
related:
  - "[[API Security Review Checklist]]"
  - "[[DevOps Security Best Practices]]"
  - "[[Python Code Quality]]"
created: 2026-02-19
updated: 2026-02-19
---

## Purpose

Security verification checklist before deploying a Python application to production.

## Code Quality

- [ ] Pylint / flake8 passing — no critical errors
- [ ] Type hints validated with `mypy --strict`
- [ ] `pip audit` run — no known CVEs in dependencies
- [ ] All dependencies pinned to exact versions in `requirements.txt`
- [ ] No `# noqa` suppressions without documented reason

## Secrets & Configuration

- [ ] No credentials or API keys in source code or git history
- [ ] All secrets loaded from environment variables
- [ ] `.env` files excluded in `.gitignore`
- [ ] Production secrets stored in vault (AWS Secrets Manager, HashiCorp Vault, etc.)
- [ ] Secrets rotation schedule defined

## Authentication & Authorization

- [ ] All endpoints require authentication
- [ ] JWT tokens have expiration set (≤ 60 min)
- [ ] Refresh token rotation enabled
- [ ] Role-based access control (RBAC) enforced
- [ ] Admin endpoints require elevated privileges

## Infrastructure

- [ ] HTTPS enforced — TLS 1.2+ only
- [ ] HSTS header enabled
- [ ] Firewall rules restrict unnecessary ports
- [ ] SSH access limited to key-based auth only
- [ ] Database not exposed to public internet

## Logging & Monitoring

- [ ] Security events logged (auth failures, permission denials)
- [ ] Logs do not contain passwords, tokens, or PII
- [ ] Centralized log aggregation configured
- [ ] Alerting on anomalous patterns (e.g. repeated 401s)

## Sign-Off

**Reviewed by:** _______________
**Date:** _______________
**Approved:** [ ] Yes  [ ] No — **Blockers:** _______________
