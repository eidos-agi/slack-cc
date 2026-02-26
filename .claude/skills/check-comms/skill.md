# /check-comms — Query Communications Shadow Copy

## When to Use
During `/takeoff` or on demand. Checks the centralized comms shadow copy for Greenmark-relevant messages.

## What It Does
Queries Daniel's comms.db (maintained by the director cockpit) filtered to Greenmark-relevant senders, domains, and topics. Surfaces new messages, pending responses, and blocker-relevant communications.

## Prerequisites
- Comms database exists at the director cockpit path
- Database has been swept recently (check `last_sweep_at` in stats)

## Configuration

```
COMMS_DB: /Users/dshanklinbv/repos-personal/aic-director-of-ai-cockpit/comms/comms.db
COMMS_CLI: /Users/dshanklinbv/repos-personal/aic-director-of-ai-cockpit/comms/comms.py
```

### Greenmark Scope Filters
- **Domains:** `@greenmarkwaste.com`, `@htdisposal.com`
- **Key people:** Michael Nguyen, Alex Kaye, Lannis Nicholson, Robert Heath
- **Topics:** Sage Intacct, HubSpot, Navusoft, Cerebro, SEO, Fleetio, dashboard, data warehouse
- **Negative filter:** Exclude newsletters, automated notifications, marketing

## Execution Steps

### 1. Check Database Freshness

```bash
python3 $COMMS_CLI stats
```

If `last_sweep_at` for email sources is stale (>24h), note it:
```
COMMS: Shadow copy is N hours stale. Run /sweep-comms in director cockpit to refresh.
```

### 2. Search for Greenmark-Relevant Messages

Run targeted searches for active blockers and priorities:

```bash
# Blocker: Sage credentials from Alex
python3 $COMMS_CLI search "Sage Intacct Alex credentials account" --limit 5

# Blocker: HubSpot access from Michael
python3 $COMMS_CLI search "HubSpot API access Michael" --limit 5

# General Greenmark activity
python3 $COMMS_CLI search "greenmark waste" --limit 10

# SEO / website related
python3 $COMMS_CLI search "Webflow SEO website" --limit 5
```

### 3. Drill Into Relevant Threads

For any search hit that looks relevant, get thread context:
```bash
python3 $COMMS_CLI context <message_id>
```

Then read full bodies if needed:
```bash
python3 $COMMS_CLI read <id1> <id2>
```

### 4. Present Findings

Format output as a concise briefing:

```
COMMS CHECK (shadow copy as of <last_sweep_at>)

  NEW SINCE LAST SESSION
    - <sender>: <subject> (<date>) — <1-line summary>
    - ...

  BLOCKER-RELEVANT
    - Sage access: <status based on email trail>
    - HubSpot access: <status based on email trail>

  ACTION NEEDED
    - <any emails requiring Daniel's response>

  QUIET (no new messages)
    - <topics with no activity since last check>
```

### 5. Integration with /takeoff

When composed by `/takeoff`, the comms check output appears after the four-part briefing:
```
WHERE WE WERE
  ...
WHERE WE ARE
  ...
WHERE WE'RE GOING
  ...
BLOCKERS
  ...

COMMS CHECK
  ...
```

## Notes
- This skill READS ONLY. It never modifies the comms database.
- If comms.db doesn't exist or is empty, say "Comms shadow copy not initialized. Set up in director cockpit."
- The 3-layer query pattern (search → context → read) minimizes token usage.
- Adjust search queries based on current project priorities and active blockers from the takeoff briefing.
