# Security Policy

This repository contains public civic data — state, county, and other
division records — and the Python tooling to validate it. There is no
user-facing application, network service, or authentication system here.
The practical security surface is small.

## Reporting

If you discover a security issue — for example, a YAML file containing
accidentally committed secrets or credentials, a malicious URL in a
`sources:` entry, or a dependency vulnerability — please:

- For anything sensitive, use [GitHub's private vulnerability reporting](https://github.com/VoterBloc/divisions/security/advisories/new).
- For everything else, open a regular issue.

Thanks for helping keep the dataset trustworthy.
