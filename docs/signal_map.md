# Mapa signálů: situace → fáze → zdroj → pole šablony

Každá situace z hodnocení je kombinace několika polí z `input/template.json`. Tabulky říkají, ve kterém zdroji a ve kterém poli se signál zjistí. Cesty polí odpovídají klíčům v šabloně.

Zkratky zdrojů: **KN** = Nahlížení do KN (přihlášený uživatel), **MAP** = Mapy.com / ortofoto / mapa v Nahlížení do KN, **LPIS** = Veřejný registr půdy, **AOPK** = mapy AOPK a NATURA 2000, **FLOOD** = záplavová území (POVIS, správci povodí), **ZONING** = územní plán (Národní geoportál územního plánování nebo web obce).

## Fáze 1: lze parcelu vůbec koupit?

### BLOCKED

| Situace | Zdroj | Pole | Signál |
|---|---|---|---|
| Plomba (probíhající řízení) | KN | `cadastre.pending_proceedings.seal_present` | `true` |
| Exekuce (exekuční příkaz, nařízení nebo zahájení exekuce, exekutorské zástavní právo) | KN | `cadastre.restrictions[].type` | text obsahuje "exekuc" |
| Insolvence / konkurs | KN | `cadastre.restrictions[].type` | "insolvenc", "konkursní podstat", "úpadk" |
| Zákaz zcizení | KN | `cadastre.restrictions[].type` | "Zákaz zcizení" |
| Poznámka spornosti, podaná žaloba | KN | `cadastre.other_records[].type` | "spornost", "žaloba" |
| Nedostatečně identifikovaný vlastník | KN | `cadastre.owners[].insufficiently_identified` | `true` |
| SJM se zemřelým manželem, neskončené dědické řízení | KN + vstup od prodávajícího | `cadastre.owners[].sjm`, `seller_facts.deceased_owner_in_sjm` | KN smrt nezobrazuje, jen ručně doplněný údaj |
| Pozemek spojený s jednotkami | KN | `cadastre.owners[].relation_type` | "Vlastnictví jednotek" |

### REQUIRES_OFFER (flag, hodnocení pokračuje, výsledek nejvýš CONDITIONAL)

| Situace | Zdroj | Pole | Signál |
|---|---|---|---|
| NP, NPR, NPP, jeskyně mimo zastavěné území (§ 61 zákona 114/1992 Sb.) | AOPK + ZONING | `nature_protection.large_protected_area.type`, `nature_protection.small_protected_area.type`, `nature_protection.cave_related`, `zoning.built_up_status` | NP / NPR / NPP a zároveň NE "zastavěné území". Platí i při částečném zásahu a i bez zápisu v KN |
| Stavba jiného vlastníka (§ 3056 NOZ) | KN | `cadastre.building.relation`, `cadastre.building.on_different_lv` | "Stavba na parcele" nebo stavba na jiném LV |
| Zapsané předkupní právo | KN | `cadastre.restrictions[].type` | "Předkupní právo" |
| Předkupní právo obce / kraje podle starého § 101 | ZONING + KN | `zoning.preemption_right_101`, `cadastre.restrictions[]` | holder != null |
| Podíl zděděný před méně než 6 měsíci (§ 1124 NOZ) | vstup od prodávajícího | `seller_facts.inheritance_date` | Nahlížení do KN nabývací titul nezobrazuje |

### REQUIRES_CONSENT

| Situace | Zdroj | Pole | Signál |
|---|---|---|---|
| Schválené pozemkové úpravy | KN | `cadastre.other_records[].type` | "Schválené pozemkové úpravy" |

## Fáze 2: komu lze parcelu prodat (exit)

| Exit | Zdroj | Pole | Signál |
|---|---|---|---|
| **Silnice II./III. třídy → kraj** | KN | `cadastre.land.land_use`, `cadastre.owners[].name` | "silnice" a vlastník NENÍ kraj ani stát |
| | MAP | `map.adjacent_roads[].road_number`, `.road_class` | 3místné číslo = II. třída, 4 - 5místné = III. třída |
| | MAP | `map.road_covers_parcel` | celá / část / ne |
| **Spoluvlastnický podíl → ostatní spoluvlastníci nebo soudní zrušení** | KN | `cadastre.owners[]` (počet, `share`) | víc než 1 vlastník mimo SJM |
| **Pole → uživatel z LPIS** | KN | `cadastre.land.land_type` | orná půda, TTP, chmelnice, vinice, sad, zahrada |
| | LPIS | `lpis.dpb_items[].user_name`, `.culture` | uživatel != vlastník |
| **Pozemek pod cizí stavbou → vlastník stavby** (prodej nebo úplata za užívání) | KN | `cadastre.building.*` | stavba jiného vlastníka |
| **Les → soused nebo prodej dřeva** | KN | `cadastre.land.land_type` | "lesní pozemek" |
| | MAP | `map.orthophoto_land_cover`, `map.access_type`, `map.neighbouring_parcels` | vzrostlý les + přístup |

## Fáze 3: co exit zabije nebo sníží hodnotu

| Faktor | Dotčený exit | Zdroj | Pole | Dopad |
|---|---|---|---|---|
| Vlastník je kraj / stát | silnice | KN | `cadastre.owners[].name` | zabije (už vykoupeno) |
| Silnice pokrývá jen část parcely | silnice | MAP | `map.road_covers_parcel` | sníží (nutný geometrický plán) |
| Cesta s veřejným užíváním se souhlasem vlastníka (I. ÚS 2541/25) | místní komunikace | žádný zdroj | `missing_data` | nelze zjistit, právní prověrka |
| Insolvence nebo exekuce jiného spoluvlastníka | podíl | KN | `cadastre.restrictions[]` | zabije soudní cestu / zdrží |
| Velký počet spoluvlastníků, malý podíl | podíl | KN | `cadastre.owners[]` | sníží (diskont za podíl) |
| Zapsaný pacht / nájem | pole | KN | `cadastre.restrictions[]` | sníží, pacht přechází na kupujícího |
| Rozpor KN orná půda vs. LPIS TTP | pole | KN + LPIS | `cadastre.land.land_type`, `lpis.dpb_items[].culture` | sníží |
| Silná erozní ohroženost (SEO) | pole | LPIS | `lpis.dpb_items[].erosion` | sníží |
| Parcela bez DPB v LPIS | pole | LPIS | `lpis.parcel_in_lpis = false` | zabije exit "uživatel z LPIS" |
| Holina, pařezy | les | MAP | `map.orthophoto_land_cover` | zabije nebo silně sníží |
| Bez přístupu | les, malé pozemky | MAP | `map.access_type` | zabije nebo silně sníží |
| Les jiný než hospodářský | les | KN | `cadastre.land.land_use` | sníží |
| Aktivní zóna záplavového území | všechny stavební a oplocení | FLOOD | `flood.active_zone` | zabije stavební exit |
| Q100 mimo aktivní zónu | všechny | FLOOD | `flood.designated_flood_zone` | sníží |
| CHKO I. a II. zóna, EVL, ptačí oblast | všechny | AOPK | `nature_protection.*` | sníží |
| Zástava, věcné břemeno, osobní služebnost (výměnek, užívání) | všechny | KN | `cadastre.restrictions[]` | sníží |
| Parcela zjednodušené evidence (PK, EN) | všechny | KN | `cadastre.identification.parcel_kind_code = PZE` | sníží (nejistá poloha a výměra) |
| VPS / VPO s možností vyvlastnění | soukromý exit | ZONING | `zoning.public_benefit_construction` | kupcem je veřejný investor |

## Pravidla šablony

1. **Každý zdroj má `status`:**
   - `checked`: zdroj jsem otevřel a opsal. Prázdný seznam nebo `false` znamená "zkontrolováno, nic tam není".
   - `not_checked`: zdroj jsem neotevřel. Hodnoty uvnitř jsou `null` a nic neznamenají.
   - `not_available`: zdroj pro parcelu nic nenabízí nebo ho nelze zobrazit (obec nemá ÚP, vlastníci skryti bez přihlášení, úsek bez záplavové mapy). Do `notes` napsat proč.
2. **`null` uvnitř zdroje se statusem `checked`** znamená "toto pole jsem nezjistil". Model ho musí dát do `missing_data`, nesmí ho domýšlet.
3. **Texty z KN se opisují doslova** (typ omezení, způsob ochrany). Interpretace patří promptu, ne tomu, kdo vyplňuje.
4. **Zdroj `not_checked`, který může zabít exit,** posouvá výsledek nejvýš na CONDITIONAL a do `missing_data`.
5. **`seller_facts`** jsou údaje, které žádný veřejný zdroj nemá (dědictví, úmrtí v SJM, pachtovní smlouva). Bez nich jsou příslušná pravidla `not_checked`.
