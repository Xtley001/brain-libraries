# Security Policy — brain-decorrelator

## Disclosure

Report vulnerabilities privately to https://github.com/Xtley001/brain-libraries/security/advisories.
Do not open a public issue. We acknowledge receipt within 48 hours.

## Supported Versions

| Version | Status |
|---|---|
| `0.1.x` | Supported |
| `< 0.1` | Unsupported |

## Scope

- Plugin registry execution safety
- AST mutation safety in `axes/universal.py`

Excludes untrusted user-defined axis plugin implementations.
