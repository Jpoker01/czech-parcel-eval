# Vstupní šablona: tvar položek a povolené hodnoty

Doplňuje `input/template.json`. Hodnoty se píšou česky tak, jak je zobrazuje zdroj. Pravidla pro `status` a `null` jsou v `signal_map.md`.

## cadastre

| Pole | Povolené hodnoty / formát |
|---|---|
| `logged_in`, `owners_visible` | `true` / `false`. Bez přihlášení jsou vlastníci skryti, pak `owners_visible: false` |
| `identification.parcel_kind_code` | `PKN` (parcela katastru nemovitostí) / `PZE` (parcela zjednodušené evidence) |
| `identification.simplified_evidence_origin` | `EN` / `PK` / `GP` / `null` |
| `identification.numbering_type` | `pozemková` / `stavební` / `null` (jednotná řada) |
| `identification.parcel_number` | jak v KN, např. `1292/2`, `st. 24/1` |
| `land.map_sheet` | `DKM` / `KMD` / `KM-D` / `analogová mapa` / `null` (PZE) |
| `land.area_determination` | `Ze souřadnic v S-JTSK` / `Jiným číselným způsobem` / `Graficky nebo v digitalizované mapě` / `null` |
| `land.land_type` | `orná půda`, `chmelnice`, `vinice`, `zahrada`, `ovocný sad`, `trvalý travní porost`, `lesní pozemek`, `vodní plocha`, `zastavěná plocha a nádvoří`, `ostatní plocha` |
| `land.land_use` | doslova z KN (např. `silnice`, `ostatní komunikace`, `dráha`, `les jiný než hospodářský`, `jiná plocha`) nebo `null` |
| `building.relation` | `Součástí je stavba` / `Stavba na parcele` / `null` |

### owners[]

```json
{
  "relation_type": "Vlastnické právo",
  "name": "Liberecký kraj",
  "share": "1/1",
  "sjm": false,
  "insufficiently_identified": false,
  "foreign_address": false
}
```

- `share`: zlomek z KN. U výlučného vlastnictví bez podílu psát `1/1`.
- `sjm`: `true`, pokud je vlastník zapsán jako SJM. Oba manželé tvoří jednu položku, druhé jméno do `name` za středník.
- Jména fyzických osob v test cases anonymizovat (`Osoba A`). Názvy obcí, krajů a firem nechat, model z nich pozná veřejného vlastníka.

### protection[], bpej[], restrictions[], other_records[]

```json
"protection": [{"name": "zemědělský půdní fond"}],
"bpej": [{"code": "24811", "area_m2": 5000}],
"restrictions": [
  {
    "type": "Zástavní právo smluvní",
    "beneficiary": "Banka a.s.",
    "applies_to_share_only": false,
    "related_parcels": []
  }
],
"other_records": [{"type": "Změna výměr obnovou operátu"}]
```

- `type` a `name` vždy doslova z KN.
- Prázdný seznam při `status: checked` = KN zobrazuje "Nejsou evidována žádná ...".

## map

| Pole | Povolené hodnoty |
|---|---|
| `source` | `Mapy.com` / `Nahlížení do KN - mapa` / `Geoportál ČÚZK` |
| `adjacent_roads[]` | `{"road_number": "III/29317", "road_class": "III. třída"}` |
| `road_covers_parcel` | `celá` / `část` / `ne` |
| `access_type` | `silnice` / `místní komunikace` / `polní cesta` / `bez viditelného přístupu` |
| `orthophoto_land_cover` | `orná půda` / `louka` / `les` / `holina` / `zástavba` / `zarůstání` / `silnice` |
| `neighbouring_parcels[]` | čísla sousedních parcel, u lesa a malých pozemků i s vlastníkem: `{"number": "1293/1", "owner": "Osoba B"}` |

## lpis

| Pole | Povolené hodnoty |
|---|---|
| `parcel_in_lpis` | `true` / `false` (parcela nepatří do žádného DPB) |
| `dpb_items[]` | viz níže |

```json
{
  "square_code": "640-1080",
  "user_name": "Zemědělské družstvo X",
  "culture": "standardní orná půda",
  "area_ha": 12.4,
  "organic_farming": "konvenční",
  "erosion": "MEO"
}
```

- `culture`: doslova z LPIS (`standardní orná půda`, `trvalý travní porost`, `travní porost`, `úhor`, `vinice`, `chmelnice`, `ovocný sad`, `zalesněná půda`, `jiná kultura` ...).
- `erosion`: `SEO` / `MEO` / `NEO` / `null`.

## nature_protection

| Pole | Povolené hodnoty |
|---|---|
| `large_protected_area.type` | `NP` / `CHKO` / `null` |
| `large_protected_area.zone` | NP: `přírodní`, `přírodě blízká`, `soustředěné péče o přírodu`, `kulturní krajiny`; CHKO: `I.`, `II.`, `III.`, `IV.`; jinak `null` |
| `small_protected_area.type` | `NPR` / `PR` / `NPP` / `PP` / `null` |
| `parcel_only_partially_inside` | `true` / `false` / `null` |
| `cave_related` | `true` / `false` |
| `natura2000.evl`, `natura2000.bird_area` | název lokality nebo `null` |
| `uses_element` | `biocentrum` / `biokoridor` / `null` |

## flood

| Pole | Povolené hodnoty |
|---|---|
| `designated_flood_zone` | `Q5` / `Q20` / `Q100` / `mimo` |
| `active_zone` | `ano` / `ne` / `nestanovena` |
| `hazard_category` | `vysoké` / `střední` / `nízké` / `reziduální` / `null` |

## zoning

| Pole | Povolené hodnoty |
|---|---|
| `municipality_has_zoning_plan` | `true` / `false` (pak `status: not_available` u zbytku a zastavěné území = intravilán 1966) |
| `area_type` | doslova z ÚP, např. `plocha bydlení`, `plocha zemědělská` |
| `built_up_status` | `zastavěné území` / `zastavitelná plocha` / `plocha přestavby` / `nezastavěné území` / `územní rezerva` |
| `public_benefit_construction.type` | `VPS` / `VPO` / `null` |
| `preemption_right_101.holder` | `obec` / `kraj` / `stát` / `null` |

## seller_facts

Údaje, které veřejné zdroje nemají. V testech se doplňují jen tam, kde je případ na nich postavený.

| Pole | Formát |
|---|---|
| `inheritance_date` | `YYYY-MM-DD` nebo `null` |
| `deceased_owner_in_sjm` | `true` / `false` / `null` |
| `inheritance_proceedings_open` | `true` / `false` / `null` |
| `lease_contract` | `{"lessee": "...", "until": "2033-09-30"}` nebo `null` |
