// QuickAdd Macro: Fix Related Links YAML
// Исправляет формат поля related для Obsidian Properties

module.exports = async (params) => {
    const { app, quickAddApi } = params;
    const { vault, metadataCache } = app;

    let filesProcessed = 0;
    let filesFixed = 0;
    let errors = [];

    const files = vault.getMarkdownFiles();
    
    new Notice(`Обработка ${files.length} файлов...`);

    for (const file of files) {
        try {
            filesProcessed++;

            let content = await vault.read(file);
            
            if (!content.startsWith('---')) {
                continue;
            }

            const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
            if (!frontmatterMatch) {
                continue;
            }

            const frontmatterText = frontmatterMatch[1];
            const fullFrontmatter = frontmatterMatch[0];
            
            if (!frontmatterText.includes('related:')) {
                continue;
            }

            const metadata = metadataCache.getFileCache(file)?.frontmatter;
            if (!metadata || !metadata.related) {
                continue;
            }

            let related = metadata.related;
            let needsFix = false;
            let fixedRelated = [];

            // Обработка строки или массива
            const relatedArray = Array.isArray(related) ? related : [related];
            
            for (const item of relatedArray) {
                let cleaned = String(item).trim();
                
                // Убрать существующие кавычки
                cleaned = cleaned.replace(/^["']|["']$/g, '');
                
                // Добавить [[]] если нет
                if (!cleaned.startsWith('[[')) {
                    cleaned = `[[${cleaned}]]`;
                    needsFix = true;
                } else if (!cleaned.endsWith(']]')) {
                    cleaned = `${cleaned}]]`;
                    needsFix = true;
                }
                
                // Убрать лишние скобки
                cleaned = cleaned.replace(/\[\[\[\[/g, '[[').replace(/\]\]\]\]/g, ']]');
                
                fixedRelated.push(cleaned);
            }

            if (needsFix || !Array.isArray(related)) {
                
                let newFrontmatterLines = frontmatterText.split('\n');
                let relatedStartIndex = -1;
                let relatedEndIndex = -1;

                // Найти блок related
                for (let i = 0; i < newFrontmatterLines.length; i++) {
                    const line = newFrontmatterLines[i];
                    
                    if (line.match(/^related:/)) {
                        relatedStartIndex = i;
                        
                        // Найти конец блока
                        if (line.trim() === 'related:') {
                            for (let j = i + 1; j < newFrontmatterLines.length; j++) {
                                const nextLine = newFrontmatterLines[j];
                                if (nextLine.trim().startsWith('-') || nextLine.trim() === '') {
                                    relatedEndIndex = j;
                                } else if (nextLine.trim() !== '' && !nextLine.startsWith(' ')) {
                                    break;
                                } else {
                                    break;
                                }
                            }
                        } else {
                            relatedEndIndex = i;
                        }
                        break;
                    }
                }

                if (relatedStartIndex === -1) {
                    errors.push(`${file.path}: Не удалось найти поле related`);
                    continue;
                }

                // КРИТИЧНО: Создать валидный YAML с кавычками
                const newRelatedLines = ['related:'];
                for (const link of fixedRelated) {
                    // Двойные кавычки для валидности YAML
                    newRelatedLines.push(`  - "${link}"`);
                }

                newFrontmatterLines.splice(
                    relatedStartIndex,
                    relatedEndIndex - relatedStartIndex + 1,
                    ...newRelatedLines
                );

                const newFrontmatter = `---\n${newFrontmatterLines.join('\n')}\n---`;
                const newContent = content.replace(fullFrontmatter, newFrontmatter);

                await vault.modify(file, newContent);
                filesFixed++;
            }

        } catch (error) {
            errors.push(`${file.path}: ${error.message}`);
        }
    }

    const summary = [
        `✅ Обработано: ${filesProcessed}`,
        `🔧 Исправлено: ${filesFixed}`,
        errors.length > 0 ? `⚠️ Ошибок: ${errors.length}` : ''
    ].filter(Boolean).join('\n');

    new Notice(summary, 5000);

    if (errors.length > 0) {
        console.log('=== ОШИБКИ ===');
        errors.forEach(err => console.log(err));
    }

    // Создать отчёт
    const reportContent = `# Related Links Fix Report

**Дата:** ${new Date().toISOString()}

## Статистика

- Обработано: ${filesProcessed}
- Исправлено: ${filesFixed}
- Ошибок: ${errors.length}

${errors.length > 0 ? `## Ошибки\n\n${errors.map(e => `- ${e}`).join('\n')}` : ''}

## Пример результата

\`\`\`yaml
related:
  - "[[Link 1]]"
  - "[[Link 2]]"
\`\`\`
`;

    const reportPath = `Related-Fix-Report-${Date.now()}.md`;
    try {
        await vault.create(reportPath, reportContent);
        new Notice(`📊 Отчёт: ${reportPath}`, 3000);
    } catch (e) {
        console.log('Report:', reportContent);
    }
};