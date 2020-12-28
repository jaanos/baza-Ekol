import os
import sqlite3
import json
# import xlrd
# import sys
# import openpyxl.reader.excel
# import openpyxl.workbook
from geslo import sifriraj_geslo

PARAM_FMT = ":{}"


class Ekol:
    '''
        Razred, ki predstavlja tabelo v bazi.
        Polja razreda:
            - ime: ime tabele
            - podatki: ime datoteke s podatki ali None
    '''
    ime = None
    podatki = None

    def __init__(self, conn):
        '''
            Konstruktor razreda.
        '''
        self.conn = conn


    def ustvari(self):
        '''
            Metoda za ustvarjanje tabele.
        '''
        raise NotImplementedError


    def uvozi(self):
        '''
            Metoda za uvažanke podatkov.
            Podrazredi morajo povoziti to metodo.
        '''
        raise NotImplementedError


    def izbrisi(self):
        '''
            Metoda za brisanje tabele.
        '''
        self.conn.execute("DROP TABLE IF EXISTS {};".format(self.ime))


    def izprazni(self):
        '''
            Metoda za praznjenje tabele.
        '''
        self.conn.execute("DELETE FROM {};".format(self.ime))


    def dodajanje(self, stolpci=None):
        '''
            Metoda za gradnjo poizvedbe.
            Argumenti:
                - stolpci: tabela stolpcev
        '''
        return "INSERT INTO {} ({}) VALUES ({});" \
            .format(self.ime, ", ".join(stolpci),
                    ", ".join(PARAM_FMT.format(s) for s in stolpci))


    def dodaj_vrstico(self, /, **podatki):
        '''
            Metoda za dodajanje vrstice.
            Argumenti:
                - poimenovani parametri: vrednosti v ustreznih stolpcih
        '''
        podatki = {kljuc: vrednost for kljuc, vrednost in podatki.items() if vrednost is not None}
        poizvedba = self.dodajanje(podatki.keys())
        cur = self.conn.execute(poizvedba, podatki)
        return cur.lastrowid


# ---------------------------------------------------------------------------------------------------------
class Uporabnik(Ekol):
    '''
        Ekol za uporabnike.
    '''
    ime = "uporabnik"

    def ustvari(self):
        '''
            Ustvari tabelo uporabnik.
        '''
        self.conn.execute('''
            CREATE TABLE uporabnik (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                ime       TEXT NOT NULL UNIQUE,
                zgostitev TEXT NOT NULL,
                sol       TEXT NOT NULL
            )
        ''')


    def dodaj_vrstico(self, /, **podatki):
        '''
            Dodaj uporabnika.
            Če sol ni podana, zašifrira podano geslo.
            Argumenti:
                - poimenovani parametri: vrednosti v ustreznih stolpcih
        '''
        if podatki.get("sol", None) is None and podatki.get("zgostitev", None) is not None:
            podatki["zgostitev"], podatki["sol"] = sifriraj_geslo(podatki["zgostitev"])
        return super().dodaj_vrstico(**podatki)


# -------------------------------------------------------------------------------------------------------
class Podjetje(Ekol):
    ime = 'podjetje'
    # podatki = {ime: podjetje}

    def ustvari(self):
        self.conn.execute('''
                CREATE TABLE podjetje (
                id  INTEGER PRIMARY KEY AUTOINCREMENT,
                ime TEXT    NOT NULL
            );''')


    def dodaj_vrstico(self, /, **podatki):
        '''
            Če podjetja še ni v bazi, ga doda.
        '''
        podjetje = self.conn.execute("""
            SELECT id FROM podjetje
            WHERE ime = :ime;
        """, podatki).fetchone()

        if podjetje is None:
            # to podjetje je novo
            return super().dodaj_vrstico(**podatki)
        else:
            id, = podjetje
            return id


    def uvozi(self, sl_id_podjetje):
        for podjetje in sl_id_podjetje:
            nov = dict()
            nov['ime'] = podjetje
            self.dodaj_vrstico(**nov)

# ---------------------------------------------------------------------------------------------------------
class VrstaOdpadka(Ekol):
    ime = 'vrsta_odpadka'
    # podatki = {klasifikacijska_stevilka: kl_stevilka, naziv: ime}
    
    def ustvari(self):
        self.conn.execute('''
                CREATE TABLE vrsta_odpadka (
                    klasifikacijska_stevilka VARCHAR (9) PRIMARY KEY
                                             CHECK (klasifikacijska_stevilka LIKE '__ __ __%'),
                    naziv                    TEXT        NOT NULL
                );''')
    
    
    def uvozi(self, sl_klas_st_ime):
        for klas, ime in sl_klas_st_ime.items():
            nov = dict()
            nov['klasifikacijska_stevilka'] = klas
            nov['naziv'] = ime
            self.dodaj_vrstico(**nov)


# ------------------------------------------------------------------------------------------------------------
class Skladisce(Ekol):
    ime = 'skladisce'
    # podatki = {id: st, ime: ime}

    def ustvari(self):
        self.conn.execute('''
                CREATE TABLE skladisce (
                    id  INTEGER PRIMARY KEY,
                    ime TEXT    NOT NULL
                );''')


    def uvozi(self, sl_sklad):
        for ime, st in sl_sklad.items():
            nov = {'id': st, 'ime': ime} 
            self.dodaj_vrstico(**nov)


# ---------------------------------------------------------------------------------------------------------------
class Odpadek(Ekol):
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
        for (kl, teza), sl in sez_podatkov.items():
            nov = dict()
            nov['klasifikacijska_stevilka'] = kl
            nov['teza'] = teza
            nov['prejemnik'] = ''
            nov['povzrocitelj'] = sl.get('pov', '')
            nov['opomba_uvoz'] = sl.get('op_uv', '')
            nov['skladisce'] = sl.get('skl', '')
            nov['datum_uvoza'] = sl.get('dat_uv', '')
            nov['datum_izvoza'] = sl.get('dat_iz', '')
            nov['opomba_izvoz'] = sl.get('op_iz', '')
            self.dodaj_vrstico(**nov)
    

# ---------------------------------------------------------------------------------------------------------------------------
# KONEC RAZREDOV ------------------------------------------------------------------------------------------------------------
def ustvari_tabele(tabele):
    '''
        Ustvari podane tabele.
    '''
    for t in tabele:
        t.ustvari()


def izbrisi_tabele(tabele):
    '''
        Izbriši podane tabele.
    '''
    for t in tabele:
        t.izbrisi()


def izprazni_tabele(tabele):
    '''
        Izprazni podane tabele.
    '''
    for t in tabele:
        t.izprazni()


def uvozi_podatke(tabele, conn):
    '''
        Uvozi podatke v podane tabele.
    '''
#    sl_sklad = {'Sklad-3': 3, 'Sklad-7': 7}
#    
#    dat_1 = xlrd.open_workbook(os.path.join(sys.path[0], "ND_00_Seznam klasifikacij po dovoljenjih.xlsx"))
#    dat_2 = xlrd.open_workbook(os.path.join(sys.path[0], "001_Evidenca_odpadko_v_skladiscu.xlsm"))
#
#    list1 = dat_1.sheet_by_index(1)
#    sl_klas_st_ime = dict()
#    for i in range(1, list1.nrows):  # po vrsticah
#        klas_st = list1.cell_value(i, 0)
#        ime = list1.cell_value(i, 1)
#        sl_klas_st_ime[klas_st] = ime
#
#    # napolnimo tabelo podjetje
#    list3 = dat_2.sheet_by_index(4)
#    sl_id_podjetje = dict()  # zato da bo id podjetja nekje shranjen
#    mn_podatkov = set()
#    st = 1
#    for i in range(1, list3.nrows):
#        vred = list3.cell_value(i, 1)
#        if vred and vred not in {'x', 'X'}:
#            podatek = vred.upper()
#            if podatek not in mn_podatkov:
#                # z velikimi črkami zaradi neusklajenosti pisanja v excellu
#                mn_podatkov.add(podatek)
#                sl_id_podjetje[podatek] = st
#                st += 1
#    
#    # napolnimo tabelo podjetje
#    vhod = dat_2.sheet_by_index(4)  # 334 vrstic
#    sl_podatkov = dict()
#    povzrocitelj = ''
#    for i in range(1, vhod.nrows):
#        klas_st = vhod.cell_value(i, 0)
#        povzrocitelj = vhod.cell_value(i, 1).upper()
#        opomba_uvoz = vhod.cell_value(i, 2)
#        teza = vhod.cell_value(i, 3)
#        skladisce = vhod.cell_value(i, 4)
#        datum = vhod.cell_value(i, 5)
#        
#        if datum and teza not in {1, '', 1.0}:  # teža 1 pomeni napako
#            # vrstica ni prazna
#            # spremenimo datum primeren za SQL
#            teza = int(teza)
#            if opomba_uvoz in {'x', 'X'}:
#                opomba_uvoz = ''
#            if povzrocitelj in sl_id_podjetje:
#                povzrocitelj = sl_id_podjetje[povzrocitelj]
#            else:
#                # nov povzročitelj
#                if povzrocitelj in {'x', 'X'}:
#                    # neznan povzročitelj
#                    povzrocitelj = ''
#
#            skladisce = sl_sklad[skladisce]
#            leto, mesec, dan, _, _, _ = xlrd.xldate_as_tuple(datum, dat_1.datemode)
#            sql_datum = '{}-{}-{}'.format(leto, mesec, dan)
#
#            # da bomo lahoko dopolnili še v primeru izvoza, ločujemo glede (klas. št., teža), saj se trenutno ne ponavljajo
#            sl_podatkov[(klas_st, teza)]  = {'pov': povzrocitelj, 'op_uv': opomba_uvoz, 'skl': skladisce, 'dat_uv': sql_datum}
#
#    izhod = dat_2.sheet_by_index(5)  # 297 vrstic
#    for i in range(1, izhod.nrows):
#        klas_st = izhod.cell_value(i, 0)
#        opomba_izvoz = izhod.cell_value(i, 1)
#        teza = izhod.cell_value(i, 2)
#        datum_izv = izhod.cell_value(i, 3)
#        # skladisce = izhod.cell_value(i, 4)
#
#        if teza:
#            # ni prazna vrstica
#            teza = int(teza)
#
#            if opomba_izvoz in {'x', 'X'}:
#                # ni opombe
#                opomba_izvoz = ''
#
#            # spremenimo datum v primerenega za SQL
#            leto, mesec, dan, _ ,_, _ = xlrd.xldate_as_tuple(datum_izv, dat_1.datemode)
#            sql_datum = '{}-{}-{}'.format(leto, mesec, dan)
#            
#            if (klas_st, teza) in sl_podatkov.keys():
#                # ta podatek je bil  res uvožen
#                sl_podatkov[klas_st, teza]['dat_iz'] = sql_datum
#                sl_podatkov[klas_st, teza]['op_iz'] = opomba_izvoz
#
#    uporabnik, podjetja, vrsta_odpadka, skladisce, odpadek = tabele
#    with conn:
#        vrsta_odpadka.uvozi(sl_klas_st_ime)
#        podjetja.uvozi(sl_id_podjetje)
#        skladisce.uvozi(sl_sklad)
#        odpadek.uvozi(sl_podatkov)
#
#    conn.execute('VACUUM')
    with open('podatki.json', encoding='utf-8') as podatki:
        data = json.load(podatki)
    slo_sklad = data['slo_sklad']
    slo_id_podjetje = data['slo_id_podjetje']
    slo_klas_ste_ime = data['slo_klas_ste_ime']
    vmesni = data['sez_podatkov']
    slo_odpadki = dict()
    for sez in vmesni.values():
        slo_odpadki[sez[0], sez[1]] = {
                                        sez[2][0]: sez[2][1],
                                        sez[3][0]: sez[3][1],
                                        sez[4][0]: sez[4][1],
                                        sez[5][0]: sez[5][1]
        }

    uporabnik, podjetja, vrsta_odpadka, skladisce, odpadek = tabele
    with conn:

        vrsta_odpadka.uvozi(slo_klas_ste_ime)

        podjetja.uvozi(slo_id_podjetje)

        skladisce.uvozi(slo_sklad)

        odpadek.uvozi(slo_odpadki)

    conn.execute('VACUUM')


def pripravi_tabele(conn):
    '''
        Pripravi objekte za tabele.
    '''
    uporabnik = Uporabnik(conn)
    podjetje = Podjetje(conn)
    vrsta_odpadka = VrstaOdpadka(conn)
    skladisce = Skladisce(conn)
    odpadek = Odpadek(conn)
    return [uporabnik, podjetje, vrsta_odpadka, skladisce, odpadek]


def ustvari_bazo(conn):
    '''
        Izvede ustvarjanje baze.
    '''    
    tabele = pripravi_tabele(conn)
        
    izbrisi_tabele(tabele)
    ustvari_tabele(tabele)
    uvozi_podatke(tabele, conn)


def ustvari_bazo_ce_ne_obstaja(conn):
    '''
        Ustvari bazo, če ta še ne obstaja.
    '''
    with conn:
        cur = conn.execute("SELECT COUNT(*) FROM sqlite_master")
        if cur.fetchone() == (0, ):
            ustvari_bazo(conn)


# conn = sqlite3.connect(os.path.join(sys.path[0], 'Ekol.sqlite'))
conn = sqlite3.connect('Ekol.sqlite')
ustvari_bazo_ce_ne_obstaja(conn)