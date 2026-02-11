---
title: "Prompt Engineering Workflow"
type: guide
domain: prompt-engineering
level: advanced
status: active
tags: [prompt-engineering, workflow, ai, automation]
related:
  - "[[AI_Solutions_Architect]]"
  - "[[System_Prompt_AI_Knowledge_Filler]]"
  - "[[AI_Augmented_Work_Principles]]"
created: 2026-02-06
updated: 2026-02-06
---

## Purpose
Standardized workflow for designing, executing and validating tasks using AI.

---

## Core Principle
AI is used as **executor and accelerator**,  
human — as **architect, controller and source of responsibility**.

---

## Workflow Stages

### 1. Problem Framing
- Clearly formulate business task
- Fix expected result
- Define constraints and context

**Artifact:** brief task description

---

### 2. Role Assignment
- Assign AI specific role
- Define responsibility boundaries
- Fix style and output format

**Artifact:** system / role prompt

---

### 3. Output Specification
- Output format (Markdown, JSON, schema)
- Structure and required elements
- Result readiness criteria

**Artifact:** output contract

---

### 4. Prompt Construction
- Instructions → principles → constraints
- Minimum ambiguity
- One task — one prompt

**Artifact:** final working prompt

---

### 5. AI Execution
- Result generation
- Without manual intervention in process
- Output version fixation

**Artifact:** raw AI output

---

### 6. Validation
- Logic and structure verification
- Goal compliance verification
- Search for errors and hallucinations

**Artifact:** list of corrections

---

### 7. Refinement Loop
- Prompt refinement
- Re-generation
- Version comparison

Cycle repeats until criteria are met.

---

### 8. Finalization
- Final validation
- Result cleanup
- Integration into system (Obsidian, project, client)

**Artifact:** production-ready output

---

## Prompt Design Rules

- One prompt = one goal
- Explicit constraints are more important than examples
- Format is more important than 'text beauty'
- Always specify role and operating mode

---

## Common Failure Modes

- Unclear goal
- Absence of readiness criteria
- Role mixing
- Absence of validation

---

## Success Indicators

- Predictable result
- Minimum iterations
- Scalability of approach
- Ability to delegate to AI

---

## Integration
Used together with:
- [[System_Prompt_AI_Knowledge_Filler]]
- Obsidian + Dataview
- Consulting workflows
