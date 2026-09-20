# Repository Analysis and Integration Setup

## Repository analysis summary

`Radioactive_Foot_pi` currently contains:
- Python-focused project areas in `/common` and `/dark-cocoa-dc`
- Protobuf schemas in `/schemas`
- GitHub Pages static documentation in `/docs`
- Existing baseline automation:
  - `.github/workflows/ci.yml` for Python compile checks and protobuf validation
  - `.github/workflows/pages.yml` for docs publishing
  - Issue and pull request templates in `.github/ISSUE_TEMPLATE` and `.github/pull_request_template.md`

## Added integrations

### 1) Copilot cloud-agent environment bootstrap
- Workflow: `.github/workflows/copilot-setup-steps.yml`
- Purpose: deterministic setup of Python + protobuf toolchain and Node.js for MCP/server tooling.

### 2) API connector smoke checks
- Workflow: `.github/workflows/integrations-health.yml`
- Connectors validated:
  - GitHub API
  - GitLab API
  - Gemini API
  - Google Custom Search API
  - Loveable endpoint (when explicitly enabled)
- Trigger: manual (`workflow_dispatch`) and daily schedule.

### 3) Repository automation
- PR auto-labeling:
  - `.github/workflows/pr-labeler.yml`
  - `.github/labeler.yml`
- GitLab main branch sync:
  - `.github/workflows/gitlab-main-sync.yml`

### 4) MCP server configuration
- File: `/.mcp.json`
- Includes MCP server definitions for GitHub, GitLab, Gemini, Google APIs, and Loveable.

### 5) Loveable extension activation
- Activation toggle: repository variable `LOVEABLE_EXTENSION_ENABLED=true`
- Validation path: workflow `integrations-health.yml` checks `${LOVEABLE_API_URL}/health` with `LOVEABLE_API_KEY` and `X-Loveable-Extension: active` only when both `LOVEABLE_EXTENSION_ENABLED=true` and `LOVEABLE_HEALTHCHECK_ENABLED=true`.
- MCP entry: `loveable` server in `.mcp.json`.

## Required repository secrets and variables

### Secrets
- `GH_CONNECTOR_TOKEN`
- `GITLAB_TOKEN`
- `GITLAB_MIRROR_URL`
- `GEMINI_API_KEY`
- `GOOGLE_API_KEY`
- `LOVEABLE_API_KEY`

### Variables
- `GITLAB_BASE_URL` (for example: `https://gitlab.com`)
- `GEMINI_MODEL` (default `gemini-2.5-flash`)
- `GOOGLE_CSE_ID`
- `LOVEABLE_EXTENSION_ENABLED` (`true` to activate)
- `LOVEABLE_HEALTHCHECK_ENABLED` (`true` to enforce endpoint probe)
- `LOVEABLE_API_URL` (Loveable service base URL)

## Webhook and automation guidance

Some integrations (GitHub/GitLab webhooks, external API project bindings) must be configured in provider UIs and cannot be fully created from repository code alone. Recommended production setup:

1. Configure webhook endpoints in GitHub/GitLab for issue and PR events.
2. Store webhook signing secrets in repository secrets.
3. Keep endpoint health checks in `integrations-health.yml` to detect drift.

## Operational notes

- Workflows are safe-by-default and skip external checks when required credentials are missing.
- Loveable checks fail only when Loveable activation is explicitly enabled but configuration is incomplete.
- No credentials are committed to this repository; all secrets are runtime-injected from GitHub Actions settings.
