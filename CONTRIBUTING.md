# Contributing to Vinyl Preflight

Děkujeme za váš zájem o přispívání do projektu Vinyl Preflight! Tento dokument obsahuje pokyny pro přispěvatele.

## 🚀 Jak začít

1. **Fork repository** na GitHubu
2. **Clone** váš fork lokálně:
   ```bash
   git clone https://github.com/mvappshub/vinyl-preflight.git
   cd vinyl-preflight
   ```
3. **Vytvořte virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # nebo
   venv\Scripts\activate     # Windows
   ```
4. **Nainstalujte závislosti**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   ```

## 🔧 Vývojové prostředí

### Spuštění testů
```bash
# Všechny testy
pytest tests/ -v

# S pokrytím kódu
pytest tests/ --cov=src --cov-report=html

# Konkrétní test
pytest tests/test_vinyl_preflight.py::TestPreflightProcessor::test_empty_directory -v
```

### Kontrola kvality kódu
```bash
# Formátování (pokud máte black)
black src/ tests/

# Linting (pokud máte flake8)
flake8 src/ tests/
```

## 📝 Pravidla pro přispívání

### Git workflow
1. Vytvořte novou branch pro vaši funkci:
   ```bash
   git checkout -b feature/amazing-feature
   ```
2. Proveďte změny a commitujte:
   ```bash
   git add .
   git commit -m "Add amazing feature"
   ```
3. Push do vašeho forku:
   ```bash
   git push origin feature/amazing-feature
   ```
4. Otevřete Pull Request

### Commit zprávy
- Používejte anglické commit zprávy
- Začněte s velkým písmenem
- Používejte imperativ ("Add feature" ne "Added feature")
- Buďte struční ale popisní

Příklady:
```
Add support for MP3 files
Fix WAV duration calculation bug
Update README with installation instructions
Refactor PDF extraction logic
```

### Kódovací standardy
- **Python 3.8+** kompatibilita
- **PEP 8** style guide
- **Type hints** kde je to možné
- **Docstrings** pro všechny veřejné funkce
- **Error handling** - vždy ošetřete výjimky
- **Logging** místo print statements

### Testování
- **Všechny nové funkce musí mít testy**
- **Testy musí projít** před odesláním PR
- **Pokrytí kódu** by mělo zůstat vysoké
- **Testujte edge cases** a error conditions

## 🐛 Hlášení chyb

Při hlášení chyby prosím uveďte:

1. **Verzi aplikace**
2. **Operační systém**
3. **Python verzi**
4. **Kroky k reprodukci**
5. **Očekávané chování**
6. **Skutečné chování**
7. **Error logy** (pokud existují)

Použijte template:
```markdown
**Verze:** v2.5
**OS:** Windows 10
**Python:** 3.9.7

**Kroky k reprodukci:**
1. Spustit aplikaci
2. Vybrat složku s...
3. Kliknout na...

**Očekávané chování:**
Aplikace by měla...

**Skutečné chování:**
Aplikace místo toho...

**Error log:**
```
[vložte error log zde]
```
```

## 💡 Návrhy nových funkcí

Před implementací nové funkce:

1. **Otevřete Issue** s popisem funkce
2. **Diskutujte** s maintainery
3. **Počkejte na schválení** před začátkem práce

## 📚 Dokumentace

- **README.md** - základní informace a quick start
- **docs/** - detailní dokumentace
- **Docstrings** - dokumentace funkcí v kódu
- **Comments** - vysvětlení složité logiky

## 🎯 Priority pro přispívání

Aktuálně hledáme pomoc s:

1. **Podpora dalších audio formátů** (MP3, FLAC, AIFF)
2. **Vylepšení GUI** - modernější design
3. **Batch processing** - zpracování více projektů najednou
4. **Konfigurace** - nastavitelné tolerance, formáty výstupu
5. **Dokumentace** - více příkladů, tutoriály
6. **Testy** - rozšíření test coverage

## ❓ Otázky

Máte otázky? Kontaktujte nás:

- **GitHub Issues** - pro technické otázky
- **GitHub Discussions** - pro obecné diskuse

Děkujeme za váš čas a přispění! 🙏
