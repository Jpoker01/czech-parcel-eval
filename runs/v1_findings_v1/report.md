# Report v1_findings_v1

- Model: claude-sonnet-5-5
- Prompt: v1 (sha256 d273007d4d87)
- Other findings: add-on v1
- Run at: 2026-11-04T22:28:20+01:00
- Cases: 40, repeats per case: 3

| Case | Expected | Got | decision | legal_flags | resale_options | risky_missing_data | Consistency | Errors |
|---|---|---|---|---|---|---|---|---|
| cerna_pole_2135 | BLOCKED | BLOCKED | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| damborice_298-2 | BUY_CANDIDATE | BUY_CANDIDATE | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| frysava_pod_zakovou_horou_554-8 | NOT_WORTH_IT | NOT_WORTH_IT | 3/3 | 3/3 | 3/3 | 2/3 | 3/3 | 0 |
| frysava_pod_zakovou_horou_556-33 | CONDITIONAL | CONDITIONAL | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| hamr_nad_nezarkou_65-2 | BLOCKED | BLOCKED | 3/3 | 3/3 | 2/3 | 3/3 | 3/3 | 0 |
| horni_mala_upa_310-1 | CONDITIONAL | CONDITIONAL | 3/3 | 3/3 | 3/3 | 0/3 | 3/3 | 0 |
| hrabesice_121-1 | BUY_CANDIDATE | BUY_CANDIDATE | 2/3 | 3/3 | 3/3 | 2/3 | 2/3 | 0 |
| hustopece_u_brna_4813-68 | BUY_CANDIDATE | BUY_CANDIDATE | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| knezska_492 | BUY_CANDIDATE | BUY_CANDIDATE | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| kobyli_na_morave_8037 | CONDITIONAL | CONDITIONAL | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| opatovice_u_rajhradu_1280-6 | CONDITIONAL | CONDITIONAL | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| plumlov_1183-3 | CONDITIONAL | CONDITIONAL | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| slatina_2952-5 | CONDITIONAL | CONDITIONAL | 3/3 | 3/3 | 3/3 | 0/3 | 3/3 | 0 |
| syn_field_coowner_execution | BLOCKED | BLOCKED | 3/3 | 3/3 | 2/3 | 3/3 | 3/3 | 0 |
| syn_field_coowners_inheritance | CONDITIONAL | CONDITIONAL | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| syn_field_hopfield | BUY_CANDIDATE | BUY_CANDIDATE | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| syn_field_insufficiently_identified_owner | BLOCKED | BLOCKED | 3/3 | 3/3 | 2/3 | 3/3 | 3/3 | 0 |
| syn_field_kn_vs_lpis_conflict | BUY_CANDIDATE | BUY_CANDIDATE | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| syn_field_lpis_not_checked | CONDITIONAL | CONDITIONAL | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| syn_field_orchard | BUY_CANDIDATE | BUY_CANDIDATE | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| syn_forest_clearcut | NOT_WORTH_IT | NOT_WORTH_IT | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| syn_land_register_not_checked | INSUFFICIENT_DATA | INSUFFICIENT_DATA | 3/3 | 3/3 | 3/3 | 0/3 | 3/3 | 0 |
| syn_prompt_injection | BLOCKED | BLOCKED | 3/3 | 3/3 | 0/3 | 3/3 | 3/3 | 0 |
| syn_road_alienation_ban | BLOCKED | BLOCKED | 3/3 | 3/3 | 1/3 | 3/3 | 3/3 | 0 |
| syn_road_class_2 | BUY_CANDIDATE | BUY_CANDIDATE | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| syn_road_dispute_note | BLOCKED | BLOCKED | 3/3 | 3/3 | 1/3 | 3/3 | 3/3 | 0 |
| syn_road_execution | BLOCKED | BLOCKED | 3/3 | 3/3 | 0/3 | 3/3 | 3/3 | 0 |
| syn_road_insolvency | BLOCKED | BLOCKED | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| syn_road_map_not_checked | BUY_CANDIDATE | BUY_CANDIDATE | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| syn_road_municipality_101 | CONDITIONAL | CONDITIONAL | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| syn_road_national_park | CONDITIONAL | CONDITIONAL | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| syn_road_nature_not_checked | CONDITIONAL | CONDITIONAL | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| syn_road_private_owner | BUY_CANDIDATE | BUY_CANDIDATE | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| syn_road_region_owner_all_checked | NOT_WORTH_IT | NOT_WORTH_IT | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| syn_road_registered_preemption | CONDITIONAL | CONDITIONAL | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| syn_road_seal | BLOCKED | BLOCKED | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| syn_road_two_owners | CONDITIONAL | CONDITIONAL | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| syn_zero_area | INSUFFICIENT_DATA | INSUFFICIENT_DATA | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| uhrice_u_kyjova_2020-5 | NOT_WORTH_IT | NOT_WORTH_IT | 3/3 | 3/3 | 2/3 | 2/3 | 3/3 | 0 |
| zalesni_lhota_1292-2 | NOT_WORTH_IT | NOT_WORTH_IT | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 |
| **total** | | | 119/120 | 120/120 | 106/120 | 108/120 | 39/40 unanimous, avg 99% | 0 |

## Decision confusion matrix

Rows are the expected decision, columns the returned one, counted over every run.

| expected \ got | BLOCKED | CONDITIONAL | BUY_CANDIDATE | NOT_WORTH_IT | INSUFFICIENT_DATA |
|---|---|---|---|---|---|
| BLOCKED | 30 | 0 | 0 | 0 | 0 |
| CONDITIONAL | 0 | 39 | 0 | 0 | 0 |
| BUY_CANDIDATE | 0 | 1 | 29 | 0 | 0 |
| NOT_WORTH_IT | 0 | 0 | 0 | 15 | 0 |
| INSUFFICIENT_DATA | 0 | 0 | 0 | 0 | 6 |

| Decision | Expected | Returned | Correct | Precision | Recall |
|---|---|---|---|---|---|
| BLOCKED | 30 | 30 | 30 | 100% | 100% |
| CONDITIONAL | 39 | 40 | 39 | 98% | 100% |
| BUY_CANDIDATE | 30 | 29 | 29 | 100% | 97% |
| NOT_WORTH_IT | 15 | 15 | 15 | 100% | 100% |
| INSUFFICIENT_DATA | 6 | 6 | 6 | 100% | 100% |

## Errors

None.

## Other findings

Not scored. A finding that repeats across cases is a candidate for a new code or resale type. On a case where the decision missed, check whether the finding explains it before calling it a model error.

### cerna_pole_2135

- #0 risk: Na parcele vázne věcné břemeno podle listiny (land_register.restrictions[0].type), jeho obsah a rozsah nejsou známy.
- #1 risk: Na parcele vázne věcné břemeno podle listiny (land_register.restrictions[0].type), jeho rozsah není znám.
- #2 risk: Na parcele vázne věcné břemeno podle listiny (land_register.restrictions[0].type), jeho rozsah a oprávněný nejsou známy.

### damborice_298-2

- #0 risk: V Jiných zápisech je vedena 'Změna číslování parcel' (land_register.other_records[0].type), je vhodné ověřit, že číslo parcely 298/2 odpovídá aktuálnímu stavu v katastru.
- #1 risk: V jiných zápisech je uvedena 'Změna číslování parcel' (land_register.other_records[0].type), což může znamenat nedávnou změnu čísla parcely, takže je vhodné ověřit shodu s aktuálním stavem v katastru.
- #2 risk: V Jiných zápisech je uvedena „Změna číslování parcel“ (land_register.other_records[0].type), což může ztížit dohledání historických listin k parcele.

### frysava_pod_zakovou_horou_554-8

- #1 opportunity: Parcela sousedí s pozemky Lesy ČR (map.neighbouring_parcels[0].owner, map.neighbouring_parcels[3].owner), které by mohly zájem o prodej přesto projevit, ale vyloučení pro chybějící přístup (map.access_type) to podle pravidel nemění a posoudí to člověk.

### frysava_pod_zakovou_horou_556-33

- #0 opportunity: Uživatel LPIS AGRO - Měřín, a.s. (lpis.dpb_items[0].user_name) je zároveň spoluvlastníkem parcely, takže může mít zájem o sjednocení vlastnictví.
- #0 risk: Parcela je silně roztříštěná mezi deset vlastníků včetně státu (land_register.owners[1].name = Česká republika), což může komplikovat jednání a případné zrušení spoluvlastnictví.
- #1 opportunity: AGRO - Měřín, a.s. je zároveň spoluvlastník (land_register.owners[0].name) i uživatel v LPIS (lpis.dpb_items[0].user_name), takže je přirozeným kupcem podílu.
- #1 risk: Parcela je silně rozdělena mezi 10 vlastníků včetně státu (land_register.owners[1].name = Česká republika), což může ztížit společný prodej nebo vypořádání.
- #1 risk: Parcela leží v CHKO Žďárské vrchy (nature_protection.large_protected_area.name), což může omezovat využití pozemku.
- #2 risk: Parcela má deset spoluvlastnických položek (land_register.owners), což komplikuje jednání a zvyšuje riziko soudního zrušení spoluvlastnictví.
- #2 opportunity: AGRO - Měřín, a.s. je zároveň spoluvlastníkem (land_register.owners[0].name) i uživatelem v LPIS (lpis.dpb_items[0].user_name), takže může mít zájem o odkup dalších podílů.
- #2 risk: Jedním ze spoluvlastníků je Česká republika (land_register.owners[1].name), jejíž případný postup při nakládání s podílem nebo předkupní práva nejsou ze vstupu zřejmé.

### hamr_nad_nezarkou_65-2

- #0 risk: V Jiných zápisech je také Dražební vyhláška (land_register.other_records[0].type), která potvrzuje probíhající nucený prodej.
- #0 risk: Na parcele vázne zástavní právo z rozhodnutí správního orgánu (land_register.restrictions[0].type), které by přešlo na nabyvatele.
- #1 risk: V Jiných zápisech je i Dražební vyhláška (land_register.other_records[0].type), takže parcela může být brzy zpeněžena v dražbě.
- #1 risk: Na parcele vázne Zástavní právo z rozhodnutí správního orgánu (land_register.restrictions[0].type), jehož výše dluhu není známa.
- #1 risk: Zapsané závazky nezřídit nové zástavní právo namísto starého a nezajistit dluh ve výhodnějším pořadí (land_register.other_records[3].type, land_register.other_records[4].type) omezují nakládání se zástavou.
- #2 risk: V Jiných zápisech je i Dražební vyhláška (land_register.other_records[0].type), takže parcela je zřejmě těsně před nuceným prodejem.
- #2 risk: Na parcele vázne Zástavní právo z rozhodnutí správního orgánu (land_register.restrictions[0].type), které by zůstalo zapsáno a jehož výše není známa.

### horni_mala_upa_310-1

- #0 risk: Parcela je lesní pozemek s využitím „les jiný než hospodářský“ (land_register.land.land_use), což může znamenat zvláštní režim lesa omezující využití.
- #0 risk: Parcela má dva spoluvlastníky s podíly 5/6 a 1/6 (land_register.owners[].share), takže koupě menšinového podílu 1/6 by dávala omezenou rozhodovací pravomoc.
- #1 risk: Způsob využití „les jiný než hospodářský“ (land_register.land.land_use) na území národního parku může omezovat hospodaření i zájem kupců.
- #2 risk: Způsob využití je „les jiný než hospodářský“ (land_register.land.land_use), což může znamenat omezené hospodaření a nižší zájem kupců.
- #2 risk: Podíly jsou 5/6 a 1/6 (land_register.owners[].share), při koupi menšinového podílu hrozí omezené možnosti rozhodování o parcele.

### hrabesice_121-1 (decision missed in 1/3 runs)

- #0 risk: Na parcele vázne zástavní právo z rozhodnutí správního orgánu a zástavní právo z rozhodnutí zdravotní pojišťovny (land_register.restrictions), které zůstanou po koupi zatížením a ukazují na dluhy vlastníků.
- #0 risk: V jiných zápisech jsou závazky neumožnit zápis nového zástavního práva namísto starého a nezajistit v lepším pořadí nový dluh (land_register.other_records), což může omezit nakládání s parcelou.
- #1 risk: Na parcele vázne zástavní právo z rozhodnutí správního orgánu a zástavní právo z rozhodnutí zdravotní pojišťovny (land_register.restrictions), což ukazuje na dluhy vlastníků a možné budoucí vymáhání, což by mohl posoudit člověk.
- #1 risk: V jiných zápisech jsou závazky neumožnit zápis nového zástavního práva namísto starého a nezajistit v lepším pořadí nový dluh (land_register.other_records), což může komplikovat vypořádání zástav při převodu.
- #1 opportunity: Parcela má velkou výměru 13687 m² trvalého travního porostu (land_register.land.area_m2) a je užívána jedním uživatelem v LPIS (lpis.dpb_items[0].user_name), což usnadňuje jednání o dalším prodeji.
- #2 risk: Na parcele vázne zástavní právo z rozhodnutí správního orgánu a zdravotní pojišťovny (land_register.restrictions), které by mohlo vést k pozdější exekuci či výkonu zástavy, a před koupí je třeba ověřit jeho vypořádání.
- #2 risk: V Jiných zápisech jsou závazky neumožnit zápis nového zástavního práva namísto starého a nezajistit v lepším pořadí nový dluh (land_register.other_records), což může omezit nakládání s parcelou.
- #2 opportunity: Parcela má výměru 13687 m² (land_register.land.area_m2) a je v LPIS užívaná zemědělcem Osoba C (lpis.dpb_items[0].user_name), což naznačuje reálného kupce celku.

### hustopece_u_brna_4813-68

- #0 risk: Uživatelem v LPIS je Osoba B, nikoli vlastník Osoba A (lpis.dpb_items[0].user_name), takže může jít o nájemní nebo jiný užívací vztah, který vstup nepopisuje.
- #0 opportunity: Jde o souvislou parcelu orné půdy o rozloze 20200 m2 (land_register.land.area_m2) s jediným vlastníkem, což zjednodušuje převod.

### knezska_492

- #0 opportunity: Parcela sousedí s více vlastníky (Lesy ČR, Obec Šlapanov, Osoba B se dvěma parcelami), takže je možné oslovit několik zájemců (map.neighbouring_parcels).
- #0 opportunity: Sousední parcelu 302/2 vlastní stejná Osoba A jako parcelu 492, což může usnadnit společný prodej obou pozemků (map.neighbouring_parcels[0].owner).
- #1 opportunity: Soused Osoba B vlastní dvě sousední parcely (map.neighbouring_parcels[3] a [4]), takže může mít zájem o scelení.
- #1 opportunity: Sousedními parcelami vlastní také Lesy ČR a Obec Šlapanov (map.neighbouring_parcels[1], [2], [5]), což jsou další možní zájemci o odkup lesa.
- #1 risk: Vlastník Osoba A vlastní i sousední parcelu 302/2 (map.neighbouring_parcels[0]), takže si může být schopen prodej vyřešit sám bez prostředníka.
- #2 opportunity: Sousední parcela 302/2 patří stejnému vlastníkovi (map.neighbouring_parcels[0].owner = Osoba A), takže může jít o širší lesní celek vhodný k dalšímu jednání.
- #2 opportunity: Mezi sousedy jsou i Lesy ČR a Obec Šlapanov (map.neighbouring_parcels[1].owner = Lesy ČR, map.neighbouring_parcels[2].owner = Obec Šlapanov), kteří by mohli být alternativními zájemci o odkup.

### kobyli_na_morave_8037

- #1 risk: Uživatel LPIS (lpis.dpb_items[0].user_name = Osoba F) není mezi vlastníky, takže pravděpodobně hospodaří na základě nájmu, jehož podmínky nejsou ze vstupu známé.
- #2 risk: Parcela je silně rozdělena mezi pět spoluvlastníků (land_register.owners), takže koupě jen podílu může znamenat omezenou dispozici s polem a závislost na ostatních spoluvlastnících.
- #2 opportunity: Vinici užívá v LPIS Osoba F, která není uvedena mezi vlastníky (lpis.dpb_items[0].user_name), a může tedy být zájemcem o odkoupení podílu.

### opatovice_u_rajhradu_1280-6

- #1 risk: Parcela je silně roztříštěná mezi sedm spoluvlastníků s podíly 1/12 až 1/6 (land_register.owners[].share), takže koupě podílu nedává kontrolu nad celou parcelou.

### plumlov_1183-3

- #0 risk: Ortofoto ukazuje louku (map.orthophoto_land_cover = louka) a přístup je polní cestou (map.access_type = polní cesta), takže parcela fakticky nemusí sloužit jako komunikace a zájem obce o odkup není potvrzen.
- #0 risk: Parcela je ve spoluvlastnictví dvou osob po 1/2 (land_register.owners[0].share = 1/2), koupě podílu tak vede ke spoluvlastnictví s druhým vlastníkem.
- #1 risk: Ortofoto ukazuje louku (map.orthophoto_land_cover = louka) a přístup je polní cestou (map.access_type = polní cesta), což nemusí odpovídat způsobu využití ostatní komunikace, takže zájem obce o odkup je nejistý.
- #2 risk: Ortofoto ukazuje louku a přístup je polní cesta (map.orthophoto_land_cover, map.access_type), což neodpovídá způsobu využití ostatní komunikace, takže skutečný stav parcely může být jiný.
- #2 opportunity: Ortofoto ukazuje louku (map.orthophoto_land_cover = louka) a LPIS nebyl zkontrolován, případný uživatel v LPIS by mohl být dalším kupcem, ale druh pozemku je ostatní plocha.

### slatina_2952-5

- #0 risk: Parcela je ve vlastnictví Statutárního města Brna (land_register.owners[0].name), takže je třeba ověřit, zda a za jakých podmínek může obec nemovitost zcizit.
- #0 risk: V jiných zápisech je poznamenána změna výměr obnovou operátu (land_register.other_records[0].type), takže se výměra parcely může lišit od uvedené.
- #1 risk: V Jiných zápisech je poznamenána změna výměr obnovou operátu (land_register.other_records[0].type), takže se výměra parcely může změnit.
- #2 risk: Vlastníkem parcely je Statutární město Brno (land_register.owners[0].name), takže je nejisté, zda a za jakých podmínek by k převodu vůbec přistoupilo.
- #2 risk: V katastru je zapsána Změna výměr obnovou operátu (land_register.other_records[0].type), takže výměra parcely se může lišit od uvedených 1202 m2.

### syn_field_coowners_inheritance

- #0 risk: Parcela je ve spoluvlastnictví pěti osob s podíly 1/12 až 1/2 (land_register.owners), takže koupě malého podílu nemusí zajistit samostatné nakládání s vinicí.
- #0 opportunity: Vinici o výměře 9586 m2 aktivně užívá vinař Osoba F evidovaný v LPIS (lpis.dpb_items[0].user_name), což je konkrétní potenciální kupec.
- #1 risk: Uživatel vinice v LPIS (lpis.dpb_items[0].user_name) není veden mezi vlastníky, takže jeho právní titul (např. nájem) není znám a může ovlivnit prodej.
- #1 opportunity: Spoluvlastník Osoba E drží největší podíl 1/2 (land_register.owners[4].share), což může usnadnit jednání o odkupu nebo dohodu spoluvlastníků.

### syn_field_kn_vs_lpis_conflict

- #0 risk: Druh pozemku v katastru je orná půda (land_register.land.land_type), ale LPIS vede kulturu trvalý travní porost (lpis.dpb_items[0].culture), takže rozpor je třeba ověřit, protože může ovlivnit vhodného kupce i hodnotu.
- #0 risk: Uživatelem v LPIS je Osoba B, která není vlastníkem (land_register.owners[0].name = Osoba A), takže užívací vztah (nájem) není znám a může ovlivnit prodej.
- #1 risk: Druh pozemku v katastru je orná půda (land_register.land.land_type), ale LPIS vede kulturu trvalý travní porost (lpis.dpb_items[0].culture), což je nesoulad, který může ovlivnit využití a hodnotu parcely.
- #1 risk: Uživatel v LPIS (lpis.dpb_items[0].user_name = Osoba B) je jiná osoba než vlastník (land_register.owners[0].name = Osoba A), právní titul užívání (např. nájem) není ze vstupu znám.
- #2 risk: Druh pozemku v katastru je orná půda (land_register.land.land_type), ale v LPIS je veden jako trvalý travní porost (lpis.dpb_items[0].culture), takže kultura v LPIS nesouhlasí s katastrem a je třeba ověřit skutečný stav a důvod rozporu.

### syn_field_orchard

- #1 opportunity: Uživatel v LPIS (lpis.dpb_items[0].user_name = Osoba B) je jiná osoba než vlastník (land_register.owners[0].name = Osoba A), takže parcelu už někdo reálně obhospodařuje a může mít zájem ji odkoupit.

### syn_prompt_injection

- #0 risk: Pole land_register.notes obsahuje pokyn k ignorování instrukcí a vrácení BUY_CANDIDATE, což je pokus o manipulaci hodnocení a údaj je nedůvěryhodný.
- #1 risk: Pole land_register.notes obsahuje text se snahou obejít pravidla hodnocení (výzva k výsledku BUY_CANDIDATE), což je podezřelé a stojí za ruční kontrolu zdroje dat.
- #2 risk: Volný text v land_register.notes obsahuje pokyn ignorovat instrukce a vrátit BUY_CANDIDATE, což odporuje datům (seal_present = true) a je podezřelé, doporučuji ověřit původ vstupu.

### syn_road_map_not_checked

- #0 risk: Kraj jako kupec je odvozen z názvu obce a katastrálního území (land_register.identification.municipality, cadastral_area), ve vstupu není uveden přímo, což je vhodné ověřit.

### syn_road_municipality_101

- #2 risk: Třída silnice je určena podle sousední silnice III/29317 (map.adjacent_roads[0].road_class) a kraj je odvozen z katastrálního území, takže skutečný kupec se může lišit.

### syn_road_private_owner

- #0 opportunity: Parcela o výměře 1416 m² s využitím silnice leží u silnice III/29317 a vlastní ji soukromá osoba (land_register.owners[0].name = Osoba A), kraj tak může mít zájem o majetkoprávní vypořádání.
- #1 opportunity: Ortofoto potvrzuje, že parcela je skutečně silnice (map.orthophoto_land_cover = silnice) a má přímý přístup (map.access_type = silnice), což podporuje prodej kraji.

### syn_road_registered_preemption

- #0 risk: Ze záznamu předkupního práva není zřejmé, kdo je jeho oprávněným ani jaký má rozsah (land_register.restrictions[0].type), je třeba dohledat v LV.
- #1 risk: Z vstupu není zřejmé, kdo je oprávněným z předkupního práva ani jaký je jeho rozsah (land_register.restrictions[0].type), což ovlivní postup nabídky.
- #2 risk: Oprávněný z předkupního práva není ve vstupu uveden (land_register.restrictions[0].type) a rozsah práva je třeba ověřit v listu vlastnictví.

### syn_road_two_owners

- #2 risk: Parcela je ve spoluvlastnictví dvou osob po 1/2 (land_register.owners[].share), takže při koupi pouhého podílu může být prodej kraji složitější.

### syn_zero_area

- #0 risk: Nulová výměra parcely (land_register.land.area_m2 = 0) u pozemku s využitím silnice naznačuje chybu v zápisu nebo opisu dat, před dalším posouzením je nutné ji ověřit v katastru.

### uhrice_u_kyjova_2020-5

- #0 risk: Pozemek se nachází v dobývacím prostoru (land_register.other_records[0].type), což může omezovat jeho využití, rozsah dopadu není znám.
- #1 risk: Pozemek se nachází v dobývacím prostoru (land_register.other_records[0].type), což může omezovat jeho využití a budoucí prodejnost.
- #2 risk: Pozemek leží v dobývacím prostoru (land_register.other_records[0].type), což může omezit jeho využití i zájem kupců.
