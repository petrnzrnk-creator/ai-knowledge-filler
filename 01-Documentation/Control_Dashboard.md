---
title: "Control Dashboard — AI Knowledge Filler"
type: reference
domain: ai-system
level: intermediate
status: active
version: v1.0
tags: [dashboard, monitoring, governance, dataview, analytics]
related:
  - "[[System_Prompt_AI_Knowledge_Filler]]"
  - "[[Metadata_Template_Standard]]"
  - "[[Domain_Taxonomy]]"
  - "[[Deployment_Guide]]"
created: 2026-02-06
updated: 2026-02-06
---

## PURPOSE

Dataview-powered dashboard for monitoring, governance, and quality assurance of AI-generated knowledge files.

---

## QUICK STATS

### Total Files by Status

```dataview
TABLE
  length(rows) as "Count"
FROM "/"
WHERE file.name != "Control_Dashboard"
GROUP BY status
SORT length(rows) DESC
```

### Files by Domain

```dataview
TABLE
  length(rows) as "Count"
FROM "/"
WHERE domain
GROUP BY domain
SORT length(rows) DESC
```

### Files by Type

```dataview
TABLE
  length(rows) as "Count"
FROM "/"
WHERE type
GROUP BY type
SORT length(rows) DESC
```

---

## RECENT ACTIVITY

### Recently Updated (Last 7 Days)

```dataview
TABLE
  title as "Title",
  domain as "Domain",
  type as "Type",
  status as "Status",
  updated as "Updated"
FROM "/"
WHERE updated >= date(today) - dur(7 days)
SORT updated DESC
LIMIT 20
```

### Recently Created (Last 7 Days)

```dataview
TABLE
  title as "Title",
  domain as "Domain",
  type as "Type",
  status as "Status",
  created as "Created"
FROM "/"
WHERE created >= date(today) - dur(7 days)
SORT created DESC
LIMIT 20
```

---

## QUALITY MONITORING

### Draft Files (Needs Review)

```dataview
TABLE
  title as "Title",
  domain as "Domain",
  type as "Type",
  created as "Created"
FROM "/"
WHERE status = "draft"
SORT created ASC
```

### Files Without Related Links

```dataview
TABLE
  title as "Title",
  domain as "Domain",
  type as "Type"
FROM "/"
WHERE !related OR length(related) = 0
SORT file.mtime DESC
LIMIT 20
```

### Files With Few Tags (< 3)

```dataview
TABLE
  title as "Title",
  domain as "Domain",
  tags as "Tags",
  length(tags) as "Tag Count"
FROM "/"
WHERE length(tags) < 3
SORT length(tags) ASC
LIMIT 20
```

### Files Missing Version

```dataview
TABLE
  title as "Title",
  domain as "Domain",
  type as "Type",
  status as "Status"
FROM "/"
WHERE !version AND type IN ["guide", "reference", "template"]
SORT file.name ASC
```

---

## DOMAIN ANALYSIS

### Files Per Domain (Detailed)

```dataview
TABLE WITHOUT ID
  domain as "Domain",
  length(rows.file.link) as "Total Files",
  length(filter(rows, (r) => r.status = "active")) as "Active",
  length(filter(rows, (r) => r.status = "draft")) as "Draft",
  length(filter(rows, (r) => r.status = "completed")) as "Completed"
FROM "/"
WHERE domain
GROUP BY domain
SORT length(rows.file.link) DESC
```

### Domain Coverage by Type

```dataview
TABLE WITHOUT ID
  type as "Type",
  length(rows.file.link) as "Total",
  join(list(map(group(rows, (r) => r.domain), (g) => g.key + " (" + length(g.rows) + ")")), ", ") as "Domains"
FROM "/"
WHERE type AND domain
GROUP BY type
SORT length(rows.file.link) DESC
```

---

## CONTENT TYPE BREAKDOWN

### Guides

```dataview
TABLE
  title as "Title",
  domain as "Domain",
  level as "Level",
  status as "Status",
  updated as "Updated"
FROM "/"
WHERE type = "guide"
SORT updated DESC
```

### Concepts

```dataview
TABLE
  title as "Title",
  domain as "Domain",
  level as "Level",
  status as "Status"
FROM "/"
WHERE type = "concept"
SORT domain ASC, title ASC
```

### References

```dataview
TABLE
  title as "Title",
  domain as "Domain",
  level as "Level",
  status as "Status",
  version as "Version"
FROM "/"
WHERE type = "reference"
SORT domain ASC, title ASC
```

### Checklists

```dataview
TABLE
  title as "Title",
  domain as "Domain",
  status as "Status"
FROM "/"
WHERE type = "checklist"
SORT domain ASC, title ASC
```

### Projects

```dataview
TABLE
  title as "Title",
  domain as "Domain",
  status as "Status",
  updated as "Last Update"
FROM "/"
WHERE type = "project"
SORT updated DESC
```

---

## GOVERNANCE & COMPLIANCE

### Files With Invalid Metadata

```dataview
TABLE
  title as "Title",
  file.name as "Filename",
  "Missing/Invalid" as "Issue"
FROM "/"
WHERE !title OR !type OR !domain OR !level OR !status OR !created OR !updated
```

### Files With Non-Standard Domains

```dataviewjs
// Define valid domains from taxonomy
const validDomains = [
  "ai-system", "system-design", "api-design", "data-engineering",
  "security", "devops", "product-management", "consulting",
  "workflow-automation", "prompt-engineering", "business-strategy",
  "project-management", "knowledge-management", "documentation",
  "learning-systems", "frontend-engineering", "backend-engineering",
  "infrastructure", "machine-learning", "data-science", "operations",
  "finance", "marketing", "sales", "healthcare", "finance-tech",
  "education-tech", "e-commerce"
];

const pages = dv.pages()
  .where(p => p.domain && !validDomains.includes(p.domain));

dv.table(
  ["Title", "Domain", "Filename"],
  pages.map(p => [p.title, p.domain, p.file.name])
);
```

### Files With Invalid Status Values

```dataviewjs
const validStatuses = ["draft", "active", "completed", "archived"];

const pages = dv.pages()
  .where(p => p.status && !validStatuses.includes(p.status));

dv.table(
  ["Title", "Status", "Domain"],
  pages.map(p => [p.title, p.status, p.domain])
);
```

### Files With Invalid Type Values

```dataviewjs
const validTypes = [
  "concept", "guide", "reference", "checklist",
  "project", "roadmap", "template", "audit"
];

const pages = dv.pages()
  .where(p => p.type && !validTypes.includes(p.type));

dv.table(
  ["Title", "Type", "Domain"],
  pages.map(p => [p.title, p.type, p.domain])
);
```

---

## KNOWLEDGE GRAPH ANALYSIS

### Most Referenced Files

```dataviewjs
// Count incoming links to each file
const pages = dv.pages();
const linkCounts = new Map();

for (const page of pages) {
  const incomingLinks = pages
    .where(p => p.file.outlinks.includes(page.file.link))
    .length;
  
  if (incomingLinks > 0) {
    linkCounts.set(page, incomingLinks);
  }
}

// Sort by link count
const sorted = Array.from(linkCounts.entries())
  .sort((a, b) => b[1] - a[1])
  .slice(0, 20);

dv.table(
  ["Title", "Domain", "Incoming Links"],
  sorted.map(([page, count]) => [page.title, page.domain, count])
);
```

### Orphaned Files (No Incoming Links)

```dataviewjs
const pages = dv.pages()
  .where(p => p.file.name != "Control_Dashboard");

const orphans = pages.filter(page => {
  const incomingLinks = pages
    .where(p => p.file.outlinks.includes(page.file.link))
    .length;
  return incomingLinks === 0;
});

dv.table(
  ["Title", "Domain", "Type", "Created"],
  orphans
    .sort(p => p.created, "desc")
    .limit(20)
    .map(p => [p.title, p.domain, p.type, p.created])
);
```

### Files With Most Outgoing Links

```dataview
TABLE
  title as "Title",
  domain as "Domain",
  length(file.outlinks) as "Outgoing Links"
FROM "/"
WHERE length(file.outlinks) > 0
SORT length(file.outlinks) DESC
LIMIT 20
```

---

## TEMPORAL ANALYSIS

### Creation Timeline (Last 30 Days)

```dataviewjs
const now = dv.luxon.DateTime.now();
const thirtyDaysAgo = now.minus({ days: 30 });

const pages = dv.pages()
  .where(p => p.created && dv.luxon.DateTime.fromISO(p.created) >= thirtyDaysAgo);

// Group by date
const grouped = pages.groupBy(p => p.created);

dv.table(
  ["Date", "Files Created"],
  grouped
    .sort(g => g.key, "desc")
    .map(g => [g.key, g.rows.length])
);
```

### Update Frequency by Domain

```dataviewjs
const pages = dv.pages().where(p => p.domain);

const domainUpdates = pages
  .groupBy(p => p.domain)
  .map(g => {
    const avgDaysSinceUpdate = g.rows
      .map(p => {
        const updated = dv.luxon.DateTime.fromISO(p.updated);
        const now = dv.luxon.DateTime.now();
        return now.diff(updated, 'days').days;
      })
      .reduce((sum, days) => sum + days, 0) / g.rows.length;
    
    return {
      domain: g.key,
      count: g.rows.length,
      avgDays: Math.round(avgDaysSinceUpdate)
    };
  })
  .sort(d => d.avgDays, "asc");

dv.table(
  ["Domain", "File Count", "Avg Days Since Update"],
  domainUpdates.map(d => [d.domain, d.count, d.avgDays])
);
```

### Stale Files (Not Updated in 90 Days)

```dataviewjs
const now = dv.luxon.DateTime.now();
const ninetyDaysAgo = now.minus({ days: 90 });

const stale = dv.pages()
  .where(p => {
    const updated = dv.luxon.DateTime.fromISO(p.updated);
    return updated < ninetyDaysAgo;
  })
  .sort(p => p.updated, "asc")
  .limit(20);

dv.table(
  ["Title", "Domain", "Status", "Last Updated", "Days Ago"],
  stale.map(p => {
    const updated = dv.luxon.DateTime.fromISO(p.updated);
    const daysAgo = Math.round(now.diff(updated, 'days').days);
    return [p.title, p.domain, p.status, p.updated, daysAgo];
  })
);
```

---

## LEVEL DISTRIBUTION

### Files by Difficulty Level

```dataview
TABLE
  length(rows) as "Count"
FROM "/"
WHERE level
GROUP BY level
SORT length(rows) DESC
```

### Advanced Files by Domain

```dataview
TABLE
  title as "Title",
  domain as "Domain",
  type as "Type",
  status as "Status"
FROM "/"
WHERE level = "advanced"
SORT domain ASC, title ASC
```

### Beginner-Friendly Content

```dataview
TABLE
  title as "Title",
  domain as "Domain",
  type as "Type"
FROM "/"
WHERE level = "beginner"
SORT domain ASC, title ASC
```

---

## TAG ANALYSIS

### Most Used Tags

```dataviewjs
const pages = dv.pages();
const tagCounts = new Map();

for (const page of pages) {
  if (page.tags) {
    for (const tag of page.tags) {
      tagCounts.set(tag, (tagCounts.get(tag) || 0) + 1);
    }
  }
}

const sorted = Array.from(tagCounts.entries())
  .sort((a, b) => b[1] - a[1])
  .slice(0, 30);

dv.table(
  ["Tag", "Usage Count"],
  sorted
);
```

### Tag Co-occurrence

```dataviewjs
const pages = dv.pages().where(p => p.tags && p.tags.length >= 2);

const cooccurrence = new Map();

for (const page of pages) {
  const tags = page.tags.sort();
  for (let i = 0; i < tags.length; i++) {
    for (let j = i + 1; j < tags.length; j++) {
      const pair = `${tags[i]} + ${tags[j]}`;
      cooccurrence.set(pair, (cooccurrence.get(pair) || 0) + 1);
    }
  }
}

const sorted = Array.from(cooccurrence.entries())
  .sort((a, b) => b[1] - a[1])
  .slice(0, 20);

dv.table(
  ["Tag Pair", "Co-occurrence Count"],
  sorted
);
```

---

## CUSTOM SEARCHES

### Files Matching Criteria

```dataview
TABLE
  title as "Title",
  domain as "Domain",
  type as "Type",
  status as "Status",
  updated as "Updated"
FROM "/"
WHERE 
  domain = "api-design" AND
  status = "active" AND
  type = "guide"
SORT updated DESC
```

### Multi-Domain Search

```dataview
TABLE
  title as "Title",
  domain as "Domain",
  level as "Level",
  status as "Status"
FROM "/"
WHERE domain IN ["ai-system", "prompt-engineering", "workflow-automation"]
SORT domain ASC, title ASC
```

---

## ACTIONABLE INSIGHTS

### Files Needing Attention

```dataviewjs
const issues = [];

const pages = dv.pages();

for (const page of pages) {
  const problems = [];
  
  // Missing related links
  if (!page.related || page.related.length === 0) {
    problems.push("No related links");
  }
  
  // Few tags
  if (!page.tags || page.tags.length < 3) {
    problems.push("Insufficient tags");
  }
  
  // Draft status
  if (page.status === "draft") {
    problems.push("Draft status");
  }
  
  // No version on reference/guide
  if (!page.version && ["guide", "reference", "template"].includes(page.type)) {
    problems.push("Missing version");
  }
  
  if (problems.length > 0) {
    issues.push({
      title: page.title,
      domain: page.domain,
      problems: problems.join(", ")
    });
  }
}

dv.table(
  ["Title", "Domain", "Issues"],
  issues
    .sort((a, b) => a.title.localeCompare(b.title))
    .slice(0, 30)
    .map(i => [i.title, i.domain, i.problems])
);
```

---

## SYSTEM HEALTH SCORE

```dataviewjs
const pages = dv.pages().where(p => p.file.name != "Control_Dashboard");
const total = pages.length;

// Calculate metrics
const withMetadata = pages.where(p => p.title && p.type && p.domain).length;
const withLinks = pages.where(p => p.related && p.related.length > 0).length;
const withTags = pages.where(p => p.tags && p.tags.length >= 3).length;
const active = pages.where(p => p.status === "active").length;

const metadataScore = (withMetadata / total * 100).toFixed(1);
const linkScore = (withLinks / total * 100).toFixed(1);
const tagScore = (withTags / total * 100).toFixed(1);
const activeScore = (active / total * 100).toFixed(1);

const overallScore = ((
  parseFloat(metadataScore) +
  parseFloat(linkScore) +
  parseFloat(tagScore) +
  parseFloat(activeScore)
) / 4).toFixed(1);

dv.header(2, `Overall Health Score: ${overallScore}%`);

dv.table(
  ["Metric", "Score", "Count"],
  [
    ["Complete Metadata", `${metadataScore}%`, `${withMetadata}/${total}`],
    ["Has Related Links", `${linkScore}%`, `${withLinks}/${total}`],
    ["Sufficient Tags (3+)", `${tagScore}%`, `${withTags}/${total}`],
    ["Active Status", `${activeScore}%`, `${active}/${total}`]
  ]
);
```

---

## USAGE

### How to Use This Dashboard

1. **Pin to Sidebar** — Keep dashboard accessible
2. **Review Weekly** — Check quality metrics and stale files
3. **Fix Issues** — Address files in "Needing Attention" section
4. **Monitor Growth** — Track domain coverage and creation timeline
5. **Enforce Standards** — Use governance queries to maintain quality

### Customization

Modify queries to match your workflow:
- Change time ranges (7 days → 30 days)
- Add custom domains to validation
- Adjust quality thresholds
- Create domain-specific dashboards

---

## MAINTENANCE TASKS

### Weekly
- [ ] Review draft files
- [ ] Check files without related links
- [ ] Update stale files
- [ ] Validate new files

### Monthly
- [ ] Domain coverage analysis
- [ ] Tag cleanup and standardization
- [ ] Orphaned files review
- [ ] Health score assessment

### Quarterly
- [ ] Taxonomy updates
- [ ] Archived files cleanup
- [ ] System prompt refinement
- [ ] Documentation updates

---

## CONCLUSION

This dashboard provides real-time visibility into your AI-generated knowledge base quality, growth, and governance.

Use insights to maintain **high-quality**, **well-connected**, and **discoverable** knowledge files.
