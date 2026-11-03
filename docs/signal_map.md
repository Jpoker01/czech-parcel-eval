# Mapa signálů: situace → fáze → zdroj → pole šablony

Každá situace z hodnocení je kombinace několika polí z `input/template.json`. Tabulky říkají, ve kterém zdroji a ve kterém poli se signál zjistí.

Zkratky zdrojů: **KN** = Nahlížení do KN (přihlášený uživatel), **MAP** = Mapy.com / ortofoto / mapa v Nahlížení do KN, **LPIS** = Veřejný registr půdy, **AOPK** = mapy AOPK, **ZONING** = územní plán (Národní geoportál územního plánování nebo web obce), **SELLER** = údaje od prodávajícího.

## Fáze 1: lze parcelu vůbec koupit?

### BLOCKED

| Situace | Zdroj | Pole | Signál |
|---|---|---|---|
| Plomba | KN | `land_register.seal_present` | `true` |
| Exekuce | KN | `land_register.restrictions[].type` | obsahuje "exekuc" |
| Insolvence / konkurs | KN | `land_register.restrictions[].type` | "insolvenc", "konkurs", "úpadk" |
| Zákaz zcizení | KN | `land_register.restrictions[].type` | "Zákaz zcizení" |
| Poznámka spornosti, žaloba | KN | `land_register.other_records[].type` | "spornost", "žaloba" |
| Nedostatečně identifikovaný vlastník | KN | `land_register.owners[].insufficiently_identified` | `true` |
| SJM se zemřelým manželem, neskončené dědictví | SELLER | `seller_facts.deceased_owner_in_sjm`, `inheritance_proceedings_open` | obojí `true` |
| Pozemek spojený s jednotkami | KN | `land_register.owners[].relation_type` | "Vlastnictví jednotek" |

### REQUIRES OFFER / CONSENT (flag, výsledek nejvýš CONDITIONAL)

| Situace | Zdroj | Pole | Signál |
|---|---|---|---|
| NP, NPR, NPP, jeskyně mimo zastavěné území (§ 61 zákona 114/1992 Sb.) | AOPK + ZONING | `nature_protection.large_protected_area.type`, `small_protected_area.type`, `cave_related`, `parcel_only_partially_inside`, `zoning.built_up_status` | NP / NPR / NPP / jeskyně a zároveň NE "zastavěné území"; platí i při částečném zásahu |
| Stavba jiného vlastníka (§ 3056 NOZ) | KN | `land_register.building.relation`, `on_different_lv` | "Stavba na parcele" nebo `true` |
| Zapsané předkupní právo | KN | `land_register.restrictions[].type` | "Předkupní právo" |
| Předkupní právo obce / kraje (starý § 101) | ZONING | `zoning.preemption_right_101_holder` | není `null` |
| Podíl zděděný před méně než 6 měsíci (§ 1124 NOZ) | SELLER | `seller_facts.inheritance_date` | mladší než 6 měsíců |
| Schválené pozemkové úpravy (souhlas úřadu) | KN | `land_register.other_records[].type` | "pozemkové úpravy" |

## Fáze 2: komu lze parcelu prodat (exit)

| Exit | Zdroj | Pole | Signál |
|---|---|---|---|
| Silnice II./III. třídy → kraj | KN + MAP | `land_register.land.land_use`, `map.adjacent_roads[].road_class` | "silnice"; třída z mapy |
| Místní komunikace → obec | KN | `land_register.land.land_use`, `identification.municipality` | "ostatní komunikace" |
| Podíl → ostatní spoluvlastníci | KN | `land_register.owners[]` | víc než jeden vlastník mimo SJM |
| Pole → uživatel z LPIS | KN + LPIS | `land_register.land.land_type`, `lpis.dpb_items[].user_name`, `.culture` | zemědělský druh pozemku; kultura rozliší ornou půdu a TTP |
| Pozemek pod cizí stavbou → vlastník stavby | KN | `land_register.building.*` | stavba jiného vlastníka |
| Les → soused | KN + MAP | `land_register.land.land_type`, `map.neighbouring_parcels[]` | "lesní pozemek" |

## Fáze 3: co exit zabije

| Faktor | Exit | Zdroj | Pole |
|---|---|---|---|
| Vlastník je kraj / obec / stát | silnice, místní komunikace | KN | `land_register.owners[].name` |
| Holina | les | MAP | `map.orthophoto_land_cover = holina` |
| Bez přístupu | les | MAP | `map.access_type = bez viditelného přístupu` |
| Parcela bez DPB | pole | LPIS | `lpis.parcel_in_lpis = false` |
| Exekuce / insolvence jiného spoluvlastníka | podíl | KN | `land_register.restrictions[].beneficiary`, `applies_to_share_only` |

## Co se nesbírá a proč

- **Záplavy, BPEJ, zástavy, pacht, CHKO a Natura 2000:** jen snižují hodnotu, verdikt nemění. Kontrolující je uvidí na LV.
- **Souhlas s veřejným užíváním cesty (I. ÚS 2541/25):** z žádného zdroje nejde zjistit.
- **Podrobnosti stavby (č. p., typ):** pro rozhodnutí stačí, že stavba jiného vlastníka existuje.
