import os
import sqlite3
import xlrd

PARAM_FMT = ":{}"


class Tabela:
    """
    Razred, ki predstavlja tabelo v bazi.
    Polja razreda:
    - ime: ime tabele
    - podatki: ime datoteke s podatki ali None
    """
    ime = None
    podatki = None
    def __init__(self, conn):
        """
        Konstruktor razreda.
        """
        self.conn = conn
    def ustvari(self):
        """
        Metoda za ustvarjanje tabele.
        Podrazredi morajo povoziti to metodo.
        """
        raise NotImplementedError
    def uvozi(self):
        """
        Metoda za uvažanke podatkov.
        Podrazredi morajo povoziti to metodo.
        """
        raise NotImplementedError
    def izbrisi(self):
        """
        Metoda za brisanje tabele.
        """
        self.conn.execute("DROP TABLE IF EXISTS {};".format(self.ime))
    def izprazni(self):
        """
        Metoda za praznjenje tabele.
        """
        self.conn.execute("DELETE FROM {};".format(self.ime))
    def dodajanje(self, stolpci=None):
        """
        Metoda za gradnjo poizvedbe.
        Argumenti:
        - stolpci: seznam stolpcev
        """
        return "INSERT INTO {} ({}) VALUES ({});" \
            .format(self.ime, ", ".join(stolpci),
                    ", ".join(PARAM_FMT.format(s) for s in stolpci))
    def dodaj_vrstico(self, /, **podatki):
        """
        Metoda za dodajanje vrstice.
        Argumenti:
        - poimenovani parametri: vrednosti v ustreznih stolpcih
        """
        podatki = {kljuc: vrednost for kljuc, vrednost in podatki.items() if vrednost is not None}
        poizvedba = self.dodajanje(podatki.keys())
        cur = self.conn.execute(poizvedba, podatki)
        return cur.lastrowid

class Uporabnik(Tabela):
    """
    Tabela za uporabnike.
    """
    ime = "uporabnik"
    podatki = "podatki/uporabnik.csv"

    def ustvari(self):
        """
        Ustvari tabelo uporabnik.
        """
        self.conn.execute("""
            CREATE TABLE uporabnik (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                ime       TEXT NOT NULL UNIQUE,
                zgostitev TEXT NOT NULL,
                sol       TEXT NOT NULL
            )
        """)

    def dodaj_vrstico(self, /, **podatki):
        """
        Dodaj uporabnika.
        Če sol ni podana, zašifrira podano geslo.
        Argumenti:
        - poimenovani parametri: vrednosti v ustreznih stolpcih
        """
        if podatki.get("sol", None) is None and podatki.get("zgostitev", None) is not None:
            podatki["zgostitev"], podatki["sol"] = sifriraj_geslo(podatki["zgostitev"])
        return super().dodaj_vrstico(**podatki)

class Podjetja(Tabela):
    ime = 'podjetje'
    def ustvari(self):
        self.conn.execute('''
                CREATE TABLE podjetje (
                id  INTEGER PRIMARY KEY AUTOINCREMENT,
                ime TEXT    NOT NULL
            );''')
    def dodaj_vrstico(self, /, **podatki):
        """
        Dodaj žanr.
        Če žanr že obstaja, vrne obstoječi ID.
        Argumenti:
        - poimenovani parametri: vrednosti v ustreznih stolpcih
        """
        cur = self.conn.execute("""
            SELECT id FROM podjetje
            WHERE ime = :ime;
        """, podatki)
        r = cur.fetchone()
        if r is None:
            return super().dodaj_vrstico(**podatki)
        else:
            id, = r
            return id
    def uvozi(self, slo_id_podjetje):
        for podjetje in slo_id_podjetje:
            nov = dict()
            nov['ime'] = podjetje
            self.dodaj_vrstico(**nov)

class VrstaOdpadka(Tabela):
    ime = 'vrsta_odpadka'
    def ustvari(self):
        self.conn.execute('''
                CREATE TABLE vrsta_odpadka (
                    klasifikacijska_stevilka VARCHAR (9) PRIMARY KEY
                                             CHECK (klasifikacijska_stevilka LIKE '__ __ __%'),
                    naziv                    TEXT        NOT NULL
                );''')
    def uvozi(self, slo_klas_ste_ime):
        for kl, ime in slo_klas_ste_ime.items():
            nov = dict()
            nov['klasifikacijska_stevilka'] = kl
            nov['naziv'] = ime
            self.dodaj_vrstico(**nov)

class Skladisce(Tabela):
    ime = 'skladisce'
    def ustvari(self):
        self.conn.execute('''
                CREATE TABLE skladisce (
                    id  INTEGER PRIMARY KEY,
                    ime TEXT    NOT NULL
                );''')
    def uvozi(self, slo_sklad):
        for ime, st in slo_sklad.items():
            nov = {'id': st, 'ime': ime} 
            self.dodaj_vrstico(**nov)

class Odpadek(Tabela):
    ime = 'odpadek'
    def ustvari(self):
        self.conn.execute('''
                CREATE TABLE odpadek (
                    id                       INTEGER     PRIMARY KEY AUTOINCREMENT,
                    teza                     INTEGER     NOT NULL,
                    povzrocitelj             INTEGER     NOT NULL
                                                        REFERENCES podjetje (id),
                    prejemnik                INTEGER     REFERENCES podjetje (id),-- če ni obvezen podatek, brez NOT NULL
                    datum_uvoza              DATE        NOT NULL,
                    opomba_uvoz              TEXT,
                    datum_izvoza             DATE,
                    opomba_izvoz             TEXT,
                    klasifikacijska_stevilka VARCHAR (9) NOT NULL
                                                         REFERENCES vrsta_odpadka (klasifikacijska_stevilka),
                    skladisce                INTEGER     REFERENCES skladisce (id) 
                );''')
    def uvozi(self, sez_podatkov):
        for (kl, teza), slo in sez_podatkov.items():
            nov = dict()
            nov['klasifikacijska_stevilka'] = kl
            nov['teza'] = teza
            nov['prejemnik'] = ''
            nov['povzrocitelj'] = slo.get('pov', '')
            nov['opomba_uvoz'] = slo.get('op_uv', '')
            nov['skladisce'] = slo.get('skl', '')
            nov['datum_uvoza'] = slo.get('dat_uv', '')
            nov['datum_izvoza'] = slo.get('dat_iz', '')
            nov['opomba_izvoz'] = slo.get('op_iz', '')
            self.dodaj_vrstico(**nov)
    


def ustvari_tabele(tabele):
    """
    Ustvari podane tabele.
    """
    for t in tabele:
        t.ustvari()


def izbrisi_tabele(tabele):
    """
    Izbriši podane tabele.
    """
    for t in tabele:
        t.izbrisi()



def uvozi_podatke(tabele, conn):
    """
    Uvozi podatke v podane tabele.
    """
    slo_sklad = {'Sklad-3': 3, 'Sklad-7': 7}
    IME_DATOTEKE_Z_BAZO = conn
    IME_DATOTEKE_S_PODATKI1 = "ND_00_Seznam klasifikacij po dovoljenjih.xlsx"
    IME_DATOTEKE_S_PODATKI2 = "001_Evidenca_odpadko_v_skladiscu.xlsm"
    dat = xlrd.open_workbook(IME_DATOTEKE_S_PODATKI1)
    list1 = dat.sheet_by_index(1)
    slo_klas_ste_ime = dict()
    for i in range(1, 840): # po vrsticah
        kl_st = list1.cell_value(i, 0)
        ime = list1.cell_value(i, 1)
        slo_klas_ste_ime[kl_st] = ime
    dat2 = xlrd.open_workbook(IME_DATOTEKE_S_PODATKI2)
    # da bomo tabelo podjetja napolnit
    list3 = dat2.sheet_by_index(4)
    slo_id_podjetje = dict() # zato da bo id od podjetja nekje shranjen
    mn_pod = set()
    st = 1
    for i in range(1, 334):
        vred = list3.cell_value(i, 1)
        if vred and vred not in {'x', 'X'}:
            pod = vred.upper()
            if pod not in mn_pod:
                # z velikimi črkami zaradi neusklajenosti pisanja v excellu
                mn_pod.add(pod)
                slo_id_podjetje[pod] = st
                st += 1
    dat = xlrd.open_workbook(IME_DATOTEKE_S_PODATKI2)
    # da bomo tabelo podjetja napolnit
    vhod = dat.sheet_by_index(4) # 334 vrstic
    sez_podatkov = dict()
    for i in range(1, 334):
        kl_st = vhod.cell_value(i, 0)
        povzrocitelj = vhod.cell_value(i, 1)
        opomba_uvoz = vhod.cell_value(i, 2)
        teza = vhod.cell_value(i, 3)
        sklad = vhod.cell_value(i, 4)
        datum = vhod.cell_value(i, 5)
        if datum and teza != 1: # teža 1 pomeni napako
            # pomeni ni prazna vrstica
            # spremenimo datum primeren za SQL
            if opomba_uvoz == 'x':
                opomba_uvoz = ''
            if povzrocitelj.upper() in slo_id_podjetje.keys():
                povzrocitelj = slo_id_podjetje[povzrocitelj.upper()]
            else:
                if povzrocitelj not in {'x', 'X'}:
                    povzrocitelj = povzrocitelj.upper()
                else:
                    povzrocitelj = ''
            if sklad in slo_sklad.keys():
                sklad = slo_sklad[sklad]
            leto, mesec, dan, h, i, s = xlrd.xldate_as_tuple(datum, dat.datemode)
            sql_datum = str(leto) + '-' + str(mesec) + '-' + str(dan)
            teza = int(teza)
            sez_podatkov[(kl_st, teza)]  = {'pov': povzrocitelj, 'op_uv': opomba_uvoz, 'skl': sklad, 'dat_uv': sql_datum}
            # zato da bomo dopolnili še v primeru izvoza, ti ločujemo glede kl. številke in težo saj se trenutno ne ponavlje
    izhod = dat.sheet_by_index(5)
    # 297 vrstic
    for i in range(1, 297):
        kl_st =izhod.cell_value(i, 0)
        opomba_izvoz = izhod.cell_value(i, 1)
        teza = izhod.cell_value(i, 2)
        datum_izv = izhod.cell_value(i, 3)
        sklad = izhod.cell_value(i, 4)
        if teza:
            # pomeni ni prazna vrstica
            # spremenimo datum primeren za SQL
            if opomba_izvoz == 'x':
                opomba_izvoz = ''
            povzrocitelj = povzrocitelj.upper()
            leto1, mesec1, dan1, h, i, s = xlrd.xldate_as_tuple(datum_izv, dat.datemode)
            sql_datum1 = str(leto1) + '-' + str(mesec1) + '-' + str(dan1)
            if (kl_st, teza) in sez_podatkov.keys():
                sez_podatkov[kl_st, teza]['dat_iz'] = sql_datum1
                sez_podatkov[kl_st, teza]['op_iz'] = opomba_izvoz
    uporabnik, podjetja, vrsta_odpadka, skladisce, odpadek = tabele
    with conn:

        vrsta_odpadka.uvozi(slo_klas_ste_ime)

        podjetja.uvozi(slo_id_podjetje)

        skladisce.uvozi(slo_sklad)

        odpadek.uvozi(sez_podatkov)

    conn.execute('VACUUM')


def izprazni_tabele(tabele):
    """
    Izprazni podane tabele.
    """
    for t in tabele:
        t.izprazni()


def ustvari_bazo(conn):
    """
    Izvede ustvarjanje baze.
    """
    tabele = pripravi_tabele(conn)
    izbrisi_tabele(tabele)
    ustvari_tabele(tabele)
    uvozi_podatke(tabele, conn)

def pripravi_tabele(conn):
    """
    Pripravi objekte za tabele.
    """
    uporabnik = Uporabnik(conn)
    podjetja = Podjetja(conn)
    vrsta_odpadka = VrstaOdpadka(conn)
    skladisce = Skladisce(conn)
    odpadek = Odpadek(conn)
    return [uporabnik, podjetja, vrsta_odpadka, skladisce, odpadek]


def ustvari_bazo_ce_ne_obstaja(conn):
    """
    Ustvari bazo, če ta še ne obstaja.
    """
    with conn:
        cur = conn.execute("SELECT COUNT(*) FROM sqlite_master")
        if cur.fetchone() == (0, ):
            ustvari_bazo(conn)
conn = sqlite3.connect('Ekol.sqlite')
ustvari_bazo_ce_ne_obstaja(conn)