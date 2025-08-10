# Vinyl Preflight v2.5

**Vinyl Preflight** je pokročilý nástroj pro automatickou kontrolu a validaci podkladů pro výrobu vinylových desek. Automaticky detekuje nesrovnalosti v délkách skladeb mezi tracklistem (PDF) a master audio soubory (WAV) s podporou pro různé formáty projektů.

## 🎯 Klíčové funkce

- **Automatická detekce módu projektu** - Individual tracks vs. Consolidated sides
- **Inteligentní párování souborů** - Pokročilé algoritmy pro spojení PDF a WAV
- **LLM-powered extrakce** - Využívá AI pro přesnou extrakci dat z PDF
- **Robustní error handling** - Odolnost vůči poškozeným souborům
- **Detailní logování** - Kompletní auditní stopa všech operací
- **GUI aplikace** - Uživatelsky přívětivé rozhraní
- **Podpora archivů** - ZIP a RAR soubory
- **Kompletní testování** - Pytest test suite

## 🚀 Rychlý start

### Instalace

```bash
git clone https://github.com/mvappshub/vinyl-preflight.git
cd vinyl-preflight
pip install -r requirements.txt
```

### Konfigurace

1. Vytvořte `.env` soubor:
```bash
OPENROUTER_API_KEY=your_api_key_here
```

2. Získejte API klíč z [OpenRouter](https://openrouter.ai/)

### Spuštění

```bash
python src/vinyl_preflight_app.py
```

## 📋 Jak to funguje

Aplikace automaticky:

1. **Skenuje projekty** - Najde všechny složky s PDF a WAV soubory
2. **Analyzuje WAV délky** - Přesně změří délku všech audio souborů
3. **Extrahuje PDF data** - Pomocí AI získá informace o skladbách z tracklistů
4. **Detekuje mód projektu** - Rozpozná Individual tracks vs. Consolidated sides
5. **Validuje shodu** - Porovná délky a vygeneruje detailní report

### Podporované módy

- **Individual Mode**: Každá skladba má vlastní WAV soubor
- **Consolidated Mode**: Jeden WAV soubor na stranu vinylu (Side A, B, C...)

## 📊 Výstupy

### CSV Report
Hlavní výstup obsahuje:
- Status validace (OK/FAIL)
- Porovnání délek PDF vs WAV
- Detailní informace o neshodách
- Zdroje dat (názvy souborů)

### Detailní Log
Kompletní auditní stopa obsahuje:
- Nalezené projekty a soubory
- LLM komunikaci (request/response)
- Extrahovaná data z PDF
- Výsledky validace
- Časové razítka všech operací

## 🧪 Testování

```bash
# Spuštění testů
pytest tests/ -v

# Spuštění s pokrytím
pytest tests/ --cov=src --cov-report=html
```

## 📁 Struktura projektu

```
vinyl-preflight/
├── src/
│   └── vinyl_preflight_app.py    # Hlavní aplikace
├── tests/
│   └── test_vinyl_preflight.py   # Test suite
├── output/                       # Výstupní soubory
├── docs/                         # Dokumentace
├── requirements.txt              # Závislosti
├── requirements-test.txt         # Test závislosti
└── README.md
```

## 🔧 Technické detaily

### Závislosti
- **Python 3.8+**
- **PyMuPDF** - PDF zpracování
- **soundfile** - WAV analýza
- **tkinter** - GUI
- **requests** - LLM komunikace
- **pytest** - testování

### API
Aplikace využívá OpenRouter API pro přístup k LLM modelům (Google Gemini 2.5 Flash).

## 🤝 Přispívání

1. Fork repository
2. Vytvořte feature branch (`git checkout -b feature/amazing-feature`)
3. Commit změny (`git commit -m 'Add amazing feature'`)
4. Push do branch (`git push origin feature/amazing-feature`)
5. Otevřete Pull Request

## 📝 Licence

Tento projekt je licencován pod MIT licencí - viz [LICENSE](LICENSE) soubor.

## 🆘 Podpora

Pro hlášení chyb nebo žádosti o nové funkce použijte [GitHub Issues](https://github.com/mvappshub/vinyl-preflight/issues).

## 📈 Changelog

### v2.5 (2025-01-08)
- ✅ Přidána podpora pro Consolidated mode
- ✅ Pokročilé párování WAV souborů
- ✅ Detailní logování do souborů
- ✅ Robustní error handling
- ✅ Kompletní test suite
- ✅ Optimalizace výkonu

### v2.0
- ✅ GUI aplikace
- ✅ Automatická detekce módu projektu
- ✅ LLM-powered PDF extrakce

### v1.0
- ✅ Základní funkcionalita
- ✅ WAV a PDF zpracování