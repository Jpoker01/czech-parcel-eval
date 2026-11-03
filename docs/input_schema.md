# Vstupní schéma

`input/schema.json` je prázdný vstup, který se zkopíruje a vyplní pro každou parcelu. Tento soubor říká, kde ve zdroji se každá hodnota najde a jaké hodnoty jsou povolené. Hodnoty se píšou česky tak, jak je zobrazuje zdroj. Vstup obsahuje POUZE pole, která čte některé pravidlo v `docs/decision_table.md`, plus identifikaci parcely pro člověka.

## Pravidla pro všechny zdroje

- `status`: `checked` (zdroj otevřen a opsán; prázdný seznam nebo `false` znamená "nic tam není"), `not_checked` (zdroj neotevřen; hodnoty uvnitř jsou `null` a nic neznamenají), `not_available` (zdroj pro parcelu nic nenabízí, důvod do `notes`).
- `null` uvnitř zdroje se statusem `checked` znamená "toto pole jsem nezjistil".
- Texty ze zdrojů se opisují doslova (typ omezení, způsob využití, kultura). Interpretace patří promptu.
- `notes`: volný text pro člověka. Prompt ho nečte jako data, jen jako kontext.

## meta

| Pole | Hodnoty |
|---|---|
| `case_id` | vlastní ID, obvykle `<katastrální území>_<parcelní číslo>` |
| `notes` | volný text |

## land_register

Zdroj: Nahlížení do KN (nahlizenidokn.cuzk.gov.cz), stránka "Informace o pozemku", přihlášený uživatel.

| Pole | Kde ve zdroji | Hodnoty |
|---|---|---|
| `owners_visible` | sekce "Vlastníci, jiní oprávnění" je zobrazená | `true` / `false`. Bez přihlášení jsou vlastníci skryti, pak `false` a `owners` prázdné |
| `identification.municipality` | řádek "Obec" (bez kódu v závorce) | jediné pole identifikace, které prompt čte (kupec u místní komunikace) |
| `identification.cadastral_area` | řádek "Katastrální území" (bez kódu) | jen pro člověka |
| `identification.parcel_number` | řádek "Parcelní číslo" | např. `1292/2` |
| `identification.lv_number` | řádek "Číslo LV" | jen pro člověka |
| `land.area_m2` | řádek "Výměra [m2]" | celé číslo |
| `land.land_type` | řádek "Druh pozemku" | `orná půda`, `chmelnice`, `vinice`, `zahrada`, `ovocný sad`, `trvalý travní porost`, `lesní pozemek`, `vodní plocha`, `zastavěná plocha a nádvoří`, `ostatní plocha` |
| `land.land_use` | řádek "Způsob využití" | doslova (`silnice`, `ostatní komunikace`, `dráha`, `jiná plocha` ...), `null` když řádek chybí |
| `building.relation` | nadpis nad blokem stavby | `Součástí je stavba` / `Stavba na parcele` / `null` |
| `building.on_different_lv` | "Číslo LV" stavby se liší od LV parcely | `true` / `false` |
| `owners[]` | sekce "Vlastníci, jiní oprávnění", jedna položka na řádek | viz níže |
| `restrictions[]` | sekce "Omezení vlastnického práva", jedna položka na řádek | viz níže |
| `other_records[]` | sekce "Jiné zápisy", jedna položka na řádek | viz níže |
| `seal_present` | stránka ukazuje plombu / probíhající řízení | `true` / `false` |

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

- `relation_type`: typ vztahu, jak ho zobrazuje KN.
- `name`: jméno, jak je zobrazené. Jména fyzických osob v test cases anonymizovat (`Osoba A`). Názvy obcí, krajů a firem nechat, model z nich pozná veřejného vlastníka.
- `share`: sloupec "Podíl". U výlučného vlastnictví `1/1`.
- `sjm`: `true`, když řádek uvádí SJM. Oba manželé jsou jedna položka, druhé jméno do `name` za středník.
- `insufficiently_identified`: `true`, když je řádek označený jako nedostatečně identifikovaný vlastník.

### restrictions[], other_records[]

```json
"restrictions": [{"type": "Zástavní právo smluvní"}],
"other_records": [{"type": "Změna výměr obnovou operátu"}]
```

- `type`: sloupec "Typ", doslova.
- Opisují se VŠECHNY zápisy na LV, i ty, které se týkají jen jiného spoluvlastníka než prodávajícího (důvod v kroku 1 `docs/decision_table.md`).

## map

Zdroj: Mapy.com (vrstva "Katastrální data" + letecká mapa) nebo mapa v Nahlížení do KN.

| Pole | Kde ve zdroji | Hodnoty |
|---|---|---|
| `adjacent_roads[]` | silnice, které se parcely dotýkají, číslo z popisku v mapě | `{"road_number": "III/29317", "road_class": "III. třída"}`; třída z čísla: 3 číslice = II., 4 - 5 číslic = III. |
| `access_type` | čeho se parcela dotýká | `silnice` / `místní komunikace` / `polní cesta` / `bez viditelného přístupu` |
| `orthophoto_land_cover` | letecká mapa | `orná půda` / `louka` / `les` / `holina` / `zástavba` / `zarůstání` / `silnice` |
| `neighbouring_parcels[]` | parcely se společnou hranicí | `{"number": "1293/1", "owner": "Osoba B"}`, vlastník jen u lesa |

## lpis

Zdroj: Veřejný registr půdy LPIS (eagri.cz), záložka "Parcela", hledání podle k. ú. a parcelního čísla.

| Pole | Kde ve zdroji | Hodnoty |
|---|---|---|
| `parcel_in_lpis` | hledání vrátí aspoň jeden díl půdního bloku (DPB) | `true` / `false` |
| `dpb_items[].user_name` | pole "Uživatel" | např. `ZD Studenec` |
| `dpb_items[].culture` | pole "Kultura" | doslova (`standardní orná půda`, `trvalý travní porost`, `travní porost`, `úhor`, `vinice`, `chmelnice`, `ovocný sad` ...) |

## nature_protection

Zdroj: mapový portál AOPK (webgis.nature.cz / drusop.nature.cz), vrstvy chráněných území u parcely.

| Pole | Kde ve zdroji | Hodnoty |
|---|---|---|
| `large_protected_area.type` | velkoplošné chráněné území, které parcelu překrývá | `NP` / `CHKO` / `null` |
| `small_protected_area.type` | maloplošné chráněné území | `NPR` / `PR` / `NPP` / `PP` / `null` |
| `*.name` | název území | jen pro člověka |
| `parcel_only_partially_inside` | hranice území protíná parcelu | `true` / `false` |
| `cave_related` | parcela je vedená jako související s jeskyní | `true` / `false` |

## zoning

Zdroj: územní plán obce (Národní geoportál územního plánování nebo web obce). Obec bez územního plánu: `status: not_available`, důvod do `notes`.

| Pole | Kde ve zdroji | Hodnoty |
|---|---|---|
| `built_up_status` | výkres základního členění území | `zastavěné území` / `zastavitelná plocha` / `plocha přestavby` / `nezastavěné území` / `územní rezerva` |
| `preemption_right_101_holder` | předkupní právo podle starého § 101 uvedené v plánu | `obec` / `kraj` / `stát` / `null` |

## seller_facts

Zdroj: prodávající. Veřejné zdroje tyto údaje nemají, vyplňují se jen tam, kde je případ na nich postavený.

| Pole | Hodnoty |
|---|---|
| `inheritance_date` | `YYYY-MM-DD`, když podíl prodávajícího pochází z dědictví, jinak `null` |
| `deceased_owner_in_sjm` | `true`, když zemřel spoluvlastník v SJM; `false` / `null` |
| `inheritance_proceedings_open` | `true`, když toto dědictví ještě není vypořádané; `false` / `null` |
