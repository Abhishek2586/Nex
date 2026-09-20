# Security Policy

## Prototype Scope
This is a software-in-the-loop research prototype of the NEXORA system, designed for local demonstration and reviewer evaluation on a single machine.

It is **not** designed or hardened for production cloud deployment, internet-facing operation, or multi-tenant medical data handling.

## Reporting a Vulnerability

If you find a security vulnerability, please do not file a public issue. Given the research nature of this prototype, report any critical issues that affect local security (e.g. arbitrary code execution on the local host) to the maintainers directly.

## Known Limitations
* Authentication and tokens in this repository are for local simulation only and are not cryptographically secure against external attackers.
* Federated learning updates do not currently use Secure Aggregation.
* Differential Privacy (`secure_mode=False`) is used for demonstration purposes without cryptographically secure RNG unless otherwise configured.
