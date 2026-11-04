# Výstupní schéma

`output/schema.json` (JSON Schema 2020-12, `additionalProperties: false`, posílá se do API jako `output_config.format`). Vzorový očekávaný výstup: `tests/expected/zalesni_lhota_1292-2.json`.

## Šest polí

| Pole | Krok | Obsah |
|---|---|---|
| `decision` | verdikt | BLOCKED / CONDITIONAL / BUY_CANDIDATE / NOT_WORTH_IT / INSUFFICIENT_DATA |
| `legal_flags[]` | kroky 1 + 2 | `type` block / offer / consent, `code`, `evidence` |
| `resale_options[]` | kroky 3 + 4 | `resale_type`, `buyer`, `excluded`, `exclusion_reason`, `evidence` |
| `missing_data[]` | průřezové | `field` ze vstupu, `impact` |
| `confidence` | verdikt | high / medium / low |
| `reasoning` | verdikt | max 4 věty česky |

Co model nevrací, protože to spočítá Python ze vstupu nebo z configu: ceny, velikost podílu, počet vlastníků, druh parcely, podmínky k ověření (plynou z `legal_flags` a `missing_data`).

## Proč tyto tři konstrukce

- **Enumy všude.** Eval porovnává množiny kódů, ne volný text, a konzistenci mezi běhy jde měřit.
- **`evidence` u každého závěru** ve tvaru `cesta = hodnota`. Eval ověří, že cesta ve vstupu existuje a hodnota sedí. Model si tak nemůže domyslet omezení, kupce ani zákaz.
- **`resale_type` místo ceny.** Model řekne jen, komu se dá prodat. Cenu nikdy neodhaduje, z paměti by si ji vymyslel.

## Pravidla konzistence

Python po každém běhu ověří, že si výstup sám neodporuje. Výstup přitom nesrovnává s očekávaným výstupem, takže pravidla fungují i u parcely, ke které očekávaný výstup neexistuje. Každé porušení se v reportu počítá jako nekonzistentní běh.

1. **Bloker a `BLOCKED` jdou vždy spolu.** Když `legal_flags` obsahuje flag s `type = block`, musí být `decision = BLOCKED`. Naopak `BLOCKED` musí mít aspoň jeden takový flag.
2. **Nabídka nebo souhlas vylučují `BUY_CANDIDATE`.** Když `legal_flags` obsahuje flag s `type = offer` nebo `consent`, `decision` nesmí být `BUY_CANDIDATE`.
3. **`BUY_CANDIDATE` potřebuje kupce a žádná riziková chybějící data.** Aspoň jedna možnost dalšího prodeje musí mít `excluded = false` a vyplněný `buyer`. `missing_data` nesmí obsahovat `could_require_offer` ani `could_exclude_resale`.
4. **`NOT_WORTH_IT` znamená, že parcelu není komu prodat.** Všechny možnosti dalšího prodeje musí mít `excluded = true`, nebo žádná neexistuje. `missing_data` nesmí obsahovat `could_exclude_resale`, protože pak vyloučení není jisté.
5. **`INSUFFICIENT_DATA` právě tehdy, když chybí základní data.** Python ze vstupu vyhodnotí podmínku kroku 0 z `docs/decision_table.md`. Když platí, musí být `decision = INSUFFICIENT_DATA`. Když neplatí, nesmí.
6. **Každý důkaz sedí se vstupem.** Každé `evidence` ve tvaru `cesta = hodnota` musí ukazovat na pole, které ve vstupu existuje, a hodnota se musí shodovat.
7. **Vyloučená možnost prodeje má důvod, nevyloučená ne.** `excluded = true` musí mít vyplněný `exclusion_reason`. `excluded = false` musí mít `exclusion_reason = null`.

`CONDITIONAL` nemá vlastní pravidlo. Platí pro něj jen obecná pravidla 1, 5, 6 a 7.

## Volitelné pole `other_findings`

Enumy pokrývají jen to, co umím předem definovat, a seznam rizik a příležitostí není úplný. `run.py --other-findings v2` proto ke schématu přidá povinné pole `other_findings[]` (`type` risk / opportunity, `description` jedna věta česky s polem vstupu) a k promptu doplněk `prompts/addons/other_findings_v2.md`. Doplněk se verzuje stejně jako prompt. Základní `output/schema.json`, verze promptů ani očekávané výstupy se nemění, běh se uloží do `runs/<prompt>_findings_<doplněk>/`, např. `runs/v1_findings_v2/`.

- **Nemění verdikt.** `decision`, `legal_flags`, `resale_options`, `missing_data` a `confidence` se dál řídí jen kroky 0 až 7. Metriky tak zůstávají deterministické a nález bez kategorie nesníží skóre.
- **Nehodnotí se.** Eval ho nesrovnává s očekávaným výstupem a pravidla konzistence ho nečtou. Kontroluje se jen tvar podle schématu.
- **Čte ho člověk.** Report vypíše všechny nálezy po případech a označí případy, kde se `decision` liší od očekávaného. Tam může nález ukazovat na mezeru v taxonomii místo chyby modelu. Nález, který se opakuje, se stane novým `code` nebo `resale_type` a promítne se do decision table, promptu a očekávaných výstupů.
