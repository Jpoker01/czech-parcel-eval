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

## Doplněk `other_findings` (2026-11-04)

Enumy pokrývají jen to, co umím předem definovat. `run.py --other-findings vN` připojí k v1 doplněk `prompts/addons/other_findings_vN.md` a do schématu povinné pole `other_findings[]` (risk / opportunity, jedna věta s polem vstupu). Pole se nehodnotí a nesmí měnit verdikt. Čte ho člověk a opakující se nálezy se stanou novými kategoriemi. Základní prompt v1 ani expected výstupy se nemění.

Doplněk v1, běh na dev sadě (120 běhů, claude-sonnet-5-5, `runs/v1_findings_v1/`) proti v1:
- Decision 119/120, legal flags 120/120, konzistence 39/40, 0 chyb. Shodné s v1.
- **Resale options 106/120 (v1 117/120).** Všech 11 ztracených běhů jsou BLOCKED case (exekuce, zákaz zcizení, poznámka spornosti, prompt injection), kde model i přes "vrať BLOCKED a skonči" vypsal možnost dalšího prodeje, nejčastěji `road_class_3`. Instrukce "zapiš všechno, co vidíš" oslabila ukončení v kroku 1.
- Risky missing data 108/120 (v1 110/120), po jednom běhu u dvou NOT_WORTH_IT case. Na tomto vzorku k nerozlišení od náhody.
- 83 nálezů (63 rizik, 20 příležitostí) ve 24 ze 40 case. 67 ze 120 běhů vrátilo prázdný seznam, takže model pole nevyplňuje za každou cenu.

Doplněk v2: výslovně říká, že u `BLOCKED` zůstává `resale_options` prázdné a zjištění se zapisují i tak.

Výsledek doplňku v2 (`runs/v1_findings_v2/`, 120 běhů) proti v1:
- Resale options 119/120 (v1 117/120, doplněk v1 106/120). Regrese u BLOCKED je pryč.
- Risky missing data 111/120 (v1 110/120), konzistence 40/40 unanimous, 0 chyb.
- **Decision 117/120 (v1 119/120).** Jediný rozdíl je `hrabesice_121-1`: 3/3 CONDITIONAL místo 2/3 BUY_CANDIDATE. Ve všech třech bězích model dává `seller_facts.inheritance_date` jako `could_require_offer` a odvolává se na § 1124, přestože vlastníkem je jedna položka v SJM. Nálezy v `reasoning` nefigurují, takže verdikt neovlivnily přímo.
- 122 nálezů (88 rizik, 34 příležitostí) ve 27 ze 40 case, 50 ze 120 běhů s prázdným seznamem.

Příčina `hrabesice_121-1` je v základním promptu: pravidlo pro `co_owners_inheritance_1124` (v1 ř. 55) říká "víc než jednoho vlastníka" bez upřesnění, že SJM manželů je jedna položka. Upřesnění má jen řádek `co_owners` (ř. 70). Stejnou chybu udělal model už ve v1 v jednom běhu ze tří. Doplněk ji jen zviditelnil, protože z kolísání 1/3 se stal stabilní výsledek 3/3.

### Backlog taxonomie z nálezů

Nálezy, které se opakují nebo pojmenovávají skutečnou mezeru. Do decision table se nepromítají před holdoutem, protože každý nový `code` znamená novou verzi promptu.

- **Obec jako prodávající (§ 39 zákona o obcích).** Převod obecního majetku vyžaduje zveřejnění záměru a usnesení zastupitelstva (Slatina 2952/5, Statutární město Brno, 2/3 běhů). Kandidát na `consent` flag.
- **Rozpor zdrojů.** Ortofoto ukazuje louku u `land_use = ostatní komunikace` (Plumlov 1183/3, 3/3), druh pozemku v KN neodpovídá kultuře v LPIS (`syn_field_kn_vs_lpis_conflict`, 3/3). Kandidát na `missing_data` s novým dopadem, nebo na samostatný kód "zdroje si odporují".
- **Oprávněný z předkupního práva není ve vstupu** (`syn_road_registered_preemption`, 3/3). Mezera ve vstupním schématu: `restrictions[]` ukládá jen typ, ne oprávněného.
- **Les zvláštního určení** ("les jiný než hospodářský", Horní Malá Úpa 310/1, 3/3). Omezuje hospodaření a tím okruh kupců lesa.

Nálezy, které taxonomii nerozšíří: zástavní práva, pacht (uživatel v LPIS není vlastník), roztříštěné podíly a administrativní zápisy (změna číslování, obnova operátu) verdikt záměrně nemění (`docs/decision_table.md`, "Co nemění verdikt"). Část nálezů opakuje obsah ostatních polí, tedy porušuje pravidlo 3 doplňku. Detekce prompt injection v `notes` (3/3) je užitečná jako signál pro ruční kontrolu vstupu.

## v2 (2026-11-04)

Upřesnění jednoho pravidla, které odhalil běh s doplňkem `other_findings` v2 (`hrabesice_121-1`, viz výše).

Ve v1 pravidlo pro `co_owners_inheritance_1124` říkalo "parcela má víc než jednoho vlastníka". U SJM manželů model počítal dva vlastníky, a protože `seller_facts` nebyl zkontrolovaný, dával `could_require_offer` a výsledek CONDITIONAL. SJM ale není podílové spoluvlastnictví a § 1124 se na manžele nevztahuje. Upřesnění "SJM je jedna položka" měl jen řádek `co_owners`.

Změny:
- Pravidlo § 1124 teď testuje počet položek v `land_register.owners` se stejným upřesněním pro SJM jako `co_owners`.
- Věta o `not_checked` zdrojích říká, že `seller_facts` je potřeba jen pro § 1124, tedy jen u víc než jedné položky vlastníků.
- Stejné upřesnění v `docs/decision_table.md`.
- Pravidlo pro výstup 4 si odporovalo s pravidlem o `not_checked` zdrojích v kroku 2: jedno říkalo "jen co může změnit výsledek", druhé "každý neověřený zdroj, který pravidlo potřebuje". Nově platí: u `CONDITIONAL` a `BUY_CANDIDATE` se uvede každý neověřený zdroj, který může přidat povinnou nabídku nebo souhlas, i když je výsledek už `CONDITIONAL` kvůli jinému flagu. Účel `missing_data` je říct člověku, co zbývá ověřit, ne jen zdůvodnit verdikt. U `BLOCKED` a `NOT_WORTH_IT` se nic dalšího neověřuje.

Opravy expected výstupů podle tohoto pravidla (kontrolní skript nad všemi case, model obojí vracel 3/3 už ve v1):
- `horni_mala_upa_310-1`: dva spoluvlastníci a neověřený `seller_facts`, doplněn `seller_facts` s `could_require_offer` (§ 1124).
- `slatina_2952-5`: neověřené `nature_protection` a `zoning`, doplněny s `could_require_offer` (§ 61, § 101).

Obě opravy mění jen `risky_missing_data`, verdikt zůstává CONDITIONAL. Skóre v0 a v1 výše platí pro původní expected výstupy. Proti opraveným expected mají v1 i `v1_findings_v2` risky missing data 116/120, ostatní čísla beze změny.

Výsledek na dev sadě (`runs/v2_findings_v2/`, prompt v2 + doplněk `other_findings` v2, 120 běhů, claude-sonnet-5-5):
- Decision 120/120, legal flags 120/120, resale options 120/120, risky missing data 120/120.
- Konzistence 40/40 unanimous, 0 rule violations, 0 evidence errors.
- Precision a recall 100 % u všech pěti verdiktů.
- Proti `v1_findings_v2` se změnily jen čtyři case: `hrabesice_121-1` (BUY_CANDIDATE 3/3, oprava SJM), `horni_mala_upa_310-1` a `slatina_2952-5` (risky missing data po opravě expected) a `uhrice_u_kyjova_2020-5` (resale options 3/3, dřív 2/3).
- 85 nálezů (70 rizik, 15 příležitostí) ve 26 ze 40 case, 66 ze 120 běhů s prázdným seznamem. Žádný nález nezpochybňuje verdikt. U `syn_prompt_injection` model ve všech třech bězích označil text v `notes` jako pokus o manipulaci.

Plné skóre na dev sadě po iteraci samo o sobě nic nedokazuje: prompt i dva expected výstupy byly upravené podle chyb, které tato sada ukázala. Proto jde v2 jako finální verze na holdout a po holdoutu se už nemění.

