
# Další zjištění (`other_findings`)

Do `other_findings` zapiš všechno, co na parcele vidíš jako riziko nebo příležitost a co nepokrývá žádný `code`, `resale_type` ani `missing_data`. Pole je povinné. Když nic takového nevidíš, vrať prázdný seznam.

1. Každá položka má `type` (`risk` nebo `opportunity`) a `description`: jedna věta česky, která pojmenuje skutečnost a pole vstupu, ze kterého plyne. Příklad: "Na parcele vázne věcné břemeno ve prospěch nemovitosti mimo katastr (land_register.restrictions[0].type), jeho rozsah není znám."
2. Zjištění NEMĚNÍ `decision`, `legal_flags`, `resale_options`, `missing_data` ani `confidence`. Ty se řídí výhradně kroky 0 až 7. Pokud by podle tebe zjištění mělo verdikt změnit, napiš to do `description`, posoudí to člověk.
   Krok 1 platí beze změny: u `BLOCKED` hodnocení končí a `resale_options` zůstává prázdné. Zjištění zapiš i u blokované parcely, ale možnosti dalšího prodeje kvůli nim nevypisuj.
3. Neopakuj, co už je v ostatních polích. Nevymýšlej: každé zjištění musí plynout z konkrétní hodnoty ve vstupu.
4. Pravidla 3 a 7 platí dál: žádná cena, a nejasná hodnota, která by mohla změnit výsledek, patří do `missing_data`, ne sem.
