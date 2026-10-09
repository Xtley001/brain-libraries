# Security Policy

Vulnerability disclosure process and supported versions for the `brain-alpha-pipeline` library suite.

## Vulnerability Disclosure

If you identify a security vulnerability, do not open a public issue. Submit a private advisory at:

https://github.com/Xtley001/brain-alpha-pipeline/security/advisories

The maintainers acknowledge receipt within 48 hours and provide remediation status updates.

## Supported Versions

| Version | Status |
|---|---|
| `0.1.x` | Supported |
| `< 0.1` | Unsupported |

## Scope

The security policy covers:
- Python source packages in `brain_libraries/`
- Data store connection string handling and credential masking in `brain_core` and `brain_store`
- Third-party dependency supply chains specified in package manifests

Excludes host environment misconfiguration and custom non-standard plugin code.

## Reporting Guidelines

Include the following in your advisory:
1. Affected library and version.
2. Step-by-step reproduction instructions or proof-of-concept snippet.
3. Impact assessment (credential exposure, arbitrary code execution, denial of service).
4. Proposed patch or mitigation if available.
