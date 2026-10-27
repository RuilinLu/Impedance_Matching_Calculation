# Security Policy

**Project:** Impedance Matching AI
**Version:** 4.4.0
**Contacts:** GitHub Issues ｜ GitHub Security Advisory（私密披露）

## Supported versions

| Version | Supported |
|---|---|
| 4.4.x | Yes |
| 4.3.x | Yes (data-compatible) |
| 4.2.x | Security fixes only |
| 4.1.x | No |
| 4.0.x | No |

## Reporting a vulnerability

Please open a private GitHub Security Advisory (or, for non-sensitive reports, a
GitHub Issue) at <https://github.com/SkywalkerHolmes/Impedance_Matching_Calculation> with:

- affected version and file hash;
- reproduction steps;
- impact assessment;
- whether the issue is in the Python engine, MCP server, textbook library, documentation hub, attachment handling or the desktop shell.

Please do not open a public issue for an unpatched vulnerability.

## Local-only design

- The web UI and MCP HTTP server bind to `127.0.0.1` only.
- The MCP server validates browser `Origin` and rejects non-local origins.
- Outbound model requests, catalog updates and announcement fetches accept only
  `http`/`https` public hosts; localhost, loopback, private, link-local,
  multicast and reserved addresses are rejected before the request.
- API keys are stored locally in `data/config.json`
  (`%LOCALAPPDATA%\ImpedanceMatchingAI\data` for the frozen app) and are never
  committed to this repository or written to logs.
- Attachments are limited to 60 MB; textbook uploads to 120 MB; they stay in the
  local data directory. Textbooks are never uploaded to any provider.
- No telemetry, analytics, or automatic upload of designs is implemented.
- The desktop UI runs in a native WebView2 window; no external browser is
  launched and no console window is shown.
- The uninstaller stops running instances, then asks whether to keep personal
  data. Keeping it preserves API keys, settings, textbook index, uploads,
  reports, translation cache and search paths for the next install; deleting it
  removes the local data tree. In both modes it removes matching MCP client
  entries, shortcuts and app-specific registry keys. Shared Microsoft WebView2
  Runtime is not removed.
- The optional update checker contacts `api.github.com` only, validates the
  scheme, host and resolved public IP, follows redirects only to allow-listed
  GitHub hosts, and downloads installers to a fixed path inside the local data
  directory. The configured model may receive public release notes for a
  compatibility summary; no personal data is sent.

## Model catalog updates

Catalog updates read `models.dev`, the current provider's `/models` endpoint
(with the user's key) and public model/pricing pages. Updates are written to a
user-side override file; every update is backed up and can be rolled back.

## Code signing and antivirus

The release binaries are built reproducibly but are **not signed** unless a
maintainer supplies an Authenticode certificate. A license (MIT) does not
prevent antivirus false positives. Every release includes `SHA256SUMS.txt`;
verify downloaded files before running them.

## Third-party data

The built-in provider catalog contains public endpoint URLs, model IDs,
capabilities and reference prices only; no credentials are included. The
optional catalog refresh uses the open-source models.dev registry.
