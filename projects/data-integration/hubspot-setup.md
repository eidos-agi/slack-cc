# HubSpot API Access Setup

**Status:** Waiting on Michael
**Goal:** Enable read-only CRM access so Daniel can explore HubSpot data for the Cerebro dashboard
**Account:** Greenmark Waste Solutions (ID 244562652)

---

## What's Done

- [x] Daniel logged into HubSpot Developer Portal
- [x] HubSpot CLI installed and authenticated (Personal Access Key)
- [x] Security review completed — read-only access only, no write scopes

## What's Needed

Daniel's HubSpot user currently has only developer-level permissions. The CRM data scopes (contacts, companies, deals, etc.) are locked and Daniel cannot enable them himself. A **Super Admin** needs to update Daniel's user permissions in HubSpot.

## What Michael Needs to Do

**Time required:** ~5 minutes

Michael — the steps below will give Daniel read-only access to CRM data through the API. This does NOT give write access. Daniel will be able to look at data but not change anything in HubSpot.

> **Tip:** If you have Claude in your browser sidebar, you can open it and say: *"Watch my screen. I need to follow these steps to give a user read-only CRM API access in HubSpot. Guide me through it and stop me if I'm about to do something wrong."*

### Steps

1. **Go to HubSpot Settings**
   - Log in at [app.hubspot.com](https://app.hubspot.com)
   - Click the **gear icon** (Settings) in the top navigation bar

2. **Find Daniel's user**
   - In the left sidebar, click **Users & Teams**
   - Find the user associated with `it@greenmarkwaste.com` (this is Daniel's current login)

3. **Edit permissions**
   - Click on the user to open their profile
   - Go to the **Permissions** tab (or click "Edit permissions")

4. **Enable CRM read access**
   - Look for the **CRM** section
   - Enable **read** access for:
     - Contacts
     - Companies
     - Deals
     - Tickets
   - **Do NOT enable write, edit, or delete** for any of these. Read only.

5. **Enable Custom Objects read access** (if visible)
   - Same section, look for **Custom Objects**
   - Enable **read** access only

6. **Save**
   - Click Save / Apply at the bottom

### What NOT to do

- **Do not grant write access** to any CRM objects — Daniel's role is read-only for dashboards
- **Do not change permissions for other users** — only the `it@greenmarkwaste.com` user
- **Do not delete or deactivate any existing users or settings**

If anything looks confusing or different from what's described above, stop and message Daniel. The screen may look slightly different depending on HubSpot's plan tier.

---

## After Michael Completes This

Daniel will:
1. Regenerate his Personal Access Key with the new CRM scopes
2. Update the HubSpot CLI authentication
3. Begin exploring real CRM data for the Cerebro dashboard

---

## Email to Michael

Copy and send from Daniel's email:

---

**To:** mnguyen@greenmarkwaste.com
**Subject:** Quick HubSpot permissions update (~5 min)

Michael,

I've got the HubSpot CLI set up and authenticated for the Cerebro data work. One thing I need from you — my user account doesn't have CRM data permissions yet, and only a Super Admin can enable them.

**What I need:** Read-only access to CRM objects (Contacts, Companies, Deals, Tickets) for the `it@greenmarkwaste.com` user.

**What this does:** Lets me pull data into the dashboard. I can look but not touch — no ability to edit, delete, or modify anything in HubSpot.

**How to do it:** I put step-by-step instructions here:
[hubspot-setup.md on GitHub](https://github.com/greenmark-waste-solutions/greenmark-planning/blob/main/projects/data-integration/hubspot-setup.md)

It's about 5 minutes. If you have Claude in your browser sidebar, you can have it watch your screen and walk you through it — just tell it "help me follow these steps and make sure I only enable read access."

No rush — whenever you have a few minutes this week.

Thanks,
Daniel
