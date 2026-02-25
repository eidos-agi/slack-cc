---
name: hubspot-explore
description: "Explore HubSpot CRM data using the hs-api.sh wrapper script. Use when Daniel says 'explore hubspot', 'what's in hubspot', 'hubspot data', or '/hubspot-explore'. Queries contacts, companies, deals, tickets, properties, schemas, and owners via the HubSpot REST API."
---

# HubSpot Explore — CRM Data Explorer

Query HubSpot CRM data using the `hs-api.sh` wrapper script in the data-daemon-testing repo.

## Setup

Two environments exist:
- **Test account (sandbox):** `~/repos-greenmark-waste-solutions/data-daemon-testing/hubspot-testing/`
- **Production:** `~/repos-greenmark-waste-solutions/data-daemon-testing/hubspot/`

Default to the **test account** unless Daniel explicitly says production.

The wrapper script is at `scripts/hs-api.sh` in each folder. Always `cd` to the appropriate folder before running commands.

## Available Commands

Run from the appropriate hubspot folder:

```bash
# Record counts for all standard objects
./scripts/hs-api.sh counts

# List records (default 10, specify limit)
./scripts/hs-api.sh objects contacts 5
./scripts/hs-api.sh objects companies 10
./scripts/hs-api.sh objects deals 10

# Get a single record with all properties
./scripts/hs-api.sh object contacts 439926094546

# List all properties for an object type
./scripts/hs-api.sh properties contacts
./scripts/hs-api.sh properties companies
./scripts/hs-api.sh properties deals

# List all custom object schemas
./scripts/hs-api.sh schemas

# Search with filters (HubSpot filter JSON)
./scripts/hs-api.sh search contacts '{"filterGroups":[{"filters":[{"propertyName":"email","operator":"CONTAINS_TOKEN","value":"hubspot"}]}],"limit":5}'

# List owners/users
./scripts/hs-api.sh owners

# List associations for a record
./scripts/hs-api.sh associations contacts 439926094546

# Count for single object type
./scripts/hs-api.sh count contacts
```

## Token Management

The script reads `hubspot.config.yml` for the access token. Tokens expire every ~30 minutes. If you get a 401 error:

1. Run `npx hs auth` in the folder to refresh
2. Re-run the command

The script attempts auto-refresh on 401 but it may need manual intervention.

## Known Limitations

- **Pipelines endpoint** requires app-level auth (Private App), not user PAK. `pipelines` command will return 403.
- **Bulk exports** not supported — use `limit` parameter for pagination (max 100 per page).
- **Rate limits:** 100 requests per 10 seconds. Don't loop too aggressively.
- **Properties fetch:** The `objects` and `object` commands fetch ALL properties by first querying the property list. This uses 2 API calls per request.

## Common Exploration Tasks

### "What data exists in this account?"
```bash
./scripts/hs-api.sh counts
./scripts/hs-api.sh schemas
./scripts/hs-api.sh owners
```

### "What fields are available for contacts?"
```bash
./scripts/hs-api.sh properties contacts
```

### "Show me sample contact data"
```bash
./scripts/hs-api.sh objects contacts 3
```

### "How is the CRM structured?"
```bash
# Check each object type's properties
for type in contacts companies deals tickets; do
    echo "=== $type ==="
    ./scripts/hs-api.sh properties $type | wc -l
    echo "properties"
done
```

## Key Rules

- **Default to test account** — never hit production without explicit instruction
- **Don't create/modify data** — this skill is read-only exploration
- **Don't log PII** — if showing contact data, be mindful of real names/emails in production
- **Note surprising findings** — empty objects, unexpected custom properties, data quality issues
