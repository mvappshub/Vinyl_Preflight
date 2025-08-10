---
type: "manual"
---

# AI Agent Rules – Augment Code

## 1. Zakázané chování
- Nikdy neopravuj kód, dokud neidentifikuješ **kořenovou příčinu** (chybová hláška + stack-trace).
- Žádné náhodné pokusy nebo metoda „pokus-omyl“.
- Nepoužívej neověřené blogy ani Stack Overflow před oficiální dokumentací.

## 2. Povinný postup při chybě
1. **Analýza** – přečti hlášku, izoluj řádek.
2. **Reprodukce** – ověř, že problém lze 100 % zopakovat.
3. **Context7** – spusť `use context7` s technologií, verzí a klíčovými slovy.
4. **Hypotéza** – napiš **jednu** testovatelnou hypotézu do chatu.
5. **Jedna změna** – proveď jednu minimální úpravu a okamžitě otestuj.
6. **Verifikace** – potvrď, že testy procházejí a nevznikla regrese.
7. **Dokumentace** – přidej komentář s URL z Context7 do kódu.

## 3. Priorita zdrojů
1. Oficiální dokumentace (via Context7)
2. Oficiální specifikace / RFC
3. Oficiální repozitář kódu
4. Vlastní pokus až po vyčerpání výše uvedených.

## 4. Komunikační standard
- Vždy vysvětli, **proč** jsi zvolil daný krok.
- Cituj zdroj (link) v komentáři nebo v chatu.
- Po každé opravě: commit message `fix(scope): popis – closes #iss`.

## 5. Kontext & paměť
- Respektuj pravidla v `.augment/rules.md` > globální uživatelská pravidla.
- Před refaktorem vytvoř `@augment checkpoint`.
- V jedné relaci řeš **pouze jednu** logickou úlohu.