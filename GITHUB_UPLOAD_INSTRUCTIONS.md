# GitHub Upload Instructions

Tento dokument obsahuje kroky pro upload projektu Vinyl Preflight na GitHub.

## 🚀 Příprava před uploadem

### 1. Vyčištění projektu
```bash
# Smazat cache a temporary soubory
rm -rf __pycache__/
rm -rf .pytest_cache/
rm -rf src/__pycache__/
rm -rf tests/__pycache__/

# Smazat output soubory (volitelné - můžete ponechat jako příklady)
# rm -rf output/*.csv
# rm -rf output/*.txt
```

### 2. Kontrola citlivých dat
- ✅ `.env` soubor je v `.gitignore`
- ✅ API klíče nejsou v kódu
- ✅ Testovací data nejsou zahrnuta
- ✅ `.env.example` je připraven

### 3. Finální test
```bash
# Spustit všechny testy
python -m pytest tests/ -v

# Zkontrolovat, že aplikace funguje
python src/vinyl_preflight_app.py
```

## 📋 Kroky pro GitHub upload

### 1. Vytvoření GitHub repository
1. Jděte na https://github.com
2. Klikněte na "New repository"
3. Název: `vinyl-preflight`
4. Popis: `Automated validation tool for vinyl record production materials`
5. Nastavte jako **Public** (nebo Private dle preference)
6. **NEVYTVÁŘEJTE** README, .gitignore nebo LICENSE (už je máme)

### 2. Inicializace Git repository (pokud ještě není)
```bash
# V root složce projektu
git init
git add .
git commit -m "Initial commit - Vinyl Preflight v2.5"
```

### 3. Připojení k GitHub
```bash
# Nahraďte YOUR_USERNAME svým GitHub username
git remote add origin https://github.com/YOUR_USERNAME/vinyl-preflight.git
git branch -M main
git push -u origin main
```

### 4. Aktualizace URL v souborech
Po vytvoření repository aktualizujte tyto soubory:

**README.md:**
```markdown
git clone https://github.com/YOUR_USERNAME/vinyl-preflight.git
```

**setup.py:**
```python
url="https://github.com/YOUR_USERNAME/vinyl-preflight",
```

**CONTRIBUTING.md:**
```markdown
git clone https://github.com/YOUR_USERNAME/vinyl-preflight.git
```

### 5. Commit aktualizací
```bash
git add README.md setup.py CONTRIBUTING.md
git commit -m "Update repository URLs"
git push
```

## 🔧 Nastavení GitHub repository

### 1. Repository Settings
- **Description:** "Automated validation tool for vinyl record production materials"
- **Website:** (volitelné)
- **Topics:** `vinyl`, `audio`, `validation`, `python`, `manufacturing`, `quality-control`

### 2. Branch Protection (doporučené)
1. Jděte do Settings → Branches
2. Přidejte rule pro `main` branch:
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging

### 3. Issues Templates
- ✅ Bug report template je připraven
- ✅ Feature request template je připraven

### 4. GitHub Actions
- ✅ CI workflow je připraven v `.github/workflows/ci.yml`
- Automaticky se spustí při push/PR

## 📊 Po uploadu

### 1. Vytvořte první Release
1. Jděte do Releases
2. Klikněte "Create a new release"
3. Tag: `v2.5.0`
4. Title: `Vinyl Preflight v2.5.0`
5. Popis: Zkopírujte z CHANGELOG.md

### 2. Nastavte README badges (volitelné)
Přidejte do README.md:
```markdown
![CI](https://github.com/YOUR_USERNAME/vinyl-preflight/workflows/CI/badge.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
```

### 3. Dokumentace
- README.md je hlavní dokumentace
- docs/ obsahuje detailní dokumentaci
- GitHub Wiki můžete použít pro další dokumentaci

## ✅ Checklist před uploadem

- [ ] Všechny testy procházejí
- [ ] .env soubor není v repository
- [ ] API klíče nejsou v kódu
- [ ] README.md je aktuální
- [ ] CHANGELOG.md je kompletní
- [ ] LICENSE je přítomen
- [ ] .gitignore je správně nastaven
- [ ] requirements.txt je aktuální
- [ ] GitHub Actions workflow je připraven

## 🎯 Po uploadu

1. **Sdílejte projekt** s komunitou
2. **Sledujte Issues** a Pull Requests
3. **Aktualizujte dokumentaci** dle potřeby
4. **Vydávejte nové verze** pravidelně

---

**Projekt je připraven pro GitHub! 🚀**
