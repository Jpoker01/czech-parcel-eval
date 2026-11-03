# Iterace promptu

## v0 (2026-11-02)

Výchozí verze. Přepis `docs/decision_table.md` do instrukcí, výstup podle `output/schema.json`.

Rozhodnutí v návrhu:
- Postup je explicitně číslovaný a krok, který rozhodne, ukončí hodnocení. Model tak nemá prostor "vyvažovat" blokery proti dobrému exitu.
- Tři statusy zdroje (`checked` / `not_checked` / `not_available`) a pravidlo "nikdy nepředpokládej příznivou hodnotu" jsou hned za popisem vstupu, protože to je nejčastější způsob, jak LLM selhává.
- Signály jsou napsané jako konkrétní testy na pole vstupu (`land_register.restrictions[].type` obsahuje "exekuc"), ne jako právní pojmy. Model nemusí znát české právo, stačí číst vstup.
- `evidence` ve tvaru `cesta = hodnota` je vynucené pravidlem i schématem, aby šlo strojově ověřit.
- Ceny jsou z promptu úplně vyloučené.

Očekávaná slabá místa (k ověření při iteracích):
- Volný text v `restrictions[].type` může mít varianty, které substring testy nechytí.
- Odvození kraje z katastrálního pracoviště je implicitní znalost, model ji může mít špatně.
- `co_owners` + `field_*` u podílu na poli: model může jeden z exitů vynechat.
- Rozlišení "exekuce na prodávajícího" vs. "na jiného spoluvlastníka" vyžaduje čtení `beneficiary`, které ve vstupu nemusí být vyplněné.

Výsledek na dev sadě: zatím nespuštěno.
