# Project Cerebro / Greenmark - Kick Off
## Diarized Transcript
**Date:** 2026-02-11, 3:00-4:00 PM CST | **Platform:** Microsoft Teams
**Source:** Fireflies recording (via Collin Bird) — 2 SRT segments merged

---

## Speaker Resolution

| SRT Label | Identified As | Evidence |
|-----------|--------------|----------|
| Speaker 1 | **Daniel Shanklin** (Dir AI & Tech, AIC) | "I'm Daniel, director of AI here at EIC" (seg2 00:04:05) |
| Speaker 2 | **Michael Nguyen** (President, Greenmark) | Organizer per .ics; discusses Greenmark systems, references "our main operating system" |
| Speaker 3 | **Luke Huntley** (Sr AI Engineer, AIC) | "Data center came along with him for the ride... working on Sable and Meridian" (seg2 00:01:33) |
| Speaker 4 | **Lannis Nicholson** (CRO, Greenmark) | "Started my career with waste management... built into something pretty special and sold it" (seg2 00:02:17) |
| Speaker 5 | **Alex Kaye** (CFO, Greenmark) | "this is Alex... background is kind of in the M and A corporate development" (seg2 00:03:10) |

*Note: William Holloway and Collin Bird were optional attendees per .ics. Neither spoke in the recording — likely listening only.*

---

## Transcript

### Introductions [00:00 - 05:00]

**Michael Nguyen:** *(on mute initially, restarts)* I got Lannis sitting here kind of with me, and Alex Kaye also part of the Greenmark team. Daniel, we appreciate you jumping on. I wanted just for you to be able to meet the team real quickly and then kind of hear at a high level what we're looking for. Like I said, a lot of this stuff you can do in your sleep — it's nothing crazy. We're excited to have some of these capabilities. Daniel, do you want to introduce yourself and Luke so that Lannis and Alex can kind of hear about your background?

**Daniel Shanklin:** Sure, no problem. Hi guys, I'm Daniel, director of AI here at AIC. I've known William Holloway for, gosh, almost 20 years — he and I met back in 2007. I worked at Key Investments — I was in back office accounting, then moved to the trading desk. I was there for nine years. Then I switched over to software engineering and AI about six years ago. I've been a data engineer and now an AI engineer for about two or three of the last few years. Luke worked with me at a startup I operated out of Boone, North Carolina. And as I like to say, Collin took pity on us and said come on over and do it for me full time. So here we are. Luke and I moved to the Fort Worth area from North Carolina back in September. We try our best to build tools that will last a long time — we try not to build software. We try to build agentic type systems that withstand the test of time because I feel like software is a depreciating asset, something that loses value over time. So what kind of business process can you build that will be a little more durable? That's kind of how we try to stay down the fairway.

**Luke Huntley:** Thanks, Daniel. I came along with him for the ride and have been working on Sable and Meridian here, which are our dashboards for AIC, for going on nine months now. I enjoy building things, creating and helping automate things with AI.

**Michael Nguyen:** Lannis, Alex, y'all want to introduce yourselves?

**Lannis Nicholson:** First of all, nice to meet you, Daniel. Welcome to the AIC team. I've got about 6 more months with AIC than y'all two do. Started my career with Waste Management, worked for them out of Arkansas and left them. Started my own company with one truck and one container and built it into something pretty special and sold it to a mid-market level waste company. They wanted it more than we did, so went to work for them for about three years. Met Mike and William and Collin along the way probably a couple years ago, got to know them, learned what they were building — something pretty special — and ultimately made the decision to leave that other company and come over to the AIC team, the Greenmark team. So yeah, full steam ahead and we really appreciate you two jumping in and helping us build this platform out.

**Alex Kaye:** Hey guys, this is Alex. I think Luke, I might have met you briefly up at the AIC office in October. Nice to meet you guys. I recently joined the team in early October. My background is in the M&A, corporate development, private equity world. I have a fair amount of experience across different types of companies and industries, but a little bit of operational experience in business services and skilled labor type business service companies. I've known Michael for over 15 years — him and I started at Houlihan Lokey back in the day. Super excited to be on the Greenmark team, believing in our story and our growth potential. Happy to be working with everybody. Look forward to going through some of the things we have in mind to automate and make everything more efficient, and also give you guys and William and Collin a pretty detailed view — hopefully in real time — of everything going on at Greenmark. I think that's the overall goal of a lot of the things we're going to be talking about.

---

### The Ask: Unified Database + Dashboards [05:00 - 10:00]

**Daniel Shanklin:** Cool, let's dive in. I'll just kind of go off the little document that I sent you.

**Michael Nguyen:** I think the main goal here is we have a lot of different systems that do a lot of different things and have a lot of different data. We want to take all that data and put it into a single database where we can build more or less real-time dashboards off of them. I sent you the example of the metrics that we look at — that gets sent out to Collin and William every single month, and internally we look at it almost every single week. With our data set, you should be able to see daily views — you should be able to get pretty granular. The data comes from a lot of different systems and putting it in one unified database is going to be helpful. That's step one for us — setting up a database, whether it's AWS or Snowflake, getting an instance set up and then starting to take a look at all the individual pieces of software we have. We can get you whatever access level you need. Then see whether we need to build a connector or there's off-the-shelf stuff we can use. There's probably going to be a little bit of data engineering combining tables that make up the ultimate metrics dashboard.

**Daniel Shanklin:** Thanks for putting together this really detailed document — it does help a lot. Is there a single pain point where you're like, if we just had this one thing, it would zoom us an additional 20%?

**Michael Nguyen:** I think we have a fairly efficient system. Alex has an extremely detailed financial model down to the GL level. We can export data out of Sage and into the model, and it feeds into a good amount of the data in the metrics dashboard. I wouldn't even call it a pain point — we have it down to such a science. But it's then going and exporting the data from all the various systems that make up the rest of the metrics. It's more of like moving data around — that's what takes time.

**Daniel Shanklin:** Let's talk about dashboarding. Is it more important that you have an AI agent where you could ask it questions, or is it more important that you have a standard dashboard set with charts and graphs that are consistent, reliable, updated within the day?

**Michael Nguyen:** That's number one. Because most people are used to seeing that. The AI agent that can answer questions is kind of phase two. Most people aren't used to finding data that way — they are more used to seeing an Excel chart. The dashboards are definitely the most important.

---

### Recording & Meeting Culture [10:00 - 12:00]

**Michael Nguyen:** Real quick, Daniel — I didn't mention anything about Claude in this, and I imagine it would be a piece of all this. So getting Claude set up for Greenmark as well.

**Daniel Shanklin:** Understood. We're recording this phone call — is that a common thing that y'all do? I ask because if there's not a great record set of what's going on every week, then we can't convert that with AI into action items and things you're supposed to do next. Do you need any help with that aspect?

**Michael Nguyen:** We don't record calls. I would say we don't have a ton of them. They're more internal, if anything. A lot of our business — and you'll love this Daniel — is still face to face and shaking hands. So there's not a lot of conference calls. If we're going to discuss something with a customer, some combination of us are sitting right in front of them talking to them at the site.

**Daniel Shanklin:** Makes a lot of sense. And they're probably not the kind of personality that's going to want you to pull out your little AI recorder, right?

**Michael Nguyen:** Yes, very correct. Maybe not Alex, though — he uses AI.

**Alex Kaye:** I'm like an elementary school user of it, though. I'm like, what's two plus two? And I make sure it's four.

---

### Triage & Architecture [12:00 - 15:00]

**Daniel Shanklin:** As I scroll through this — Luke, any thoughts on how you want to triage something like this?

**Luke Huntley:** For me, it'd be getting their data warehouse set up and researching where each of these connectors are going to come in. My first jump is Supabase for Postgres, but at the same time, they need probably a lot larger data warehouse than it could support — finding the balance between whether we want to spin up an AWS database or Snowflake and seeing how the connections are going to flow.

**Daniel Shanklin:** I think having that fourth column — how easy is it to get data in or out of it? Does it have API connectivity? That's where you get limited.

**Michael Nguyen:** Navisoft, our main operating system, they have started building out an API. Sage is a pretty ubiquitous product and they have connectors they work with. Most of this stuff is all web-based, pretty readily available — except Third Eye, which is our camera and telematics system. That one I don't know how that was built. But most of this stuff shouldn't be too difficult to get things in and out.

---

### Approach & Mockups [15:00 - 20:00]

**Daniel Shanklin:** Luke and I love to "make it so" — our favorite trick is to get you a specific business question answered end-to-end, and then when we hand it over you're like, yeah, that's what I was looking for. Then we go backward and re-engineer the system to do it on a more repeated basis. It proves out within a day that we're delivering what you need without spending a week building something you don't.

**Michael Nguyen:** Most of that stuff though is secondary to getting the database and the dashboard set up. There's not a ton of different unique work processes — it is extremely repetitive. Once we get the database set up, a lot of the stuff will be using this data. Everything's going to be coming out of this database.

**Daniel Shanklin:** *(shows GitHub/AIC infra repo on screen)* Anybody here have any experience using GitHub?

**Michael Nguyen:** Can't say that I've used it. I've looked at it, but haven't used it.

**Daniel Shanklin:** I'll show you why I brought it up. This is GitHub — owned by Microsoft. It's where we put different organizations and inside each organization we put code, but it's not just code. You can put governance docs, compliance documents. You can see the last time somebody changed something — it's a file system in itself. This is our infra, short for infrastructure. It helps us understand all the different things we manage at AIC — databases, how they all work. All of it was managed by AI. I think probably one of the first projects would be to build out this infra chart based on everything you've provided as Project Cerebro. Who named that, by the way?

**Michael Nguyen:** I did. If you can guess where I got it from, even more brownie points.

**Daniel Shanklin:** I wouldn't be able to do it without looking it up. So this is kind of like our version of "where is everything" — what's the lay of the land. Because once you get it in here, AI can start helping you chew through what things cost, how you're going to do security, all that stuff. That would actually be my first suggestion because then we could come back and have a meeting in a day or two and I could say, does this match your expectation? We can build two or three fake dashboards like now if you want, then just turn around and be like, what do you like and what do you not like? That interaction might just get the ball rolling down the hill.

---

### Data Quality & Audit [20:00 - 25:00]

**Michael Nguyen:** One other thing — having checks and balances. Having warnings come up if things aren't loading correctly, if there's errors. The big piece for us is having a good audit trail. As we automate processes, we don't want it to just spit out something where there's no way to check its work. We're a trust but verify type group.

**Daniel Shanklin:** Just for those that don't know me — Michael does know this — I used to work in data quality in some of the largest hospital systems in the country. That's where I cut my teeth in data science. For me, data quality is near and dear to my heart. When people don't get that right, whatever you got in your dashboard doesn't matter. I'm all about building systems outside the original system — a second one that's ugly, but its whole job is to check that the first one is correct.

---

### Next Steps & Data Walkthrough [25:00 - 26:15]

**Alex Kaye:** I imagine at some point we'll want to show you guys what all the detailed data looks like. I'm envisioning showing you the data dump of everything coming out of our systems and then working with y'all to map that and put rules around it to get what we need — whether it's dashboards, KPIs, or asking the AI bot questions about that data set. So at some point we'll need to walk through that with you guys.

**Daniel Shanklin:** Alex, we're going to get along great because that infra idea and the map — they're so part and parcel to how you're going to prove this can work and what it might cost and how you keep it all together. I'd be happy to turn around a map and then you just look at it and go, well, that isn't right.

**Michael Nguyen:** We're going to be pretty involved throughout the whole process and want to learn each of the steps. I think one of the biggest pieces of what's going to take time is looking at all the underlying database tables and mapping them and basically joining tables. We need this metric and we get it from this table and this table and this is how we calculate it.

**Daniel Shanklin:** This is what we do. I feel good about this one — you haven't said anything where I'm like, I have no clue what to do next.

**Michael Nguyen:** I told you — you should be able to do this in your sleep.

**Daniel Shanklin:** If there's nothing else, I will make it my responsibility to get an email back to you here in the next hour or so with some ideas on where to go next and get your approval on them.

**Michael Nguyen:** Yeah, sounds good, man. Thank you, sir.

**Daniel Shanklin:** All right, thanks everybody.

**Alex Kaye:** Thanks guys.

---

## Decisions Made
- **Dashboard first, AI agent second** — Michael: "The dashboards are definitely the most important. The AI agent is phase two."
- **Greenmark gets its own tech org** — Daniel (per Slack): Separate from AIC, Greenmark property
- **Step 1 is unified database** — All systems feeding into one data warehouse
- **First deliverable: infra map** — Daniel to build out infrastructure chart from Project Cerebro docs
- **Dashboard mockups ASAP** — Daniel offered to build 2-3 mockups for feedback

## Action Items

| Owner | Action | Timeline | Source |
|-------|--------|----------|--------|
| Daniel Shanklin | Send follow-up email with ideas on next steps | Within 1 hour of call | "I will make it my responsibility to get an email back to you here in the next hour" |
| Daniel Shanklin | Build infra map from Project Cerebro docs | Days | "build out this infra chart based on everything you've provided" |
| Daniel Shanklin | Create 2-3 dashboard mockups for feedback | Days | "build two or three fake dashboards like now" |
| Daniel + Luke | Research data connectors for each system | Before next meeting | Luke: "researching where each of these connectors are going to come in" |
| Daniel + Luke | Evaluate data warehouse options (Supabase vs AWS vs Snowflake) | Before next meeting | Luke's triage recommendation |
| Michael + Alex | Provide system access for data exploration | As needed | "We can get you whatever access level you need" |
| Alex + Michael | Walk team through detailed data from each system | Future meeting | Alex: "at some point we'll want to show you guys what all the detailed data looks like" |
| Daniel | Set up Claude for Greenmark | TBD | Michael: "getting Claude set up for Greenmark" |

## Key Systems Mentioned
- **Navisoft** — Main operating system (API in development)
- **Sage** — Accounting/ERP (has connectors, ubiquitous product)
- **Third Eye** — Camera and telematics system (unknown API status — potential blocker)
- **Excel/financial model** — Alex's detailed GL-level financial model, exports from Sage

## Key Quotes

> "We try to build agentic type systems that basically withstand the test of time because I feel like software is one of those depreciating assets." — Daniel Shanklin

> "A lot of our business is still face to face and shaking hands." — Michael Nguyen

> "We're a trust but verify type group." — Michael Nguyen

> "Code is easy. Governance is hard." — Daniel Shanklin

> "I started my own company with one truck and one container and built it into something pretty special." — Lannis Nicholson
