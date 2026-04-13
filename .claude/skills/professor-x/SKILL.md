---
name: professor-x
description: "Test and improve Cerebro's FAQ coverage through adversarial generations."
---

# /professor-x — Self-Improving Adversarial Training Loop

## When to Use
Run to test and improve Cerebro's FAQ coverage. Each run is a **generation** — Professor X gets smarter at finding weaknesses, Cerebro gets better at answering. Both sides ratchet up over time.

Triggers: `/professor-x`, `run professor x`, `train cerebro`, `drill cerebro`

## What It Produces
A generation report showing:
- Pre-drill analysis (what we learned from past generations)
- Questions asked and grades received
- Gaps identified and fixes applied
- Verification results
- Generation-over-generation delta

## Constants

```
BOTFARM=~/repos-greenmark-waste-solutions/cerebro-bot-farm
TRAINING_CHANNEL=C0AJUGXR6Q5
CEREBRO_USER_ID=U0AEPQFQ24V
DB_CONN="postgresql://postgres.wwmcgtyngnziepeynccz:Fdhu913h4ufiohu98op3ghu9orghte3uqpofhgu9@aws-1-us-east-1.pooler.supabase.com:6543/postgres"
SUPABASE_URL=https://wwmcgtyngnziepeynccz.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind3bWNndHluZ256aWVwZXluY2N6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDk1ODM0MiwiZXhwIjoyMDg2NTM0MzQyfQ.S0z5blR6Z5OmsrSVaj3hjMm7ueaenqiXVD7E1kkgtUc
AI_SERVICES_URL=https://cerebro-ai-services-production.up.railway.app
AI_SERVICES_KEY=sk-gm-bot-farm-f8f383c56d2d9b9b428eed1b68775cbf
```

## Execution Steps

### Stage 0 — Intelligence Gathering

**0a. Get current generation number:**
```sql
SELECT COALESCE(MAX(generation), 0) AS last_gen
FROM cerebro_px_evolution WHERE deleted_at IS NULL;
```
New generation = last_gen + 1.

**0b. Analyze past performance (skip if generation 1):**
```sql
-- What's been mastered? (A grade 3+ times, never C/D/F recently)
SELECT question, COUNT(*) AS a_count
FROM cerebro_px_log
WHERE grade = 'A' AND deleted_at IS NULL
GROUP BY question
HAVING COUNT(*) >= 3
  AND question NOT IN (
    SELECT question FROM cerebro_px_log
    WHERE grade IN ('C', 'D', 'F')
      AND created_at > NOW() - INTERVAL '7 days'
      AND deleted_at IS NULL
  );
```
Mark these as mastered: `UPDATE cerebro_px_log SET mastered = TRUE WHERE question IN (...)`.

**0c. Find weak areas:**
```sql
-- Questions that improved but stalled (went from F/D to C but never hit A/B)
SELECT question, MAX(score) AS best_score, MAX(grade) AS best_grade
FROM cerebro_px_log
WHERE deleted_at IS NULL AND mastered = FALSE
GROUP BY question
HAVING MAX(grade) IN ('C', 'D')
ORDER BY MAX(score) ASC;
```

**0d. Mine real user gaps:**
```sql
-- Real user questions from cerebro_chat_log that got low confidence
SELECT question, confidence, intent, tool
FROM cerebro_chat_log
WHERE deleted_at IS NULL
  AND confidence < 0.6
  AND intent = 'faq'
  AND created_at > NOW() - INTERVAL '14 days'
ORDER BY confidence ASC
LIMIT 10;
```

**0e. Identify weak knowledge tags:**
```sql
-- Tags with the worst average scores
SELECT unnest(
    (SELECT tags FROM cerebro_faq WHERE id = (
        SELECT faq_id FROM cerebro_px_log WHERE question = p.question AND faq_id IS NOT NULL LIMIT 1
    ))
) AS tag, AVG(score) AS avg_score
FROM cerebro_px_log p
WHERE deleted_at IS NULL AND grade IN ('C', 'D', 'F')
GROUP BY tag
ORDER BY avg_score ASC;
```

If this query is too complex, simplify: look at which question TOPICS (sales metrics, ops, finance) tend to score lowest.

### Stage 1 — Plan the Drill

Based on Stage 0 intelligence, build the question list:

| Source | Count | Priority |
|--------|-------|----------|
| Stalled questions (C grade, never A) | up to 3 | Highest — these are the improvement targets |
| Real user gaps (low confidence from chat_log) | up to 3 | High — real users hit these |
| AI-generated novel questions | 2-4 | Medium — push the boundary |
| Static bank (untested questions) | remainder | Fill to target count |
| Mastered questions | 0 | SKIP — retired |

**AI-generated questions:** Call cerebro-ai-services to generate novel questions:
```bash
curl -s -X POST "$AI_SERVICES_URL/v1/chat" \
  -H "Authorization: Bearer $AI_SERVICES_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "anthropic/claude-haiku-4.5",
    "messages": [{"role": "user", "content": "PROMPT_BELOW"}],
    "max_tokens": 500
  }'
```

Prompt for novel question generation:
```
You are generating adversarial test questions for a business intelligence bot called Cerebro.
Cerebro serves Greenmark Waste Solutions — a commercial waste collection company in Dallas-Fort Worth.

Data sources available:
- HubSpot CRM: contacts, companies, deals, owners
- Sage Intacct: AR invoices, AP bills, GL accounts, vendors
- Fleetio: vehicles, fuel logs, maintenance orders, inspections

Weak areas from past tests: {weak_tags}
Questions that stalled at C grade: {stalled_questions}

Generate 4 challenging questions that:
1. Combine data from multiple sources (e.g., "Which customers with the most deals also have overdue invoices?")
2. Ask about trends over time (e.g., "What's our 3-month pipeline trend?")
3. Require calculations not directly in the data (e.g., "What's our customer lifetime value?")
4. Challenge with executive-level phrasing (e.g., "Give me a revenue health check")

Return ONLY the questions, one per line, no numbering.
```

### Stage 2 — Run the Drill

Get the Professor X token:
```bash
# Use railguey_variables for cerebro-bot-farm → PROFESSOR_X_SLACK_BOT_TOKEN
```

Run the drill:
```bash
cd $BOTFARM && PROFESSOR_X_SLACK_BOT_TOKEN="<token>" python -m botfarm.professor_x_bot \
  --question "first question" --delay 5
```
Run each question individually (since the list is custom-built, not from the static bank).

Wait 20 seconds for Cerebro to process all questions.

### Stage 3 — Collect Results

```sql
SELECT question, grade, score, has_sql, suggestion, suggestion_type
FROM cerebro_px_log
WHERE deleted_at IS NULL
  AND created_at > NOW() - INTERVAL '5 minutes'
ORDER BY created_at DESC;
```

Stamp all results with the generation number:
```sql
UPDATE cerebro_px_log SET generation = <N>
WHERE deleted_at IS NULL AND generation IS NULL
  AND created_at > NOW() - INTERVAL '5 minutes';
```

### Stage 4 — Fix Gaps

For each C/D/F grade, apply the fix:

**ADD_FAQ (D/F grade — no coverage):**
Write a new FAQ entry to Supabase REST API:
```
POST $SUPABASE_URL/rest/v1/cerebro_faq
Headers: apikey: $SUPABASE_KEY, Authorization: Bearer $SUPABASE_KEY, Content-Type: application/json, Prefer: return=representation
Body: {
  "question": "<the question>",
  "answer": "<generated answer based on Greenmark context>",
  "tags": ["<appropriate tags>"],
  "aliases": [],
  "sql_query": "<SQL if data question, NULL otherwise>",
  "sql_format": "<format string or 'table'>",
  "sql_name": "<identifier>",
  "source": "professor_x"
}
```

**ADD_SQL (B grade — matched but no live data):**
Write a SQL query for the matched FAQ entry:
```
PATCH $SUPABASE_URL/rest/v1/cerebro_faq?question=eq.<url_encoded_matched_question>&deleted_at=is.null
Headers: same as above
Body: {"sql_query": "<SQL>", "sql_format": "<format>", "sql_name": "<name>"}
```

**ADD_ALIAS (C grade — close but phrased differently):**
Append the question as an alias:
```sql
UPDATE cerebro_faq
SET aliases = array_append(aliases, '<the question text>')
WHERE question = '<matched question>'
  AND deleted_at IS NULL;
```

**Schema reference for SQL queries:**
```
hubspot_bronze.deals: source_id, entity, dealname, pipeline, dealstage, amount,
  closedate, createdate, hs_lastmodifieddate, dealtype, closed_won_reason,
  closed_lost_reason, hs_is_closed_won, hs_forecast_amount, hubspot_owner_id

hubspot_bronze.companies: source_id, entity, name, domain, phone, industry,
  city, state, country, annualrevenue, numberofemployees, lifecyclestage,
  hubspot_owner_id, createdate

hubspot_bronze.contacts: source_id, entity, email, firstname, lastname,
  phone, jobtitle, lifecyclestage, hs_lead_status, hubspot_owner_id, createdate

hubspot_bronze.owners: source_id, email, firstname, lastname, user_id

sage_bronze.ar_invoices: source_id, entity, customer_id, customer_name,
  invoice_date, due_date, total_amount, status

All tables: deleted_at IS NULL required. Dates are TEXT columns — cast as needed.
```

### Stage 5 — Verify Fixes

Wait 5 seconds for FAQ engine hot-reload.

Re-run ONLY the questions that got C/D/F grades:
```bash
cd $BOTFARM && PROFESSOR_X_SLACK_BOT_TOKEN="<token>" python -m botfarm.professor_x_bot \
  --question "<failed question>" --delay 5
```

Collect new grades. Stamp with same generation number.

### Stage 6 — Record Generation

Write the generation summary:
```sql
INSERT INTO cerebro_px_evolution
  (generation, avg_score, grade_dist, questions_tested, questions_retired,
   novel_generated, fixes_applied, weak_tags, notes)
VALUES (
  <N>,
  <avg_score>,
  '{"A": X, "B": X, "C": X, "D": X, "F": X}'::jsonb,
  <count>,
  <retired_count>,
  <novel_count>,
  <fixes_count>,
  ARRAY[<weak_tags>],
  '<summary notes>'
);
```

### Stage 7 — Report

Print terminal report:

```
═══ Professor X — Generation <N> ═══

  Intelligence:
    Mastered (retired): <N> questions
    Stalled at C: <N> questions
    Real user gaps found: <N>
    Novel questions generated: <N>

  BEFORE                    AFTER
  ──────                    ─────
  A: X  B: X  C: X  D: X  F: X    A: X  B: X  C: X  D: X  F: X
  Avg: XX%                  Avg: XX%

  Fixes applied: <N>
  ├─ ADD_FAQ: "<question>"
  ├─ ADD_SQL: "<question>" → <query_name>
  └─ ADD_ALIAS: "<phrase>" → "<existing question>"

  Still weak (needs human review):
  └─ "<question>" (C, XX%)

  Generation delta: +XX points
  All-time trend: Gen 1: 68% → Gen 2: 82% → Gen 3: 91%

  Next generation targets:
  └─ <what to focus on next time>
```

Save to `reports/professor-x/gen-<N>-<date>.md`.

## Options

| Arg | Default | What |
|-----|---------|------|
| (none) | 10 questions, auto-planned | Full self-improving drill |
| `hard` | Focus on hard + novel questions | Push the boundary |
| `verify-only` | Re-test last generation's failures | Quick follow-up |
| `report` | Show evolution history, no drill | Status check |
| `N` (number) | Custom question count | Scale up/down |

## The Self-Improvement Loop

```
Generation 1: Static bank → 68% avg → 5 fixes applied
Generation 2: Re-test fixes + mine user gaps + 2 novel → 82%
Generation 3: Retire 8 mastered, 4 novel cross-domain → 79% (harder questions!)
Generation 4: Fix stalled C's, 3 more novel → 88%
Generation N: Avg score climbs, question difficulty climbs, both sides improve
```

Professor X gets smarter by:
- Studying past px_log (don't re-ask mastered questions)
- Mining real user questions from chat_log
- Using AI to generate novel cross-domain questions
- Targeting specifically the weakest knowledge areas
- Increasing difficulty as Cerebro improves

Cerebro gets smarter by:
- Auto-added FAQ entries from Professor X fixes
- SQL queries written for text-only answers
- Aliases added for alternative phrasings
- All improvements are instant (database-backed, no redeploy)

## Rules
- NEVER hard-delete — soft deletes only (deleted_at)
- ALWAYS include `WHERE deleted_at IS NULL` in queries
- SQL format: Python str.format (`{col}`, `{col:,.0f}`) or `'table'` for multi-row
- Source = `'professor_x'` for auto-generated entries
- Tag with domain tags: sales, finance, ops, engineering, health, general
- If AI services are down, fall back to static question bank
- Don't generate SQL for questions that can't be answered with available schema
