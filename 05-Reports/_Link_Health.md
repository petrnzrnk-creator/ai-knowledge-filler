---
title: "Link Health Dashboard"
type: reference
domain: knowledge-management
status: active
tags: [dashboard, maintenance]
created: 2026-02-11
updated: 2026-02-11
---

## 🎯 Goal
Identify 5-10 most valuable links to add this week.

---

## ⚠️ Orphaned Files (Zero Incoming Links)

```dataview
TABLE 
  file.link as "File",
  domain as "Domain",
  type as "Type",
  created as "Created"
FROM "/"
WHERE file.name != "_Link_Health"
AND !contains(file.folder, ".obsidian")
SORT created DESC
LIMIT 15
FLATTEN 
  length(file.inlinks) as incount
WHERE incount = 0
```

## 🔗 Same Domain, Not Linked

```dataview
TABLE WITHOUT ID
  domain as "Domain",
  length(rows) as "Files",
  choice(length(rows) > 3, "❌ Review", "✅ OK") as "Status"
FROM "/"
WHERE domain
GROUP BY domain
SORT length(rows) DESC
```

## 📊 Quick Stats

```dataviewjs
const pages = dv.pages().where(p => !p.file.path.includes(".obsidian"));
const total = pages.length;
const withRelated = pages.where(p => p.related && p.related.length > 0).length;
const orphans = pages.where(p => p.file.inlinks.length === 0).length;

dv.paragraph(`
**Total Files:** ${total}  
**With Related Links:** ${withRelated} (${Math.round(withRelated/total*100)}%)  
**Orphaned:** ${orphans} (${Math.round(orphans/total*100)}%)  
**Target:** 80%+ files with related links
`);
```

---

## ✅ Weekly Action

**This Week's Focus:**
- [ ] Pick 3 orphaned files
- [ ] Add 2-3 related links each
- [ ] Update domain with most files

**Time Budget:** 15 minutes

**Next Review:** {date}
```

### Действие 1.2: Открой Dashboard

1. Создай файл
2. Открой Reading Mode
3. **Запиши:**
   - Сколько orphaned files?
   - Какие домены biggest clusters?
   - Сколько файлов with related links?

---

## PHASE 2: Manual Linking (1 неделя)

### Цель
Понять, **какие связи действительно ценны**.

### Week 1 Process

**Понедельник (15 мин):**
```markdown
1. Открой _Link_Health.md
2. Выбери 3 orphaned files из top domain
3. Для каждого:
   - Прочитай содержимое
   - Найди 2-3 релевантных файла ВРУЧНУЮ
   - Добавь в related: field
```

**Пример:**

```yaml
# File: API_Authentication.md
related:
  - [[API Design Principles]]  # Same domain
  - [[OAuth 2.0 Flow]]          # Related topic
  - [[Security Checklist]]      # Complementary type
```

**Пятница (5 мин):**
```markdown
1. Открой _Link_Health.md
2. Запиши изменения:
   - Orphans: 15 → 12 ✅
   - With related: 60% → 65% ✅
3. Заметки:
   - Какие связи оказались полезны?
   - Где тратил больше всего времени?
```

---

## PHASE 3: Measure Value (конец недели)

### Decision Point

**Ответь на вопросы:**

1. **Использовал ли новые links на этой неделе?**
   - ✅ Да, 3+ раза → Linking ценен, продолжаем
   - ❌ Нет → Останавливаемся, linking не priority

2. **Сколько времени потратил на linking?**
   - ⏱️ < 20 мин → OK, продолжаем manual
   - ⏱️ > 30 мин → Нужна automation

3. **Какой тип связей самый полезный?**
   - Same domain?
   - Same type?
   - Overlapping tags?

### Результат → Решение

**Сценарий A: Linking полезен + время OK**
→ Продолжаем manual еще неделю, refinement процесса

**Сценарий B: Linking полезен + time consuming**
→ Переходим к Phase 4 (QuickAdd automation)

**Сценарий C: Linking не используется**
→ Останавливаемся, фокус на другое

---

## PHASE 4: Automation (только если нужно)

### Trigger
Если в Phase 3 результат = **Сценарий B**.

### QuickAdd Setup (30 минут)

**Шаг 1: Установка**
```
Settings → Community Plugins → Browse
Search: "QuickAdd" → Install → Enable
```

**Шаг 2: Создай Macro**
```
Settings → QuickAdd → Manage Macros → Add Macro
Name: "Link Finder"
```

**Шаг 3: Создай файл скрипта**

**Путь:** `.obsidian/scripts/link-finder.js`

```javascript
module.exports = async (params) => {
    const { app, quickAddApi: qa } = params;
    const dv = app.plugins.plugins.dataview?.api;
    
    if (!dv) {
        new Notice("Enable Dataview plugin first");
        return;
    }
    
    const file = app.workspace.getActiveFile();
    if (!file) return;
    
    const metadata = app.metadataCache.getFileCache(file);
    const fm = metadata?.frontmatter || {};
    
    // Простой scoring
    const pages = dv.pages()
        .where(p => p.file.path !== file.path)
        .array();
    
    const scored = pages
        .map(p => {
            let score = 0;
            
            // Same domain = +3
            if (p.domain === fm.domain) score += 3;
            
            // Common tags = +1 each
            if (fm.tags && p.tags) {
                const common = fm.tags.filter(t => p.tags.includes(t));
                score += common.length;
            }
            
            return { page: p, score };
        })
        .filter(s => s.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, 8);
    
    if (scored.length === 0) {
        new Notice("No related files found");
        return;
    }
    
    // Multi-select UI
    const choices = scored.map(s => ({
        label: `${s.page.title} [${s.page.domain}] (${s.score} pts)`,
        value: s.page.file.name
    }));
    
    const selected = await qa.checkboxPrompt(
        "Add related links:",
        choices
    );
    
    if (!selected || selected.length === 0) return;
    
    // Update frontmatter
    await app.fileManager.processFrontMatter(file, (frontmatter) => {
        if (!frontmatter.related) frontmatter.related = [];
        
        selected.forEach(name => {
            const link = `[[${name.replace('.md', '')}]]`;
            if (!frontmatter.related.includes(link)) {
                frontmatter.related.push(link);
            }
        });
        
        // Update date
        frontmatter.updated = moment().format('YYYY-MM-DD');
    });
    
    new Notice(`Added ${selected.length} links`);
};
```

**Шаг 4: Добавь в QuickAdd**
```
Settings → QuickAdd → Manage Macros
Click "Link Finder" → Configure
User Scripts → Select link-finder.js → Save
```

**Шаг 5: Command Palette**
```
Settings → QuickAdd → Add Choice
Type: Macro
Name: "Find Related Links"
Select macro: Link Finder
Save → Add lightning icon (⚡)
```

### Использование

```
1. Открой файл
2. Cmd/Ctrl + P
3. Type: "Find Related"
4. Select links → Done
```

**Time:** 30 секунд vs 5 минут manual.

---

## PHASE 5: Iterate (ongoing)

### Week 2+

**Продолжаешь измерять:**

**Monday:**
- Use QuickAdd на 5 файлов (2 мин)
- Track: сколько links реально useful?

**Friday:**
- Dashboard review (2 мин)
- Adjust scoring если нужно

### Optimization Backlog

**Добавляй только if pain point:**

| Pain | Solution | Effort |
|------|----------|--------|
| Scoring неточный | Tune weights в скрипте | 15 мин |
| Хочу видеть suggestions автоматически | Weekly Review note | 30 мин |
| Нужно bulk update старых файлов | Batch script | 1 час |

---

## Lean Checklist

**Phase 1: MVP (Week 1)**
- [ ] Dashboard created
- [ ] Baseline metrics recorded
- [ ] 3 orphans manually linked
- [ ] Value assessment done

**Phase 2: Validation (Week 2)**
- [ ] Used new links 3+ times → ✅ Continue
- [ ] Time < 20 min/week → ✅ Manual OK
- [ ] OR Time > 30 min → 🤖 Automate

**Phase 3: Automation (If needed)**
- [ ] QuickAdd installed
- [ ] Script created
- [ ] Tested on 5 files
- [ ] Time reduced to <5 min/week

**Phase 4: Optimization (Optional)**
- [ ] Scoring tuned to preferences
- [ ] Batch update if needed
- [ ] Weekly review automated

---

## Success Metrics

**Week 1 Target:**
- 80%+ files have related links
- Orphans < 10% of vault
- Time investment < 20 min/week

**Week 2+ Target:**
- Links used 3+ times per week
- Manual work < 5 min/week (with automation)
- No regression in link quality

---

## When to STOP

**Red Flags:**
- Links not used for 2 weeks
- Process feels like busywork
- No navigation benefit noticed

**Action:** Pause, reassess if linking is priority.

---

## TL;DR: Your Next 30 Minutes

```markdown
1. Copy _Link_Health.md dashboard → 5 min
2. Open dashboard, record baseline → 2 min
3. Pick 3 orphaned files → 1 min
4. Manually add 2-3 links each → 15 min
5. Note which links feel valuable → 5 min
6. Calendar reminder: Friday review → 2 min
```

**Next Friday:**
- Dashboard shows progress
- Decide: continue manual OR add automation
