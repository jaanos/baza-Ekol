import json
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
class Opomba(Ekol):
    ime = 'opomba'
    

    def ustvari(self):
        self.conn.execute('''
                CREATE TABLE opomba (
                id  INTEGER PRIMARY KEY AUTOINCREMENT,
                ime TEXT    NOT NULL
            );''')


    def dodaj_vrstico(self, /, **podatki):
        '''
            Če opombe še ni v bazi, jo doda.
        '''
        opomba = self.conn.execute("""
            SELECT id FROM opomba
            WHERE ime = :ime;
        """, podatki).fetchone()

        if opomba is None:
            # to podjetje je novo
            return super().dodaj_vrstico(**podatki)
        else:
            id, = opomba
            return id


    def uvozi(self, slo_opombe):
        for opomba in slo_opombe:
            nov = dict()
            nov['ime'] = opomba
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
                    povzrocitelj             INTEGER     REFERENCES podjetje (id),
                    prejemnik                INTEGER     REFERENCES podjetje (id),-- če ni obvezen podatek, brez NOT NULL
                    datum_uvoza              DATE        NOT NULL,
                    opomba_uvoz              INTEGER     REFERENCES opomba (id),
                    datum_izvoza             DATE,
                    opomba_izvoz             INTEGER     REFERENCES opomba (id),
                    klasifikacijska_stevilka VARCHAR (9) NOT NULL
                                                         REFERENCES vrsta_odpadka (klasifikacijska_stevilka),
                    skladisce                INTEGER     REFERENCES skladisce (id) 
                );''')
    
    
    def uvozi(self, sez_podatkov):
        for (kl, teza), sl in sez_podatkov.items():
            sl['klasifikacijska_stevilka'] = kl
            sl['teza'] = teza
            self.dodaj_vrstico(**sl)


    def za_izvoz(self, id, sl):
        self.conn.execute('''
            UPDATE odpadek
                SET prejemnik = ?,
                    datum_izvoza = ?,
                    opomba_izvoz = ?
                WHERE id = ?;''',
            [
            sl['prejemnik'],
            sl['datum_izvoza'],
            sl['opomba_izvoz'],
            id])
    

    

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
    with open('podatki.json', encoding='utf-8') as podatki:
        data = json.load(podatki)
    slo_sklad = data['slo_sklad']
    slo_id_podjetje = data['slo_id_podjetje']
    slo_klas_ste_ime = data['slo_klas_ste_ime']
    slo_opombe = data['slo_opombe']
    vmesni = data['sez_podatkov']
    slo_odpadki = dict()
    for sez in vmesni.values():
        slo_odpadki[sez[0], sez[1]] = {
                                        sez[2][0]: sez[2][1],
                                        sez[3][0]: sez[3][1],
                                        sez[4][0]: sez[4][1],
                                        sez[5][0]: sez[5][1]
        }

    uporabnik, podjetja, vrsta_odpadka, skladisce, odpadek, opomba = tabele
    with conn:

        vrsta_odpadka.uvozi(slo_klas_ste_ime)

        podjetja.uvozi(slo_id_podjetje)

        skladisce.uvozi(slo_sklad)

        odpadek.uvozi(slo_odpadki)

        opomba.uvozi(slo_opombe)

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
    opomba = Opomba(conn)
    return [uporabnik, podjetje, vrsta_odpadka, skladisce, odpadek, opomba]


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
