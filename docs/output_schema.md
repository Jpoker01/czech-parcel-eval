# Výstupní schéma

`output/schema.json` (JSON Schema 2020-12, `additionalProperties: false`, posílá se do API jako `output_config.format`). Vzorový očekávaný výstup: `tests/expected/zalesni_lhota_1292-2.json`.

## Šest polí

| Pole | Fáze | Obsah |
|---|---|---|
| `decision` | verdikt | BLOCKED / CONDITIONAL / BUY_CANDIDATE / NOT_WORTH_IT / INSUFFICIENT_DATA |
| `legal_flags[]` | 1 | `type` block / offer / consent, `code`, `evidence` |
| `exits[]` | 2 + 3 | `exit_type` (klíč do `pricing.yaml`), `buyer`, `killed`, `kill_reason`, `evidence` |
| `missing_data[]` | průřezové | `field` ze vstupu, `impact` |
| `confidence` | verdikt | high / medium / low |
| `reasoning` | verdikt | max 4 věty česky |

Co model nevrací, protože to spočítá Python ze vstupu nebo z configu: ceny, velikost podílu, počet vlastníků, druh parcely, podmínky k ověření (plynou z `legal_flags` a `missing_data`).

## Proč tyto tři konstrukce

- **Enumy všude.** Eval porovnává množiny kódů, ne volný text, a konzistenci mezi běhy jde měřit.
- **`evidence` u každého závěru** ve tvaru `cesta = hodnota`. Eval ověří, že cesta ve vstupu existuje a hodnota sedí. Model si tak nemůže domyslet omezení, kupce ani zákaz.
- **`exit_type` místo ceny.** Model řekne, komu se dá prodat; cenu doplní `pricing.yaml`. Parametry jde přepsat bez změny promptu.

## Pravidla konzistence (kontroluje Python po každém běhu)

1. `legal_flags` obsahuje `block` ⇔ `decision = BLOCKED`.
2. `legal_flags` obsahuje `offer` nebo `consent` ⇒ `decision` není `BUY_CANDIDATE`.
3. `decision = BUY_CANDIDATE` ⇒ aspoň jeden exit `killed = false` s `buyer != null` a v `missing_data` nic s `could_block` ani `could_kill_exit`.
4. `decision = NOT_WORTH_IT` ⇒ všechny exity `killed = true` (nebo žádný exit) a v `missing_data` nic s `could_kill_exit`.
5. `decision = INSUFFICIENT_DATA` ⇔ `cadastre.status != checked` nebo chybí výměra, druh pozemku či vlastníci.
6. Každé `evidence` ukazuje na existující pole vstupu a hodnota se shoduje.
7. `killed = true` ⇔ `kill_reason != null`.

Cokoli jiného je CONDITIONAL. Porušení pravidla se v evalu počítá jako nekonzistence běhu.
