# Rozhodovací tabulka

Pořadí kroků: **data → bloker → povinná nabídka / souhlas úřadu → možnost dalšího prodeje → kontrola vyloučení → verdikt**. První krok, který rozhodne, vyhrává; další se už nevyhodnocují, s jednou výjimkou (krok 2 hodnocení neukončí, jen zakáže `BUY_CANDIDATE`).

Zkratky zdrojů: **KN** = Nahlížení do KN (přihlášený uživatel), **MAP** = Mapy.com / ortofoto / mapa v Nahlížení do KN, **LPIS** = Veřejný registr půdy, **AOPK** = mapy AOPK, **ZONING** = územní plán (Národní geoportál územního plánování nebo web obce), **SELLER** = údaje od prodávajícího. Pole jsou z `input/schema.json`, povolené hodnoty v `docs/input_schema.md`.

## Kroky

| # | Otázka | Podmínka (pole vstupu) | Výsledek | Pokračovat? |
|---|---|---|---|---|
| 0 | Mám základní data? | `land_register.status != checked` nebo chybí `area_m2`, `land_type`, nebo `owners` je prázdné při `owners_visible = true` | **INSUFFICIENT_DATA** | ne |
| 1 | Brání něco prodeji? | jakýkoli `legal_flags[].type = block` | **BLOCKED** | ne |
| 2 | Musí se nejdřív nabídnout někomu jinému nebo získat souhlas? | `legal_flags[].type` ∈ {offer, consent} | zakáže `BUY_CANDIDATE`, nejlepší možný výsledek je **CONDITIONAL** | ano |
| 3 | Komu se dá prodat? | aspoň jedna položka `resale_options[]` | žádná možnost dalšího prodeje → **NOT_WORTH_IT** | ano, pokud nějaká existuje |
| 4 | Zůstane možnost dalšího prodeje nevyloučená? | každá možnost dalšího prodeje dostane `excluded` + `exclusion_reason` | všechny `excluded = true` → **NOT_WORTH_IT** | ano, pokud aspoň jedna zůstala |
| 5 | Chybí data, která by mohla výsledek zhoršit? | `missing_data[].impact` ∈ {could_block, could_require_offer, could_exclude_resale} | **CONDITIONAL** | ne |
| 6 | Našel krok 2 nabídku nebo souhlas, nebo je kupec jen odhadnutý? | krok 2 našel flag `offer` nebo `consent`, nebo nevyloučená možnost dalšího prodeje má `buyer = null`, nebo jediná nevyloučená možnost dalšího prodeje je `co_owners` | **CONDITIONAL** | ne |
| 7 | Zbytek | nevyloučená možnost dalšího prodeje s pojmenovaným kupcem, bez flagu `offer` nebo `consent`, bez rizikových chybějících dat | **BUY_CANDIDATE** | ne |

`could_reduce_value` v `missing_data` výsledek nemění, jen se propíše do výstupu.

## Krok 1: blokery

| Kód | Zdroj | Signál ve vstupu |
|---|---|---|
| `seal` | KN | `land_register.seal_present = true` (plomba: v katastru je vyznačeno, že u parcely probíhá řízení, které může změnit práva k ní) |
| `execution` | KN | `land_register.restrictions[].type` obsahuje "exekuc" |
| `insolvency` | KN | `land_register.restrictions[].type` obsahuje "insolvenc", "konkurs", "úpadk" |
| `alienation_ban` | KN | `land_register.restrictions[].type` obsahuje "Zákaz zcizení" |
| `dispute_note` | KN | `land_register.other_records[].type` obsahuje "spornost" nebo "žaloba" |
| `insufficiently_identified_owner` | KN | `land_register.owners[].insufficiently_identified = true` |
| `deceased_spouse_sjm` | SELLER | `seller_facts.deceased_owner_in_sjm = true` a `inheritance_proceedings_open = true` |
| `units_ownership` | KN | `land_register.owners[].relation_type` = "Vlastnictví jednotek" |

Bloker platí pro kteréhokoli vlastníka parcely, ne jen pro prodávajícího. Exekuce nebo insolvence zapsaná u spoluvlastníka tedy také končí výsledkem **BLOCKED**, protože zisk vzniká až prodejem celé parcely a zatížený podíl ho komplikuje.

## Krok 2: povinná nabídka a souhlas

| Kód | Typ | Zdroj | Signál | Komu |
|---|---|---|---|---|
| `state_nature_protection_61` | offer | AOPK + ZONING | `nature_protection.large_protected_area.type = NP` nebo `small_protected_area.type` ∈ {NPR, NPP} nebo `cave_related = true`, a zároveň `zoning.built_up_status != zastavěné území`; platí i při `parcel_only_partially_inside = true` (§ 61 zákona 114/1992 Sb.) | AOPK ČR / správa NP |
| `building_owner_3056` | offer | KN | `land_register.building.relation = Stavba na parcele` nebo `on_different_lv = true` (§ 3056 NOZ) | vlastník stavby |
| `registered_preemption` | offer | KN | `land_register.restrictions[].type` obsahuje "Předkupní právo" | oprávněný z LV |
| `municipality_or_region_101` | offer | ZONING | `zoning.preemption_right_101_holder != null` (starý § 101 stavebního zákona) | obec / kraj |
| `co_owners_inheritance_1124` | offer | SELLER | `seller_facts.inheritance_date` mladší než 6 měsíců a víc než jeden vlastník (§ 1124 NOZ) | ostatní spoluvlastníci |
| `land_consolidation` | consent | KN | `land_register.other_records[].type` obsahuje "pozemkové úpravy" | pozemkový úřad |

Pokud je zdroj potřebný pro některé z těchto pravidel `not_checked` (AOPK, územní plán, seller_facts), jde do `missing_data` s `could_require_offer`.

## Krok 3: možnosti dalšího prodeje

| `resale_type` | Zdroj | Signál | Kupec (`buyer`) |
|---|---|---|---|
| `road_class_2` / `road_class_3` | KN + MAP | `land_register.land.land_use = silnice`; třída z `map.adjacent_roads[].road_class` | kraj dle sídla KÚ |
| `local_road` | KN | `land_register.land.land_use = ostatní komunikace` | obec z `identification.municipality` |
| `co_owners` | KN | víc než jeden vlastník v `land_register.owners[]` mimo SJM | ostatní spoluvlastníci |
| `field_arable` | KN + LPIS | `land_register.land.land_type` zemědělský a `lpis.dpb_items[].culture = standardní orná půda` (nebo sem spadá zbytek: zahrada, úhor, ...) | `lpis.dpb_items[].user_name` |
| `field_grassland` | KN + LPIS | `lpis.dpb_items[].culture` je trvalý travní porost nebo travní porost | `lpis.dpb_items[].user_name` |
| `field_vineyard` | KN + LPIS | `lpis.dpb_items[].culture = vinice` | `lpis.dpb_items[].user_name` (vinař) |
| `field_orchard` | KN + LPIS | `lpis.dpb_items[].culture = ovocný sad` | `lpis.dpb_items[].user_name` (sadař) |
| `field_hopfield` | KN + LPIS | `lpis.dpb_items[].culture = chmelnice` | `lpis.dpb_items[].user_name` (chmelař) |
| `building_owner` | KN | stavba jiného vlastníka (`land_register.building.*`) | vlastník stavby |
| `forest` | KN + MAP | `land_register.land.land_type = lesní pozemek` | soused z `map.neighbouring_parcels[]` nebo `null` |

Jedna parcela může mít víc možností dalšího prodeje (podíl na poli = `co_owners` + `field_*`). Všechny se vypíší.

## Krok 4: co vyloučí možnost dalšího prodeje

| `exclusion_reason` | Možnost dalšího prodeje | Zdroj | Signál |
|---|---|---|---|
| `owner_is_buyer` | road_*, local_road | KN | vlastník v `land_register.owners[].name` je kraj / obec / stát |
| `clearcut` | forest | MAP | `map.orthophoto_land_cover = holina` |
| `no_access` | forest | MAP | `map.access_type = bez viditelného přístupu` |
| `no_lpis_user` | field_* | LPIS | `lpis.parcel_in_lpis = false` |

Pokud zdroj pro kontrolu vyloučení chybí (`not_checked`), možnost dalšího prodeje se nevylučuje, ale údaj jde do `missing_data` s `could_exclude_resale`, což v kroku 5 dá CONDITIONAL.

## Co se nesbírá a proč

- **Záplavy, BPEJ, zástavy, pacht, CHKO a Natura 2000:** jen snižují hodnotu, verdikt nemění. Kontrolující člověk je uvidí na LV, model je nehodnotí.
- **Souhlas s veřejným užíváním cesty (I. ÚS 2541/25):** z žádného zdroje nejde zjistit.
- **Podrobnosti stavby (č. p., typ):** pro rozhodnutí stačí, že stavba jiného vlastníka existuje.

## Příklady průchodu

| Parcela | Krok, který rozhodl | Verdikt |
|---|---|---|
| Zálesní Lhota 1292/2 (silnice, vlastník kraj) | 4: `owner_is_buyer` | NOT_WORTH_IT |
| Silnice III. třídy, soukromý vlastník, čistý LV, mapa `checked`, celá pod silnicí | 7 | BUY_CANDIDATE |
| Totéž, ale `map.status = not_checked` | 5: `map.adjacent_roads` je `could_reduce_value`, nic rizikového → 7 | BUY_CANDIDATE s poznámkou v `missing_data` |
| Pole s uživatelem v LPIS, LPIS `not_checked` | 5: `could_exclude_resale` | CONDITIONAL |
| Podíl 1/48, dědictví před 2 měsíci | 2 + 6 | CONDITIONAL |
| Louka v NP mimo zastavěné území | 2 + 6 | CONDITIONAL |
| Les, holina, bez přístupu | 4 | NOT_WORTH_IT |
| Cokoli s plombou | 1 | BLOCKED |
| `land_register.status = not_checked` | 0 | INSUFFICIENT_DATA |
