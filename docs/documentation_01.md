# Vinyl Preflight v1.0

**Vinyl Preflight** je sada nástrojů navržená pro automatickou kontrolu a validaci podkladů pro výrobu vinylových desek. Cílem je odhalit nesrovnalosti v délkách skladeb mezi dodaným tracklistem (PDF) a master audio soubory (WAV) ještě před tím, než se dostanou k operátorovi.

## Problém, který řešíme

V procesu přípravy vinylových desek se často vyskytují nesrovnalosti mezi časy uvedenými v tracklistu a skutečnou délkou audio nahrávek. Tyto chyby mohou vést ke zpoždění ve výrobě, nespokojenosti zákazníků a zvýšeným nákladům na opravy a komunikaci. Tento nástroj automatizuje detekci těchto chyb a umožňuje jejich rychlé řešení.

## Jak to funguje

Projekt se skládá ze tří samostatných, ale navazujících nástrojů:

1.  **WAV Data Extractor**: Projde zadané složky a archivy, najde všechny `.wav` soubory a vygeneruje strukturovaný soubor (`wav_data.json`) s jejich přesnými délkami.
2.  **PDF Data Extractor**: Projde stejné složky a archivy, najde všechny `.pdf` soubory a pomocí umělé inteligence (LLM) z nich extrahuje informace o skladbách (strana, název, délka) do souboru `pdf_data.json`.
3.  **Preflight Validator**: Načte oba vygenerované `.json` soubory a pro každý titul (archiv) pošle data LLM, která provede expertní porovnání a vygeneruje finální report o nalezených neshodách.