# Iterace promptu

## v0 (2026-11-02)

Výchozí verze. Přepis `docs/decision_table.md` do instrukcí, výstup podle `output/schema.json`.

Rozhodnutí v návrhu:
- Postup je explicitně číslovaný a krok, který rozhodne, ukončí hodnocení. Model tak nemá prostor "vyvažovat" blokery proti dobré možnosti dalšího prodeje.
- Tři statusy zdroje (`checked` / `not_checked` / `not_available`) a pravidlo "nikdy nepředpokládej příznivou hodnotu" jsou hned za popisem vstupu, protože to je nejčastější způsob, jak LLM selhává.
- Signály jsou napsané jako konkrétní testy na pole vstupu (`land_register.restrictions[].type` obsahuje "exekuc"), ne jako právní pojmy. Model nemusí znát české právo, stačí číst vstup.
- `evidence` ve tvaru `cesta = hodnota` je vynucené pravidlem i schématem, aby šlo strojově ověřit.
- Ceny jsou z promptu úplně vyloučené.

Očekávaná slabá místa (k ověření při iteracích):
- Volný text v `restrictions[].type` může mít varianty, které substring testy nechytí.
- Odvození kraje z katastrálního pracoviště je implicitní znalost, model ji může mít špatně.
- `co_owners` + `field_*` u podílu na poli: model může jednu z možností dalšího prodeje vynechat.
- Exekuce nebo insolvence u kteréhokoli spoluvlastníka je bloker, i když právně zasahuje jen jeho podíl. Zisk vzniká až prodejem celé parcely a zatížený podíl ho komplikuje. Cena: model zahodí i parcely, kde by šly koupit podíly ostatních spoluvlastníků.

Úpravy před prvním během (2026-11-04), po sběru reálných parcel:
- `execution` a `insolvency` čtou i `other_records`: KN eviduje "Exekuční příkaz k prodeji nemovitosti" v Jiných zápisech (Hamr nad Nežárkou 65/2), původní pravidlo jen nad `restrictions` by ho minulo.
- Krok 0 bere `area_m2 <= 0` jako chybějící data.
- `field_vineyard`, `field_orchard`, `field_hopfield` jako vlastní `resale_type` (Kobylí 8037 je vinice; jiný kupec i cena než orná půda).
- 6měsíční lhůta se počítá k `meta.checked_at`, ne k datu běhu, aby expected výstupy nestárly.

- Obecný `road` resale_type pro silnici s neověřenou mapou: kupec (kraj) je znám bez třídy, hádat `road_class_2` / `road_class_3` by tvrdilo víc, než je ve vstupu.

- Odstraněn bloker `deceased_spouse_sjm` a dopad `could_block`. Bloker stál jen na dvou booleanech od prodávajícího bez opory v KN a `could_block` neemitovalo žádné pravidlo. Platí tak jednoduché pravidlo: údaje od prodávajícího nikdy neblokují, nanejvýš přidají povinnou nabídku (§ 1124), a neověřený `seller_facts` dává `could_require_offer`.

Výsledek na dev sadě: zatím nespuštěno.

## v1 (2026-11-04)

Oprava jedné věty, která táhla model systematicky do CONDITIONAL.

v0 ř. 17 říkala "`null` uvnitř zdroje se statusem `checked` znamená 'toto pole nebylo zjištěno'. Zacházej s ním stejně jako s `not_checked`." Model podle toho flagoval každé prázdné pole v checked zdroji jako `could_require_offer`. V reálných datech ale `null` v checked zdroji skoro vždy znamená "ověřeno, nic tam není": `building.relation = null` u pole bez stavby, `preemption_right_101_holder = null` u obce, která § 101 nevymezuje.

Dopad na v0 (120 běhů):
- BUY_CANDIDATE recall 23 % (7 z 30 správně). Zbylých 23 skončilo jako CONDITIONAL s missing_data `building.relation`, `building.on_different_lv` nebo `preemption_right_101_holder`.
- CONDITIONAL precision 63 % (39 z 62 správně).
- Risky missing_data sedí jen v 70 % běhů.
- Konzistence 96 % v průměru, ale u problematických case model mezi 3 běhy osciluje (1/3 nebo 2/3).

Všechno ostatní bylo v pořádku: 0 rule violations, 0 evidence errors, BLOCKED a NOT_WORTH_IT 100 % precision i recall, legal flags 120/120, resale options 116/120.

Změna: `null` v checked zdroji nově znamená "zkontrolováno, prázdné". Do `missing_data` patří už jen pole ze zdroje `not_checked` nebo `not_available`. Přidán jeden konkrétní příklad se stavbou a § 101, aby model viděl obě typické situace.

Výsledek na dev sadě (120 běhů, claude-sonnet-5-5):
- Decision 119/120 (99 %, v0 bylo 81 %).
- Legal flags 120/120.
- Resale options 117/120.
- Risky missing data 110/120 (92 %, v0 bylo 70 %).
- Konzistence 39/40 unanimous, průměr 99 %.
- 0 rule violations, 0 evidence errors.
- BLOCKED a NOT_WORTH_IT 100 % precision a recall; BUY_CANDIDATE recall 97 % (v0 bylo 23 %).

Jediný špatný verdikt zbývá na `hrabesice_121-1` (2/3), kde model občas váhá u parcely v SJM se zástavami. Není to opakující se vzor přes další case, takže další iterace by znamenala overfitting na jeden hraniční jev. v1 jde jako finální prompt na holdout.
