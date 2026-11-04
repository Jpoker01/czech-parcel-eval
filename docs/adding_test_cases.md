# Jak přidat reálnou parcelu

Postup pro přidání nové reálné parcely do dev sady. Krok 2 je jádro, zbytek je podle toho, které zdroje case potřebuje (pole `status` v jednotlivých sekcích vstupu rozhoduje, které se doplňují).

## Postup

1. **Založit vstup a očekávaný výstup** - v `input/examples/<case_id>.json` (vstup) a `tests/expected/<case_id>.json` (očekávaný výstup) podle struktury `input/schema.json`. `case_id` je k. ú. a parcela malými písmeny bez diakritiky, podtržítka mezi slovy, pomlčka za lomítkem v parcelním čísle (např. `zalesni_lhota_1292-2`). Zdroje, které case potřebuje, mají `status = "checked"`, ostatní zůstávají `"not_checked"` - to je součást testu, model nemá dostat více, než má.
2. **Najít parcelu** - podle typu case (silnice, pole, les, pozemek pod stavbou, v NP, v exekuci atd.). [Mapy.com](https://mapy.com) vedou na leteckou mapu se zapnutou katastrální vrstvou; kliknutím na parcelu se zobrazí její číslo a k. ú. Vyhledávání Mapy.com parcelní číslo NENAJDE (najde jen obec), mapu je nutné posunout ručně. Pro exekuce [portaldrazeb.cz](https://www.portaldrazeb.cz) s filtrem kategorie "Pozemek" a druh "Exekuční dražba nedobrovolná".
3. **KN** - opsat údaje do vstupu, viz sekce "KN" níže.
4. **MAP / LPIS / AOPK / ZONING / SELLER** - jen pokud je příslušný zdroj u case označený `"checked"`. Viz samostatné sekce níže.
5. **Vyplnit očekávaný výstup**: `decision`, `legal_flags` (type, code, evidence), `resale_options` (resale_type, buyer, excluded, exclusion_reason, evidence) a `missing_data`. Evidence ve tvaru `"cesta = hodnota"` přesně podle vyplněného vstupu, jinak ji eval označí za chybu.
6. **Validovat** přes `uv run python tests/check_expected.py` nebo přímo `check_output(exp, inp, schema)` ze `src/parcel_eval/checks.py`. 7 pravidel konzistence musí projít.
7. **Datum a soukromí** - `meta.checked_at` nastavit na datum ověření KN. Pole `meta.notes` a `*.notes` NECHAT `null` - model je čte jako kontext a nesmí z nich poznat očekávanou odpověď. Jména fyzických osob anonymizovat jako `Osoba A`, `Osoba B` atd., obce / kraje / firmy nechat reálné.

Odhad času: 10 - 15 min na parcelu. Case 4, 5, 7, 12, 13 jdou najít najednou v jednom k. ú. v CHKO Moravský kras nebo CHKO Pálava.

## KN

Postup ověřený na Zálesní Lhotě 1292/2.

Před hledáním se přihlásit v [Nahlížení do KN](https://nahlizenidokn.cuzk.gov.cz) přes Identitu občana. Vpravo nahoře musí být vidět jméno, jinak se vlastníci nezobrazí a stránka často vyžaduje CAPTCHA.

**Vyhledání:**

- Odkaz "Vyhledat parcelu" otevře formulář. Do rámečku "Katastrální území" napsat název k. ú. a kliknout "Vyhledat". Když existuje víc stejnojmenných k. ú., vybrat to se správným okresem (je v závorce).
- "Druh číslování" nechat "Pozemková parcela" (pro parcely "st." přepnout na "Stavební parcela"). Do prvního políčka "Parcelní číslo" napsat číslo před lomítkem, do druhého číslo za lomítkem, kliknout "Vyhledat".

**Mapování polí KN → JSON vstup:**

| KN pole | JSON cesta | Poznámka |
|---|---|---|
| Obec | `identification.municipality` | Bez kódu v závorce ("Studenec") |
| Katastrální území | `identification.cadastral_area` | Bez kódu ("Zálesní Lhota"); kód (790591) se hodí pro LPIS |
| Parcelní číslo | `identification.parcel_number` | Včetně lomítka ("1292/2") |
| Číslo LV | `identification.lv_number` | Jako číslo (404) |
| Výměra [m²] | `land.area_m2` | Jako číslo (1416) |
| Druh pozemku | `land.land_type` | Doslova ("ostatní plocha") |
| Způsob využití | `land.land_use` | Doslova ("silnice"); když řádek chybí, `null` |

**Sekce "Vlastníci, jiní oprávnění"** → `owners`, jedna položka za každého vlastníka. Nadpis sloupce ("Vlastnické právo") do `relation_type`, jméno do `name`, podíl ze sloupce "Podíl" (prázdný = "1/1"). Adresa se NEOPISUJE. Fyzické osoby anonymizovat jako "Osoba A", "Osoba B"; obce, kraje a firmy nechat (model z nich pozná veřejného vlastníka). `owners_visible = true`.

SJM se v KN zobrazí jako dva vlastníci s jedním podílem a poznámkou "SJM"; do JSON jde JEDNA položka s `sjm = true` a `name = "Osoba A; Osoba B"`.

**Sekce "Omezení vlastnického práva"** → `restrictions`. Text "Nejsou evidována žádná omezení" znamená prázdný seznam; jinak každý řádek jako `{"type": "..."}` doslova, i ty u jiných spoluvlastníků.

**Sekce "Jiné zápisy"** → `other_records`, stejným způsobem. POZOR: "Exekuční příkaz k prodeji nemovitosti" a insolvenční zápisy bývají v Jiných zápisech, ne v Omezeních. Model to pozná z pravidla `execution` / `insolvency` v decision_table.

**Sekce "Způsob ochrany nemovitosti"** se NEOPISUJE, ale je to nápověda pro krok AOPK: NP / CHKO / NPR / NPP / PP / EVL se zapíše do `nature_protection`.

**Blok "Součástí je stavba" nebo "Stavba na parcele"** se ukáže jen u pozemku se stavbou → `building.relation` (nadpis bloku) a `on_different_lv = true`, když má stavba jiné LV než pozemek.

**`seal_present = true`** jen tehdy, když stránka ukazuje plombu (probíhající řízení), jinak `false`.

Status `land_register = "checked"`.

Užitečné odkazy na stránce parcely: "Sousední parcely" vypíše sousedy i s vlastníky (pro les do `map.neighbouring_parcels`) a "Zobrazení mapy" otevře katastrální mapu s parcelou vybarvenou modře.

## MAP

- Polohu parcely nejrychleji ukáže "Zobrazení mapy" ze stránky parcely v KN. Leteckou mapu tam zapnout přes dlaždici "KM" vlevo nahoře, volba "Katastrální mapa + ortofoto".
- Čísla silnic katastrální mapa neukazuje - jsou v [Mapy.com](https://mapy.com): najít obec, přiblížit stejné místo a opsat číslo z popisku silnice. Do `adjacent_roads` jako `{"road_number": "III/29317", "road_class": "III. třída"}`. Třída podle počtu číslic: 3 = II. třída, 4 - 5 = III. třída.
- `access_type` - čeho se parcela dotýká: `"silnice"`, `"místní komunikace"`, `"polní cesta"` nebo `"bez viditelného přístupu"`.
- `orthophoto_land_cover` - co je na letecké mapě: `"orná půda"`, `"louka"`, `"les"`, `"holina"`, `"zástavba"`, `"zarůstání"` nebo `"silnice"`.
- `neighbouring_parcels` - jen u lesa, z KN odkazu "Sousední parcely" (číslo + vlastník).

## LPIS

Otevřít [veřejný LPIS](https://mze.gov.cz/public/app/lpisext/lpis/verejny2/plpis/) v co nejširším okně. V úzkém okně hlásí "Podkladová vrstva není správně načtena".

- Vpravo panel "Vyhledávání", záložka "Parcela" (šipkou doprava, pokud není vidět). Do "Katastrální území" napsat název nebo šestimístný kód k. ú. z KN a vybrat ze seznamu. Do "Parcelní číslo" číslo před lomítkem, do "Poddělení parcelního čísla" číslo za lomítkem, kliknout "Vyhledat".
- Výsledek je v tabulce "Nalezené parcely" pod formulářem.
- Žádný DPB přes parcelu = `parcel_in_lpis = false`. Jinak za každý DPB opsat uživatele do `user_name` a kulturu doslova do `culture`.

## AOPK

- Odkaz "CHRÁNĚNÉ ÚZEMÍ" v hlavním README otevírá mapu jen Natura 2000, NE národní parky a CHKO. Pro ně použít mapový server AOPK [mapy.nature.cz](https://mapy.nature.cz).
- Nápovědu dává i KN, sekce "Způsob ochrany nemovitosti" (viz krok 3 výše).
- Zapsat typ velkoplošného území (`NP` / `CHKO`) a maloplošného (`NPR` / `PR` / `NPP` / `PP`) i s názvem, `parcel_only_partially_inside` a `cave_related`. Když parcelu nic nepřekrývá, typy zůstanou `null` a status `"checked"` znamená "nic tam není".

## ZONING

- Územní plán najít na [Národním geoportálu územního plánování](https://mapy.gov.cz/map) nebo na webu obce (hlavní výkres).
- `built_up_status` - jestli parcela leží v zastavěném území, zastavitelné ploše, ploše přestavby, nezastavěném území nebo územní rezervě.
- `preemption_right_101_holder` - `"obec"`, `"kraj"` nebo `"stát"`, jen když plán u parcely uvádí předkupní právo; jinak `null`.
- Obec bez územního plánu = `status = "not_available"` a důvod do `zoning.notes`.

## SELLER

Jediný neinternetový zdroj. Vyplňuje se jen u case, kde to case popis vyžaduje (typicky dědictví):

- `inheritance_date` - datum nabytí podílu děděním (§ 1124, nabídka spoluvlastníkům do 6 měsíců).

Jinak nechat `"not_checked"`.

## Otevřené

- **LPIS** - sekce vychází z částečného průchodu; doplnit, jak se z nalezené parcely dostat k DPB a kde je vidět "Uživatel" a "Kultura" (zatím není ověřené přímo v aplikaci).
- **AOPK** - aplikace [mapy.nature.cz](https://mapy.nature.cz) ještě není ověřená přímo v prohlížeči.
- **ZONING** - Národní geoportál územního plánování ještě není ověřený přímo v prohlížeči.
- **Plomba** - na reálné parcele zatím nebyla vidět, přesný vzhled stránky se zapnutou plombou je třeba doplnit.
