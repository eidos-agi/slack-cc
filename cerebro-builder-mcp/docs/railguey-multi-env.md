---
title: Railguey Multi-Environment Access
tags: [railguey, railway, production, develop, environment, deploy, variables, account]
---

# Railguey Multi-Environment Access

Cerebro runs on Railway with two environments: **develop** (staging) and **production**. Each has its own scoped token. Railguey v0.2.5+ lets you switch between them.

## Setup

Two tokens are registered as railguey accounts:

```
railguey_account_add("develop", "<develop-token>")
railguey_account_add("production", "<production-token>")
```

Tokens live in the cerebro repo:
- `.env.local` / `.env.develop` → develop token (`0b11be0b`)
- `.env.production` → production token (`adefb6b1`)

## Switching environments

```
railguey_account_default("production")   # All tools now hit production
railguey_variable_set(...)               # Sets on PRODUCTION Railway env
railguey_account_default("develop")      # Switch back
```

Account override takes priority over `.env.local`. This is the core use case: briefly operate on production without swapping files.

## When to use

- Setting env vars on production (e.g., `NEXT_PUBLIC_ENV_LABEL=PRODUCTION`)
- Checking production deploy status or logs
- Comparing variables between environments

**Always switch back to develop when done.** Production is the exception, not the default.

## Doctor knows

`railguey_doctor` checks if the account system covers multi-environment gaps. When both accounts are registered, the "Token environment scope" check passes instead of failing.

## What went wrong (Session 28)

Production showed an orange "STAGING" banner because `NEXT_PUBLIC_ENV_LABEL=STAGING` was set on the production Railway environment. The develop-scoped token couldn't access production variables. The fix required:

1. Wiring account system into `_load_token()` (v0.2.5)
2. Using `railguey_account_default("production")` to switch
3. `railguey_variable_set("NEXT_PUBLIC_ENV_LABEL", "PRODUCTION")`
4. Code fix: `EnvBanner` doesn't render when label is "PRODUCTION"

## Environment IDs

- develop: `3c0ca8fb-09e8-4855-a8e5-85dafa935fee`
- production: `4b0c1305-68a4-4fb7-8599-7101dda1f103`
