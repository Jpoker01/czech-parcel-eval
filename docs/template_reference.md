# Vstupní šablona: tvar položek a povolené hodnoty

Doplňuje `input/template.json`. Hodnoty se píšou česky tak, jak je zobrazuje zdroj. Šablona obsahuje POUZE pole, která čte některé pravidlo v `docs/decision_table.md`, plus identifikaci parcely pro člověka.

## Pravidla pro všechny zdroje

- `status`: `checked` (zdroj otevřen a opsán; prázdný seznam nebo `false` znamená "nic tam není"), `not_checked` (zdroj neotevřen; hodnoty uvnitř jsou `null` a nic neznamenají), `not_available` (zdroj pro parcelu nic nenabízí, důvod do `notes`).
- `null` uvnitř zdroje se statusem `checked` znamená "toto pole jsem nezjistil".
- Texty z KN se opisují doslova (typ omezení, způsob využití). Interpretace patří promptu.
- `notes`: volný text pro člověka. Prompt ho nečte jako data, jen jako kontext.

## cadastre

| Pole | Hodnoty |
|---|---|
| `owners_visible` | `true` / `false`. Bez přihlášení jsou vlastníci skryti, pak `false` a `owners` prázdné |
| `identification.*` | jen pro identifikaci parcely, prompt čte pouze `municipality` (kupec u místní komunikace) |
| `land.area_m2` | celé číslo z KN |
| `land.land_type` | `orná půda`, `chmelnice`, `vinice`, `zahrada`, `ovocný sad`, `trvalý travní porost`, `lesní pozemek`, `vodní plocha`, `zastavěná plocha a nádvoří`, `ostatní plocha` |
| `land.land_use` | doslova z KN (`silnice`, `ostatní komunikace`, `dráha`, `jiná plocha` ...) nebo `null` |
| `building.relation` | `Součástí je stavba` / `Stavba na parcele` / `null` |
| `building.on_different_lv` | `true`, pokud stavba na parcele má jiné LV než pozemek |
| `seal_present` | `true` / `false` (plomba) |

### owners[]

```json
{
  "relation_type": "Vlastnické právo",
  "name": "Liberecký kraj",
  "share": "1/1",
  "sjm": false,
  "insufficiently_identified": false
}
```

- `share`: zlomek z KN. U výlučného vlastnictví `1/1`.
- `sjm`: `true` u společného jmění manželů. Oba manželé jsou jedna položka, druhé jméno do `name` za středník.
- Jména fyzických osob v test cases anonymizovat (`Osoba A`). Názvy obcí, krajů a firem nechat, model z nich pozná veřejného vlastníka.

### restrictions[], other_records[]

```json
"restrictions": [
  {"type": "Zástavní právo smluvní", "beneficiary": "Banka a.s.", "applies_to_share_only": false}
],
"other_records": [{"type": "Změna výměr obnovou operátu"}]
```

- `type` doslova z KN.
- `beneficiary` a `applies_to_share_only` slouží k rozlišení exekuce na prodávajícího od exekuce na jiného spoluvlastníka.

## map

| Pole | Hodnoty |
|---|---|
| `adjacent_roads[]` | `{"road_number": "III/29317", "road_class": "III. třída"}` |
| `access_type` | `silnice` / `místní komunikace` / `polní cesta` / `bez viditelného přístupu` |
| `orthophoto_land_cover` | `orná půda` / `louka` / `les` / `holina` / `zástavba` / `zarůstání` / `silnice` |
| `neighbouring_parcels[]` | `{"number": "1293/1", "owner": "Osoba B"}`, vlastník jen u lesa |

## lpis

| Pole | Hodnoty |
|---|---|
| `parcel_in_lpis` | `true` / `false` (parcela nepatří do žádného DPB) |
| `dpb_items[]` | `{"user_name": "ZD X", "culture": "standardní orná půda"}` |

- `culture` doslova z LPIS (`standardní orná půda`, `trvalý travní porost`, `travní porost`, `úhor`, `vinice`, `chmelnice`, `ovocný sad` ...).

## nature_protection

| Pole | Hodnoty |
|---|---|
| `large_protected_area.type` | `NP` / `CHKO` / `null` |
| `small_protected_area.type` | `NPR` / `PR` / `NPP` / `PP` / `null` |
| `*.name` | název území, jen pro člověka |
| `parcel_only_partially_inside` | `true` / `false` |
| `cave_related` | `true` / `false` |

## zoning

| Pole | Hodnoty |
|---|---|
| `built_up_status` | `zastavěné území` / `zastavitelná plocha` / `plocha přestavby` / `nezastavěné území` / `územní rezerva` |
| `preemption_right_101_holder` | `obec` / `kraj` / `stát` / `null` |

Obec bez územního plánu: `status: not_available`, důvod do `notes`.

## seller_facts

Údaje, které veřejné zdroje nemají. Vyplňují se jen tam, kde je případ na nich postavený.

| Pole | Formát |
|---|---|
| `inheritance_date` | `YYYY-MM-DD` nebo `null` |
| `deceased_owner_in_sjm` | `true` / `false` / `null` |
| `inheritance_proceedings_open` | `true` / `false` / `null` |
