# Financial Terms

Accounting and finance vocabulary used by Alex Kaye and in Sage Intacct context. Fireflies may mangle these or run them together.

## Sage Intacct Terms

| Term | What it means | Context |
|------|-------------|---------|
| GL | General Ledger — the master accounting record | Alex has a "detailed financial model down to the GL level" |
| Journal entry | A record of a financial transaction in the GL | Cerebro reads journal entries but NEVER creates them |
| AP | Accounts Payable — money owed to vendors | ap_bills in the bronze schema |
| AR | Accounts Receivable — money owed by customers | ar_invoices in the bronze schema |
| Chart of accounts | The organized list of all GL accounts | Hierarchical structure in Sage |
| Cost allocation | Assigning costs to business lines and departments | Alex's invoice processing workflow |
| Entity-level | Per business unit (NTX, Hometown, Memphis) | Financial reporting is entity-level |

## Business Metrics Terms

| Term | What it means | Context |
|------|-------------|---------|
| COGS | Cost of Goods Sold | Tracked in monthly metrics dashboard |
| SGA | Selling, General & Administrative expenses | Tracked alongside COGS |
| LOB | Line of Business | Greenmark has multiple LOBs per entity |
| Revenue per truck | Revenue divided by active truck count | Key operational efficiency metric |
| Revenue per driver hour | Revenue divided by productive driver hours | Key labor efficiency metric |
| Productive hours | Driver hours actually working (vs. total payroll hours) | Productivity % = productive / total |
| De minimis | Negligible cost — not worth worrying about | Alex used this re: Sage seat cost |

## Concepts

### System of record
Sage Intacct is the system of record. All financial truth flows from Sage. Cerebro reads from it but never writes. Daniel: "Your auditors will love it."

### Human-in-the-loop
No agentic AI writes to financial systems. AI can prepare journal entries, but a human must click approve. Daniel: "There is no test for 'you sent the email to the wrong client.'"

### Flow through Sage
Alex's preference: data from other systems (Expensify, potentially Comerica) should flow through Sage rather than directly into the warehouse. "If Sage can be our Rosetta Stone for most things, I'd rather just flow it through Sage."
