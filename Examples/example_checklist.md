---
title: "API Security Review Checklist"
type: checklist
domain: security
level: intermediate
status: active
tags: [security, api, checklist, review, audit]
related:
  - "[[API Design Principles]]"
  - "[[OAuth Implementation Guide]]"
  - "[[Security Best Practices]]"
created: 2026-02-06
updated: 2026-02-06
---

## Purpose

Comprehensive security review checklist for REST APIs before production deployment.

## Authentication & Authorization

### Authentication
- [ ] HTTPS enforced for all endpoints
- [ ] Strong authentication mechanism implemented (OAuth 2.0, JWT, API keys)
- [ ] Credentials never transmitted in URL parameters
- [ ] Session tokens are cryptographically strong (min 128-bit)
- [ ] Token expiration implemented (access tokens: 15-60 min)
- [ ] Refresh token rotation enabled
- [ ] Multi-factor authentication available for sensitive operations

### Authorization
- [ ] Principle of least privilege enforced
- [ ] Role-based access control (RBAC) implemented
- [ ] Resource-level permissions validated
- [ ] User can only access own resources
- [ ] Admin endpoints require elevated privileges
- [ ] Authorization checked on every request (no client-side only checks)

## Input Validation

- [ ] All input validated against whitelist
- [ ] Input length limits enforced
- [ ] Special characters escaped/sanitized
- [ ] SQL injection prevention (parameterized queries)
- [ ] NoSQL injection prevention
- [ ] XML/JSON parsing limits configured
- [ ] File upload restrictions (type, size, content validation)
- [ ] Command injection prevented

## Data Protection

### In Transit
- [ ] TLS 1.2+ enforced (TLS 1.3 preferred)
- [ ] Strong cipher suites configured
- [ ] Certificate pinning implemented (mobile apps)
- [ ] HTTP Strict Transport Security (HSTS) enabled

### At Rest
- [ ] Sensitive data encrypted (passwords, PII, payment info)
- [ ] Encryption keys properly managed (key rotation, HSM)
- [ ] Database encryption enabled
- [ ] Backups encrypted

### Data Exposure
- [ ] Sensitive data not logged
- [ ] Error messages don't reveal system details
- [ ] Stack traces disabled in production
- [ ] No credentials in source code or config files
- [ ] API responses don't include unnecessary data

## Rate Limiting & DoS Protection

- [ ] Rate limiting implemented per endpoint
- [ ] Rate limits appropriate for use case
- [ ] Distributed rate limiting for multi-server deployments
- [ ] 429 status code returned when limit exceeded
- [ ] Retry-After header included in rate limit responses
- [ ] Request size limits enforced
- [ ] Timeout values configured properly
- [ ] Circuit breaker pattern implemented for external dependencies

## API Design Security

### Endpoints
- [ ] No debug/admin endpoints in production
- [ ] HTTP methods properly restricted (GET not mutating data)
- [ ] Idempotency implemented for non-safe methods
- [ ] Versioning strategy in place
- [ ] Deprecated endpoints clearly marked

### Response Headers
- [ ] Content-Type header correctly set
- [ ] X-Content-Type-Options: nosniff
- [ ] X-Frame-Options: DENY or SAMEORIGIN
- [ ] Content-Security-Policy configured
- [ ] X-XSS-Protection enabled

## Error Handling

- [ ] Generic error messages for authentication failures
- [ ] Consistent error response format
- [ ] Error codes don't reveal sensitive information
- [ ] Detailed errors logged server-side only
- [ ] No stack traces or internal paths exposed

## Logging & Monitoring

### Logging
- [ ] Security events logged (auth failures, access violations)
- [ ] Logs don't contain sensitive data (passwords, tokens, PII)
- [ ] Log integrity protected (tampering prevention)
- [ ] Centralized logging configured
- [ ] Log retention policy defined

### Monitoring
- [ ] Unusual traffic patterns detected
- [ ] Failed authentication attempts monitored
- [ ] Rate limit violations tracked
- [ ] Performance metrics collected
- [ ] Security alerts configured

## Third-Party Dependencies

- [ ] All dependencies up to date
- [ ] Known vulnerabilities scanned (OWASP Dependency-Check, Snyk)
- [ ] Minimal dependencies principle followed
- [ ] License compliance verified
- [ ] Supply chain security considered

## CORS & Cross-Origin

- [ ] CORS policy configured (not wildcard * in production)
- [ ] Allowed origins whitelisted
- [ ] Credentials properly handled
- [ ] Preflight requests handled correctly

## API Documentation

- [ ] Security requirements documented
- [ ] Authentication flow documented
- [ ] Rate limits documented
- [ ] Error codes documented
- [ ] Security contacts provided

## Compliance & Privacy

- [ ] GDPR compliance verified (if applicable)
- [ ] Data retention policies implemented
- [ ] Right to deletion supported
- [ ] Privacy policy accessible
- [ ] Terms of service accepted
- [ ] Audit logs maintained

## Infrastructure Security

- [ ] WAF (Web Application Firewall) configured
- [ ] DDoS protection enabled
- [ ] Network segmentation implemented
- [ ] Least privilege for service accounts
- [ ] Secrets management solution used (Vault, AWS Secrets Manager)
- [ ] Regular security updates applied

## Testing

- [ ] Security unit tests written
- [ ] Integration tests include security scenarios
- [ ] Penetration testing completed
- [ ] OWASP Top 10 vulnerabilities tested
- [ ] Automated security scanning in CI/CD
- [ ] Manual code review performed

## Incident Response

- [ ] Incident response plan documented
- [ ] Security contacts defined
- [ ] Breach notification procedures established
- [ ] Rollback procedures tested
- [ ] Post-incident review process defined

## Pre-Production Final Checks

- [ ] All items above verified
- [ ] Security review approved by security team
- [ ] Penetration test report reviewed
- [ ] Production credentials rotated
- [ ] Monitoring and alerting tested
- [ ] Incident response team briefed
- [ ] Documentation complete and accessible

## Sign-Off

**Reviewed by:** _______________  
**Date:** _______________  
**Approved for Production:** [ ] Yes [ ] No  
**Notes:** _______________
