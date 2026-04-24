# GitHub App Permissions — cerebro-github-bot

**App ID:** 3479857
**Installation ID:** 126482862
**Rate Limit:** 6,200/hr (REST + GraphQL, independent of Daniel's PAT)

## Required Permissions

When adding a new tool to cerebro-github, check if it needs a permission
not listed here. If so, update the app settings AND this file.

### Repository Permissions

| Permission | Level | Used By |
|------------|-------|---------|
| Actions | Read & Write | rerun_ci, trigger_workflow |
| Checks | Read & Write | check_ci |
| Contents | Read & Write | create_release, merge_pr (branch delete) |
| Issues | Read & Write | create_work, close_work |
| Metadata | Read-only | all tools (implicit) |
| Pull requests | Read & Write | open_pr, merge_pr, check_ci, dashboard |

### Organization Permissions

| Permission | Level | Used By |
|------------|-------|---------|
| Members | Read-only | health_check |
| Projects | Read & Write | create_work (project board linkage) |

## Settings URL

https://github.com/organizations/greenmark-waste-solutions/settings/apps/cerebro-github-bot

## Key Storage

- PEM file: `/home/dev/.claude/cerebro-github-app.pem` (chmod 600)
- Backup: cerebro-vault as `SECRET_CEREBRO_GITHUB_APP_PRIVATE_KEY`
- Defaults hardcoded in `cerebro_github/app_auth.py` (non-secret values only)
