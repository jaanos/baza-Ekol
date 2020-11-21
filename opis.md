# Uvoz odpadka

Odpadek pride v podjetje pakiran po kosih (paleta ali zabojnik - nerelevantno). Odpadek ima lasnoti:

- `vrsta odpadka` (določena s klasifikacijsko številko in nazivom odpadka),
- `teža`,
- `povzročitelj` (tj. s katerega podjetja prihaja odpadek),
- `datum uvoza` odpadka,
- `mesto skladiščenja`,
- `opomba`.

Za nadaljno obdelavo je **nujno** potrebno poznati `mesto skladiščenja` (tj. v katerem skladišču se nakaja). Odpadek se vedno nahaja **v natanko enem** skladišču.

## Vrsta odpadka:
* klasifikacijska številka je pridobljena iz uredbe o odpadkih in je oblike oblike `?? ?? ??*`, pri čemer je `*` lahko zvezdica ali pa nič. Zvezdica na koncu je oznaka za nevarno snov;
* naziv odpadka je prosto besedilo, ki je točno določeno s pripadajočo klasifikacijsko številko;
* teža je vedno številka, največ 6 mestna (omejitev ni potrebna);
* povzročitelj je vedno neko besedilo;
* datum je oblike `dd.mm.llll`;
* mesto skladiščenja je besedilo iz obstoječega nabora:
  * skladišče 3;
  * skladišče 7;
  * drugo.
* opomba je prosto besedilo (poljuben niz).

---

# Izvoz odpadka

Ko odpadek odpeljemo, mu dodamo podatek o `datumu izvoza` in `prejemnika` (tj. kam je bil odpeljan). Tako pri uvozu kot tudi izvozu moramo imeti možnost dodajanja `opomb` (tj. kratek opis).

## Vrsta odpadka:
* datum izvoza je oblike `dd.mm.llll`;
* prejemnik je prosto besedilo;
* opomba je prosto besedilo.

---

# Obdelava podatkov:

1. Za posamezno skladišče moramo poznati skupno težo ter število kosov posameznega odpadka (klede na klasifikacijsko št.). Izpis samo za klasifikacijske številke, ki so na skladišču.
2. Vedno moramo imeti dostop do posameznih kosov odpadkov. Potrebujemo tudi vse skladiščene odpadke v nekem skladišču, včasih filtrirane samo za neko klasifikacijsko številko. Tukaj privzeto izpiše vse podatke o posameznem odpadku, lahko pa obejimo izbor izpisa.
3. Potrebujemo seznam vseh odpadkov, ki so na skladišču, seznam vseh odpadkov, ki so prišli (oz. odšli) iz nekega skladišča (oz. celotnega podjetja) v določenem časovnem obdobju (od datuma, do datuma). Tukaj privzeto izpiše vse podatke o posameznem odpadku, lahko pa omejimo izbor izpisa.
4. Potrebujemo tudi podatek o zadnjem izvozu za posamezno klasifikacijsko številko. Tj. seznam, na katerem je za vsako klasifikacijsko številko zapisan pripadajoč zadnji datum izvoza. Za tiste, ki so še na skladišču, zraven zapiše še datum prvega uvoza (najbolj oddaljenega od trenutnega dne), če odpadka za neko klasifikacijsko številko nimamo na skladišču, datuma ne izpiše. Tj. od tistih ki so na skladišču, datum prvega uvoza.

Na obrazcu izpisa mara izpisati datum in uro obdelave podatkov.


---

# Excelove tabele:

## ND_00_Seznam klasifikacij po dovoljenjih
Potrebujemo tabelo `Klasifikacije_uredba`.
- Klasifikacijska številka
- Naziv odpadka
- NEVAREN - ne rabimo

## 001_Evidenca_odpadko_v_skladiscu
- Vhod je primer vnašanja podatkov
- Izhod je primer vnašanja podatkov
- Podatki: nerelevantno
- Skladišče 3 in skladišče 7 sta primera izpisa za ti 2 skladišči