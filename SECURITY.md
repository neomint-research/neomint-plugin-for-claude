# Security policy

## Supported versions

Security fixes are applied to the most recent published version of the toolkit. If a vulnerability is confirmed in an older version, the fix lands on the current version; we do not backport. The version in use is visible in `.claude-plugin/plugin.json` and at the top of `README.md`.

## Reporting a vulnerability

Please report security issues privately to **info@neomint.com** rather than opening a public issue. (We do not maintain a dedicated security alias; the general mailbox is monitored and security reports are triaged from there.)

Include:

- the affected skill or plugin component,
- the version from `plugin.json`,
- the smallest reproduction you can produce,
- the impact you believe it has,
- any suggested mitigation.

We will acknowledge the report within five working days and aim to publish a fix or a mitigating change within thirty days of the acknowledgement. If the issue is complex and that timeline slips, we will tell you and give a revised date.

## Scope

In scope:

- any skill in the plugin misbehaving in a way that leaks user data, executes unexpected actions, or bypasses stated safety rules;
- the governance skill allowing a quality check to be silently skipped;
- the plugin's build tooling (`plugin-check.py`, per-skill graders) producing a false `PASS` for a genuinely broken plugin.

Out of scope:

- vulnerabilities in Claude, Claude Code, Cowork, or any Anthropic-provided tooling — please report those to Anthropic directly;
- vulnerabilities in third-party MCP servers or connectors the user has installed alongside this plugin;
- social-engineering paths that require convincing a user to install a modified plugin file.

## What counts as a vulnerability here

A skill's trigger phrases being too aggressive, or a grader being too strict, are quality issues rather than vulnerabilities. Please open a regular GitHub issue for those. A skill processing user data in a way that exposes it unintentionally — for example, writing filenames to a shared location without the user asking — is a vulnerability.

## Disclosure

We credit reporters by name (or a pseudonym, if preferred) in the `CHANGELOG.md` entry for the fix unless you ask us not to.
