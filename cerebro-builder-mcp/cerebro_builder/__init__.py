"""cerebro-builder — the mayor.

Holds the mission. Knows the topology. Delegates to child MCPs.
Checks alignment. Calls Rhea at decision points. Reports to stakeholders.

Children:
  cerebro-github  — PR ceremony (issues, PRs, CI, merge)
  railguey        — Railway deploys (status, logs, redeploy)
  cerebro-vault   — Supabase secrets
  wrike           — Stakeholder visibility
  rhea            — Adversarial reasoning at decision points

The mayor doesn't do the work. The mayor ensures the work serves the mission.
"""
