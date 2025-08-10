# Vinyl Preflight v2.5 - Dokumentace

**Vinyl Preflight** je pokročilý nástroj pro automatickou kontrolu a validaci podkladů pro výrobu vinylových desek. Automaticky detekuje nesrovnalosti v délkách skladeb mezi tracklistem (PDF) a master audio soubory (WAV) s podporou pro různé formáty projektů.

## Nové funkce v v2.5

- **Automatická detekce módu projektu** - Individual tracks vs. Consolidated sides
- **Pokročilé párování souborů** - Inteligentní algoritmy pro spojení PDF a WAV
- **Detailní logování** - Kompletní auditní stopa všech operací
- **Robustní error handling** - Odolnost vůči poškozeným souborům
- **Kompletní testování** - Pytest test suite s vysokým pokrytím

## Problém, který řešíme

V procesu přípravy vinylových desek se často vyskytují nesrovnalosti mezi časy uvedenými v tracklistu a skutečnou délkou audio nahrávek. Tyto chyby mohou vést ke zpoždění ve výrobě, nespokojenosti zákazníků a zvýšeným nákladům na opravy a komunikaci. Tento nástroj automatizuje detekci těchto chyb a umožňuje jejich rychlé řešení.

## Jak to funguje

Aplikace je nyní integrovaná do jednoho nástroje, který automaticky:

1. **Skenuje projekty** - Najde všechny složky s PDF a WAV soubory
2. **Analyzuje WAV délky** - Přesně změří délku všech audio souborů
3. **Extrahuje PDF data** - Pomocí AI získá informace o skladbách z tracklistů
4. **Detekuje mód projektu** - Rozpozná Individual tracks vs. Consolidated sides
5. **Validuje shodu** - Porovná délky a vygeneruje detailní report

## Podporované módy

### Individual Mode
Každá skladba má vlastní WAV soubor. Typické pro:
- Kompilace s mnoha tracky
- Projekty s jednotlivými mastery

### Consolidated Mode
Jeden WAV soubor na stranu vinylu (Side A, B, C...). Typické pro:
- Albumy s kontinuálním flow
- Projekty s konsolidovanými mastery