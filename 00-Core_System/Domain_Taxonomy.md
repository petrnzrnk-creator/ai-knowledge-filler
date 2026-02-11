---
title: "Domain Taxonomy"
type: reference
domain: ai-system
level: intermediate
status: active
version: v1.0
tags: [taxonomy, domains, classification, ontology, obsidian]
related:
  - "[[Metadata_Template_Standard]]"
  - "[[System_Prompt_AI_Knowledge_Filler]]"
  - "[[File_Update_Protocol]]"
created: 2026-02-06
updated: 2026-02-06
---

## PURPOSE

Standardized taxonomy of domain values for the `domain` field in YAML metadata across all Obsidian knowledge files.

---

## TAXONOMY STRUCTURE

### **Core Domains**

#### ai-system
Knowledge base infrastructure, AI workflows, automation systems, prompt engineering

#### system-design
Software architecture, scalability patterns, distributed systems, infrastructure

#### api-design
API architecture, REST, GraphQL, versioning, authentication, rate limiting

#### data-engineering
Data pipelines, ETL, databases, data modeling, warehousing

#### security
Application security, authentication, authorization, cryptography, compliance

#### devops
CI/CD, containerization, orchestration, monitoring, deployment

#### product-management
Product strategy, roadmaps, requirements, stakeholder management

#### consulting
Consulting methodologies, client engagement, deliverables, frameworks

#### workflow-automation
Process automation, no-code/low-code, integration platforms, RPA

#### prompt-engineering
LLM interaction, prompt design, AI agent orchestration

#### business-strategy
Strategic planning, competitive analysis, value proposition, business models

#### project-management
Project planning, execution, risk management, methodologies (Agile, Waterfall)

---

### **Knowledge Management Domains**

#### knowledge-management
Information architecture, PKM, Obsidian workflows, note-taking systems

#### documentation
Technical writing, API docs, user guides, knowledge transfer

#### learning-systems
Educational design, curriculum development, skill acquisition

---

### **Technical Domains**

#### frontend-engineering
UI development, React, Vue, web performance, accessibility

#### backend-engineering
Server-side logic, microservices, APIs, database interactions

#### infrastructure
Cloud platforms (AWS, GCP, Azure), networking, storage, compute

#### machine-learning
ML models, training pipelines, feature engineering, model deployment

#### data-science
Statistical analysis, visualization, experimentation, hypothesis testing

---

### **Business & Operations Domains**

#### operations
Business operations, process optimization, SOP development

#### finance
Financial modeling, budgeting, cost analysis, ROI calculation

#### marketing
Marketing strategy, content marketing, SEO, growth tactics

#### sales
Sales processes, pipeline management, CRM, deal flow

---

### **Specialized Domains**

#### healthcare
Medical systems, HIPAA compliance, clinical workflows

#### finance-tech
FinTech, payment systems, regulatory compliance, blockchain

#### education-tech
EdTech platforms, learning management systems, assessment tools

#### e-commerce
Online retail, payment processing, inventory management, fulfillment

---

## DOMAIN SELECTION RULES

### **Primary Domain Assignment**

- One primary domain per file
- Choose the most specific applicable domain
- If multiple domains apply, choose based on primary purpose

### **Multi-Domain Content**

- Primary domain in `domain` field
- Secondary domains in `tags` array
- Use hyphenated format consistently

### **Domain Hierarchy**

- Prefer specific over general (e.g., `api-design` over `system-design`)
- Use general domain only when content spans multiple specific domains

---

## VALIDATION RULES

### ✅ Valid Domain Values

```yaml
domain: ai-system
domain: prompt-engineering
domain: system-design
```

### ❌ Invalid Domain Values

```yaml
domain: AI System          # Not lowercase-hyphenated
domain: ai_system          # Underscores not allowed
domain: general            # Too vague, not in taxonomy
domain: technology         # Not specific enough
```

---

## DOMAIN DEFINITIONS

### ai-system
Files about AI infrastructure, system prompts, custom instructions, AI workflow orchestration, knowledge base architecture

**Examples:**
- [[System_Prompt_AI_Knowledge_Filler]]
- [[Custom Instructions — AI Working Profile]]
- [[Prompt_Engineering_Workflow]]

---

### system-design
Software architecture patterns, system scalability, distributed systems, architectural decision records

**Examples:**
- [[Microservices Architecture Patterns]]
- [[CAP Theorem Explained]]
- [[Event-Driven Architecture]]

---

### api-design
API development standards, REST principles, GraphQL schemas, API versioning strategies, authentication methods

**Examples:**
- [[API Design Principles]]
- [[REST vs GraphQL Decision Framework]]
- [[API Rate Limiting Strategy]]

---

### data-engineering
Data pipeline construction, ETL processes, data warehouse design, stream processing

**Examples:**
- [[Data Pipeline Architecture]]
- [[Dimensional Modeling]]
- [[CDC Implementation Patterns]]

---

### consulting
Consulting methodologies, client engagement frameworks, deliverable templates, advisory best practices

**Examples:**
- [[Consulting Engagement Framework]]
- [[Discovery Phase Checklist]]
- [[Executive Summary Template]]

---

### prompt-engineering
Prompt design techniques, LLM optimization, AI agent workflows, context window management

**Examples:**
- [[Prompt_Engineering_Workflow]]
- [[Few-Shot Prompting Techniques]]
- [[Chain-of-Thought Reasoning]]

---

## ADDING NEW DOMAINS

### **When to Add a New Domain**

- Existing taxonomy insufficient for 5+ files
- New specialization emerging in knowledge base
- Domain logically distinct from existing domains

### **New Domain Criteria**

- Must be lowercase-hyphenated
- Must be distinct and non-overlapping
- Must have clear scope and definition
- Must be expected to have multiple files

### **Addition Process**

1. Propose new domain with definition
2. Validate against existing domains
3. Update this taxonomy file
4. Update [[Metadata_Template_Standard]] if needed
5. Retroactively tag applicable files

---

## DOMAIN MIGRATION

### **When Domain Changes**

If a domain is renamed, deprecated, or split:

1. Document change in this file
2. Create migration mapping
3. Update affected files
4. Preserve old domain in `tags` for discoverability

### **Deprecated Domains**

Mark as deprecated, preserve in taxonomy for reference:

```yaml
#### legacy-domain (DEPRECATED → new-domain)
[Definition and migration path]
```

---

## CROSS-DOMAIN PATTERNS

### **Multi-Domain Files**

When content genuinely spans domains:

```yaml
domain: api-design
tags: [api, security, authentication, system-design]
```

Primary domain: `api-design` (main focus)  
Secondary domains: captured in tags

---

### **Domain Clusters**

Related domains often appear together:

- `ai-system` + `prompt-engineering` + `workflow-automation`
- `api-design` + `security` + `system-design`
- `consulting` + `business-strategy` + `project-management`

---

## QUERYING BY DOMAIN

### **Dataview Examples**

**All files in domain:**
```dataview
TABLE title, status, level
FROM #ai-system
WHERE domain = "ai-system"
SORT updated DESC
```

**Cross-domain query:**
```dataview
LIST
FROM "/"
WHERE domain IN ["api-design", "system-design"]
AND status = "active"
```

---

## INTEGRATION

### **With [[Metadata_Template_Standard]]**
- `domain` field references this taxonomy
- Invalid domains rejected during validation

### **With [[System_Prompt_AI_Knowledge_Filler]]**
- AI validates domain against this list
- Suggests closest match if invalid domain requested

### **With Obsidian**
- Domains enable powerful filtering
- Graph view grouping by domain
- Tag-based navigation

---

## MAINTENANCE

### **Regular Review**

- Quarterly review of domain usage
- Identify under-utilized or over-broad domains
- Refine definitions based on actual usage

### **Version Control**

- Track taxonomy changes in this file
- Update version when domains added/removed
- Document rationale for changes

---

## QUALITY CHECKLIST

- [ ] Domain is lowercase-hyphenated
- [ ] Domain is in approved taxonomy
- [ ] Domain is most specific applicable
- [ ] Secondary domains in tags if needed
- [ ] Domain definition clear and distinct

---

## CONCLUSION

This taxonomy ensures consistent, discoverable, and meaningful domain classification across the entire Obsidian knowledge base.