# Rozhodovací tabulka

Pořadí kroků: **data → bloker → povinná nabídka / souhlas úřadu → exit → kill-check → verdikt**. První krok, který rozhodne, vyhrává; další se už nevyhodnocují, s jednou výjimkou (krok 2 jen nastaví strop a pokračuje se).

Faktory, které jen snižují hodnotu (zástava, pacht, Q100 mimo aktivní zónu...), model nehodnotí. Verdikt nemění a kontrolující člověk je uvidí na LV.

## Kroky

| # | Otázka | Podmínka (pole vstupu) | Výsledek | Pokračovat? |
|---|---|---|---|---|
| 0 | Mám základní data? | `cadastre.status != checked` nebo chybí `area_m2`, `land_type`, nebo `owners` je prázdné při `owners_visible = true` | **INSUFFICIENT_DATA** | ne |
| 1 | Brání něco prodeji? | jakýkoli `legal_flags[].type = block` (plomba, exekuce, insolvence, zákaz zcizení, spornost, neidentifikovaný vlastník, SJM se zemřelým, jednotky) | **BLOCKED** | ne |
| 2 | Musí se nejdřív nabídnout někomu jinému nebo získat souhlas? | `legal_flags[].type` ∈ {offer, consent} | nastaví strop **CONDITIONAL** | ano |
| 3 | Komu se dá prodat? | aspoň jeden `exits[]` | žádný exit → **NOT_WORTH_IT** | ano, pokud exit existuje |
| 4 | Přežije exit třetí fázi? | každý exit dostane `killed` + `kill_reason` z tabulky níže | všechny `killed = true` → **NOT_WORTH_IT** | ano, pokud aspoň jeden přežil |
| 5 | Chybí data, která by mohla výsledek zhoršit? | `missing_data[].impact` ∈ {could_block, could_require_offer, could_kill_exit} | **CONDITIONAL** | ne |
| 6 | Platí strop z kroku 2 nebo je kupec jen odhadnutý? | strop CONDITIONAL, nebo přeživší exit má `buyer = null`, nebo jediný přeživší exit je `co_owners` | **CONDITIONAL** | ne |
| 7 | Zbytek | přeživší exit s pojmenovaným kupcem, bez stropu, bez rizikových chybějících dat | **BUY_CANDIDATE** | ne |

`could_reduce_value` v `missing_data` výsledek nemění, jen se propíše do výstupu.

## Krok 1: blokery

| Kód | Signál ve vstupu |
|---|---|
| `seal` | `cadastre.pending_proceedings.seal_present = true` |
| `execution` | `cadastre.restrictions[].type` obsahuje "exekuc" |
| `insolvency` | `cadastre.restrictions[].type` obsahuje "insolvenc", "konkurs", "úpadk" |
| `alienation_ban` | `cadastre.restrictions[].type` obsahuje "Zákaz zcizení" |
| `dispute_note` | `cadastre.other_records[].type` obsahuje "spornost" nebo "žaloba" |
| `insufficiently_identified_owner` | `cadastre.owners[].insufficiently_identified = true` |
| `deceased_spouse_sjm` | `seller_facts.deceased_owner_in_sjm = true` a `inheritance_proceedings_open = true` |
| `units_ownership` | `cadastre.owners[].relation_type` = "Vlastnictví jednotek" |

Bloker u jiného spoluvlastníka než prodávajícího (např. exekuce na cizí podíl) NENÍ bloker koupě podílu, ale `kill_reason = co_owner_insolvency` pro exit `co_owners` v kroku 4.

## Krok 2: povinná nabídka a souhlas

| Kód | Typ | Signál | Komu |
|---|---|---|---|
| `state_nature_protection_61` | offer | `nature_protection.large_protected_area.type = NP` nebo `small_protected_area.type` ∈ {NPR, NPP} nebo `cave_related = true`, a zároveň `zoning.built_up_status != zastavěné území` | AOPK ČR / správa NP |
| `building_owner_3056` | offer | `cadastre.building.relation = Stavba na parcele` nebo `on_different_lv = true` | vlastník stavby |
| `registered_preemption` | offer | `cadastre.restrictions[].type` obsahuje "Předkupní právo" | oprávněný z LV |
| `municipality_or_region_101` | offer | `zoning.preemption_right_101.holder != null` | obec / kraj |
| `co_owners_inheritance_1124` | offer | `seller_facts.inheritance_date` mladší než 6 měsíců a víc než jeden vlastník | ostatní spoluvlastníci |
| `land_consolidation` | consent | `cadastre.other_records[].type` obsahuje "pozemkové úpravy" | pozemkový úřad |

Pokud je zdroj potřebný pro některé z těchto pravidel `not_checked` (AOPK, územní plán, seller_facts), jde do `missing_data` s `could_require_offer`.

## Krok 3: exity

| `exit_type` | Signál | Kupec (`buyer`) |
|---|---|---|
| `road_class_2` / `road_class_3` | `cadastre.land.land_use = silnice`; třída z `map.adjacent_roads[].road_class` | kraj dle sídla KÚ |
| `local_road` | `cadastre.land.land_use = ostatní komunikace` | obec |
| `co_owners` | víc než jeden vlastník mimo SJM | ostatní spoluvlastníci |
| `field_arable` / `field_grassland` | `cadastre.land.land_type` zemědělský; typ dle `lpis.dpb_items[].culture` | `lpis.dpb_items[].user_name` |
| `building_owner` | stavba jiného vlastníka | vlastník stavby |
| `forest` | `cadastre.land.land_type = lesní pozemek` | soused z `map.neighbouring_parcels[]` nebo `null` |

Jedna parcela může mít víc exitů (podíl na poli = `co_owners` + `field_*`). Všechny se vypíší.

## Krok 4: co exit zabije

| `kill_reason` | Exit | Signál |
|---|---|---|
| `owner_is_buyer` | road_*, local_road | vlastník je kraj / obec / stát |
| `clearcut` | forest | `map.orthophoto_land_cover = holina` |
| `no_access` | forest | `map.access_type = bez viditelného přístupu` |
| `no_lpis_user` | field_* | `lpis.parcel_in_lpis = false` |
| `co_owner_insolvency` | co_owners | exekuce / insolvence na cizím podílu |

Pokud zdroj pro kill-check chybí (`not_checked`), exit se nezabíjí, ale jde do `missing_data` s `could_kill_exit`, což v kroku 5 dá CONDITIONAL.

## Příklady průchodu

| Parcela | Krok, který rozhodl | Verdikt |
|---|---|---|
| Zálesní Lhota 1292/2 (silnice, vlastník kraj) | 4: `owner_is_buyer` | NOT_WORTH_IT |
| Silnice III. třídy, soukromý vlastník, čistý LV, mapa `checked`, celá pod silnicí | 7 | BUY_CANDIDATE |
| Totéž, ale `map.status = not_checked` | 5: `map.road_covers_parcel` je `could_reduce_value`, nic rizikového → 7 | BUY_CANDIDATE s poznámkou v `missing_data` |
| Pole s uživatelem v LPIS, LPIS `not_checked` | 5: `could_kill_exit` | CONDITIONAL |
| Podíl 1/48, dědictví před 2 měsíci | 2 + 6 | CONDITIONAL |
| Louka v NP mimo zastavěné území | 2 + 6 | CONDITIONAL |
| Les, holina, bez přístupu | 4 | NOT_WORTH_IT |
| Cokoli s plombou | 1 | BLOCKED |
| `cadastre.status = not_checked` | 0 | INSUFFICIENT_DATA |
