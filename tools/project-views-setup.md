# Cerebro Engineering Project — View Setup

> Paste this into a Claude session with the GitHub MCP connected, or follow manually.

## Project URL

https://github.com/orgs/greenmark-waste-solutions/projects/1

## Views to Create

### 1. Active PRs

- **Type:** Table
- **Filter:** `is:pr is:open`
- **Columns:** Repository, Title, Status, Linked pull requests
- **Purpose:** Daily check — what's ready to merge?

### 2. Sage Roadmap

- **Type:** Roadmap
- **Date fields:** Start Date / Target Date
- **Filter:** items with "M-0" in title
- **Purpose:** Gantt view of Sage pipeline milestones (M-01 through M-07)

### 3. Needs Attention

- **Type:** Table
- **Filter:** `is:open`
- **Sort:** Updated, ascending (stalest first)
- **Columns:** Repository, Title, Status, Updated
- **Purpose:** What's going stale? What needs a push?

## Category Field

Add a single-select field called **Category** with these options:

| Option | Color | What gets tagged |
|--------|-------|-----------------|
| **PR** | Blue | Items that are pull requests |
| **Milestone** | Purple | Items with "M-0" in title |
| **Task** | Green | Sub-issues of milestones |
| **Infrastructure** | Gray | Release practices, CI, tooling |

## How to Create Views (Browser Only)

1. Open the project URL above
2. Click the **+ New view** tab at the top right
3. Select the view type (Table or Roadmap)
4. Name it
5. Add filters using the filter bar
6. Drag columns to reorder

## How to Add the Category Field

1. Click **+** at the end of the column headers
2. Select **New field**
3. Name: `Category`
4. Type: Single select
5. Add options: PR, Milestone, Task, Infrastructure
6. Tag each item by clicking its Category cell
