import os
import sqlite3
import xlrd
import json

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
    with open('podatki.json', encoding='utf-8') as podatki:
        data = json.load(fh)
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