# Security Policy

**Project:** 智配芯生 · ImpedanceMCP
**Version:** 4.2.0
**Contacts:** radarlurui@gmail.com ｜ Lu_Skywalker2915@sjtu.edu.cn

## Supported versions

| Version | Supported |
|---|---|
| 4.2.x | Yes |
| 4.1.x | Security fixes only |
| 4.0.x | No |
| V3.0 MATLAB App | Classic interface only |

## Reporting a vulnerability

Please email both contacts above with:

- affected version and file hash;
- reproduction steps;
- impact assessment;
- whether the issue is in the Python engine, MCP server, installer, or MATLAB bridge.

Please do not open a public issue for an unpatched vulnerability.

## Local-only design

- The web UI and MCP HTTP server bind to `127.0.0.1` only.
- The MCP server validates browser `Origin` and rejects non-local origins.
- Outbound model requests accept only `http`/`https` public hosts; localhost,
  loopback, private, link-local and reserved addresses are rejected.
- API keys are stored locally in `data/config.json`
  (`%LOCALAPPDATA%\ImpedanceMCP\data` for the installed app) and are never
  committed to this repository.
- Uploaded files are limited to 25 MB and stored under the local data directory.
- No telemetry, analytics, or automatic upload of designs is implemented.
- The installer does not modify PATH, browser settings, or startup entries.

## Code signing and antivirus

The release binaries are built reproducibly but are **not signed** unless a
maintainer supplies an Authenticode certificate. A license (MIT) does not
prevent antivirus false positives. See
`docs/安装与杀毒软件说明.md` for the recommended signing and false-positive
reporting process. Every release includes `SHA256SUMS.txt`; verify downloaded
files before running them.

## Third-party data

The provider catalog is generated from the open-source models.dev registry. It
contains public endpoint URLs and model IDs only; no credentials are included.
