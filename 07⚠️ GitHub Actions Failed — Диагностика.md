## ⚠️ GitHub Actions Failed — Диагностика

Validation workflow упал. Нужно исправить. Это нормально при первом push.

---

## Проверка Проблемы

```bash
cd /storage/emulated/0/Download/ai-knowledge-filler

# 1. Проверить что скрипт существует
ls -la Scripts/validate_yaml.py
```

```bash
# 2. Проверить workflow файл
cat .github/workflows/validate-metadata.yml
```

---

## Скорее всего проблема в одном из:

1. **Путь к скрипту неправильный** в workflow
2. **Скрипт не скопирован** в Scripts/
3. **requirements.txt отсутствует**

---

## Быстрый Fix

### Вариант А: Если скрипт НЕ скопирован

```bash
# Скопировать скрипт
cp ../AKF_Vault/03-Scripts/validate_yaml.py Scripts/

# Проверить
ls -la Scripts/validate_yaml.py
```

### Вариант Б: Исправить workflow (если путь неправильный)

```bash
# Открыть workflow
cat .github/workflows/validate-metadata.yml | grep "python"
```

Должно быть:
```yaml
- name: Run YAML validator
  run: python Scripts/validate_yaml.py
```

Если там `python validate_yaml.py` (без Scripts/), то исправить:

```bash
cat > .github/workflows/validate-metadata.yml << 'EOF'
name: Validate Metadata

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pyyaml
        
    - name: Run YAML validator
      run: python Scripts/validate_yaml.py
EOF
```

---

## Commit и Push Fix

```bash
# Добавить изменения
git add Scripts/validate_yaml.py .github/workflows/validate-metadata.yml

# Commit
git commit -m "Fix: Update validation workflow path"

# Push
git push
```

---

## Проверить Результат

**Через 1-2 минуты:**

**🌐 Открой:** https://github.com/petrnzrnk-creator/ai-knowledge-filler/actions

Workflow должен запуститься автоматически и показать ✅ Success.

---

## Временное Решение (Опционально)

Если хочешь пока отключить validation:

```bash
# Удалить workflow временно
rm .github/workflows/validate-metadata.yml

# Commit
git add .github/workflows/validate-metadata.yml
git commit -m "Temporarily disable validation workflow"
git push
```

Потом можно вернуть позже.

---

**Какой вариант выбираешь?**

A) Исправить workflow (рекомендую)  
B) Временно отключить  
C) Сначала проверить что там в Scripts/

Напиши букву — дам точные команды.