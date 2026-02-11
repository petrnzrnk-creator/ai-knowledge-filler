---
title: "File Update Protocol"
type: reference
domain: ai-system
level: advanced
status: active
version: v1.0
tags: [protocol, file-management, update, merge, obsidian]
related:
  - "[[System_Prompt_AI_Knowledge_Filler]]"
  - "[[Metadata_Template_Standard]]"
  - "[[Custom Instructions — AI Working Profile]]"
  - "[[Prompt_Engineering_Workflow]]"
created: 2026-02-06
updated: 2026-02-06
---

## PURPOSE

Standard protocol for handling updates, merges, and conflicts when AI Knowledge Filler modifies existing Obsidian files.

---

## CORE PRINCIPLES

- **Preservation First:** Existing content is not deleted without explicit user instruction
- **Additive by Default:** New content is added, not replaced
- **Metadata Integrity:** YAML fields follow strict merge rules
- **User Authority:** User-created content takes precedence over AI suggestions

---

## UPDATE SCENARIOS

### 1. NEW CONTENT ADDITION
**Trigger:** User requests adding new section/information to existing file

**Action:**
- Append new content to appropriate section
- Maintain existing structure
- Update `updated` field in YAML
- Add new tags if relevant (preserve existing)

**Example:**
```
User: "Add API versioning best practices to [[API Design Principles]]"
AI: Adds new ## Versioning section, updates YAML
```

---

### 2. CONTENT REFINEMENT
**Trigger:** User requests improving/expanding existing section

**Action:**
- Enhance existing content in place
- Preserve original structure and intent
- Update `updated` field
- Optionally increment `version` if major rewrite

**Example:**
```
User: "Expand the caching section with Redis examples"
AI: Enhances ## Caching section, updates metadata
```

---

### 3. STRUCTURAL REORGANIZATION
**Trigger:** User requests restructuring file organization

**Action:**
- Reorganize sections as specified
- Preserve all content (no deletion)
- Update `updated` and `version` fields
- Note structural change in commit/update log if maintained

**Example:**
```
User: "Reorganize by priority instead of chronology"
AI: Restructures, increments version to v2.0
```

---

### 4. METADATA UPDATE
**Trigger:** User requests changing YAML fields

**Action:**
- Update specified fields only
- Follow [[Metadata_Template_Standard]]
- Always update `updated` field
- Validate against allowed values

**Example:**
```
User: "Change status to completed and add version v1.0"
AI: Updates YAML, preserves all content
```

---

### 5. CONFLICT RESOLUTION
**Trigger:** User instruction conflicts with existing content

**Action:**
- **Default:** Ask user for clarification
- **If instructed to replace:** Remove old content, add new
- **If instructed to merge:** Combine both versions
- Always note conflict in response

**Example:**
```
Existing: "Use REST APIs"
User: "Change to GraphQL recommendation"
AI: "File currently recommends REST. Replace or add GraphQL as alternative?"
```

---

## YAML METADATA MERGE RULES

### **Field Priority Matrix**

| Field | Update Rule | Preservation |
|-------|-------------|--------------|
| `title` | User approval required | Always preserve unless explicit change |
| `type` | User approval required | Preserve |
| `domain` | Can suggest change | Preserve unless invalid |
| `level` | Auto-update if content complexity changes | Preserve |
| `status` | Auto-update per lifecycle | Update on completion |
| `version` | Auto-increment on major changes | Increment, never replace |
| `tags` | **Additive merge** | Preserve + add new |
| `related` | **Additive merge** | Preserve + add new |
| `created` | **Never change** | Always preserve |
| `updated` | **Always change** | Update to current date |

---

### **Tags Merge Strategy**

**Rule:** Union of existing and new tags, deduplicated

**Process:**
1. Preserve all existing tags
2. Add new relevant tags
3. Remove duplicates (case-insensitive)
4. Sort alphabetically (optional)
5. Max 10 tags total

**Example:**
```yaml
# Existing
tags: [api, rest, design]

# AI adds
tags: [api, rest, design, graphql, versioning]
```

---

### **Related Links Merge Strategy**

**Rule:** Union of existing and new links, deduplicated

**Process:**
1. Preserve all existing `[[links]]`
2. Add new relevant links
3. Remove duplicates
4. Validate link format
5. No arbitrary limit

**Example:**
```yaml
# Existing
related:
  - [[API Design Principles]]
  
# AI adds
related:
  - [[API Design Principles]]
  - [[GraphQL Best Practices]]
  - [[Versioning Strategy]]
```

---

## CONTENT MERGE STRATEGIES

### **Section-Level Merge**

**When:** Adding new section to existing file

**Process:**
1. Identify insertion point (end of file or logical position)
2. Add appropriate heading level
3. Insert new content
4. Maintain heading hierarchy
5. Preserve all existing sections

---

### **Paragraph-Level Enhancement**

**When:** Expanding existing section

**Process:**
1. Locate target section
2. Add new paragraphs/content
3. Maintain original flow
4. Use "Additionally," "Furthermore," etc. for transitions
5. Preserve original paragraphs

---

### **List Item Addition**

**When:** Adding items to existing lists

**Process:**
1. Locate target list
2. Append new items
3. Maintain formatting consistency
4. Deduplicate if overlap detected
5. Preserve original order

---

## DELETION PROTOCOL

### **When Deletion Is Allowed**

- User explicitly requests removal: "Delete X section"
- Content is demonstrably outdated: "Remove deprecated API info"
- Content is factually incorrect: "Remove false claim about Y"

### **Deletion Process**

1. Confirm scope with user
2. Remove specified content
3. Update metadata (`updated`, potentially `version`)
4. Note deletion in response

### **When Deletion Is Denied**

- Vague request: "Clean this up" → Ask for specifics
- Implicit: "Add new caching strategy" ≠ delete old one
- Uncertain: When user intent is unclear

---

## VERSION INCREMENT RULES

### **Patch (v1.0 → v1.1)**
- Minor content additions
- Typo fixes
- Metadata updates
- Small clarifications

### **Minor (v1.5 → v2.0)**
- New major sections
- Structural reorganization
- Significant content expansion
- Changed recommendations

### **Not Versioned**
- Metadata-only changes
- Tag additions
- Related link additions
- Typo corrections

---

## CONFLICT HANDLING

### **Type 1: Content Contradiction**

**Scenario:** New content contradicts existing

**Resolution:**
1. Detect contradiction
2. Present both versions to user
3. Ask: "Replace, merge, or add as alternative?"
4. Execute user decision

---

### **Type 2: Structural Incompatibility**

**Scenario:** New structure incompatible with existing

**Resolution:**
1. Identify incompatibility
2. Propose restructuring plan
3. Get user approval
4. Execute with version increment

---

### **Type 3: Metadata Conflict**

**Scenario:** Requested metadata violates standard

**Resolution:**
1. Flag violation (reference [[Metadata_Template_Standard]])
2. Suggest compliant alternative
3. Apply user-approved fix

---

## VALIDATION CHECKLIST

**Before Finalizing Update:**
- [ ] All YAML fields valid per [[Metadata_Template_Standard]]
- [ ] `updated` field set to current date
- [ ] `version` incremented if appropriate
- [ ] Existing content preserved (unless deletion approved)
- [ ] New content properly integrated
- [ ] Heading hierarchy maintained
- [ ] Internal links valid
- [ ] No duplicate tags/links
- [ ] User intent fulfilled

---

## SPECIAL CASES

### **Template Files**

**Rule:** Never auto-update templates

**Process:**
1. Suggest changes
2. User manually updates
3. Document change in template

---

### **Archived Files**

**Rule:** Require explicit user approval to modify

**Process:**
1. Alert user file is archived
2. Confirm update intent
3. Change `status` to `active` if updated
4. Proceed with normal protocol

---

### **Draft Files**

**Rule:** More permissive updates allowed

**Process:**
1. Assume work-in-progress state
2. Apply changes without extensive validation
3. Update normally

---

## FAILURE MODES & RECOVERY

### **Accidental Deletion**
- AI does not have "undo"
- User must restore from backup/git
- Prevention: Always confirm deletions

### **Metadata Corruption**
- AI regenerates compliant YAML
- User validates corrected version

### **Merge Conflict**
- Present conflicted state to user
- User manually resolves
- AI implements resolution

---

## INTEGRATION

### **With [[System_Prompt_AI_Knowledge_Filler]]**
- Protocol enforced in all update operations
- Output rules still apply (Markdown only)

### **With [[Prompt_Engineering_Workflow]]**
- Validation stage includes protocol compliance
- Refinement loop uses merge strategies

### **With Version Control (Git)**
- Protocol complements, not replaces, version control
- Users should commit before major AI updates

---

## USAGE EXAMPLES

### **Example 1: Add New Section**

**Input:**
```
User: "Add OAuth 2.0 authentication flow to [[API Security Guide]]"
```

**AI Action:**
1. Opens file, reads existing content
2. Adds ## OAuth 2.0 Authentication section
3. Updates `updated: 2026-02-06`
4. Adds `oauth` tag
5. Adds `[[OAuth 2.0 Spec]]` to related
6. Outputs updated file

---

### **Example 2: Metadata Update**

**Input:**
```
User: "Mark [[Project Alpha]] as completed"
```

**AI Action:**
1. Updates `status: completed`
2. Updates `updated: 2026-02-06`
3. Outputs updated YAML + existing content

---

### **Example 3: Conflict Resolution**

**Input:**
```
User: "Add microservices recommendation to [[System Architecture]]"
Existing file: Recommends monolithic architecture
```

**AI Response:**
```
The file currently recommends monolithic architecture for small teams.

Options:
1. Replace with microservices recommendation
2. Add microservices as alternative approach
3. Add section on when to migrate

Which approach?
```

---

## ANTI-PATTERNS

### ❌ **Silent Deletion**
Never delete content without confirmation

### ❌ **Metadata Overwrite**
Never replace `created`, always preserve tags/links

### ❌ **Implicit Replacement**
"Add X" ≠ "Replace Y with X"

### ❌ **Structure Destruction**
Never break heading hierarchy or link structure

---

## CONCLUSION

This protocol ensures reliable, predictable, and reversible updates to Obsidian knowledge files while maintaining user control and system integrity.