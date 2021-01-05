from baza import *
import sqlite3
from geslo import sifriraj_geslo, preveri_geslo

conn = sqlite3.connect('Ekol.sqlite')
ustvari_bazo_ce_ne_obstaja(conn)
conn.execute('PRAGMA foreign_keys = ON')

uporabnik, podjetja, vrsta_odpadka, skladisce, odpadek, opomba = pripravi_tabele(conn)


class LoginError(Exception):
    """
    Napaka ob napačnem uporabniškem imenu ali geslu.
    """
    pass


class Uporabnik(Ekol):
    """
    Razred za uporabnika.
    """

    def __init__(self, ime, *, id=None):
        """
        Konstruktor uporabnika.
        """
        self.id = id
        self.ime = ime

    def __str__(self):
        """
        Znakovna predstavitev uporabnika.
        Vrne uporabniško ime.
        """
        return self.ime

    @staticmethod
    def prijava(ime, geslo):
        """
        Preveri, ali sta uporabniško ime geslo pravilna.
        """
        sql = """
            SELECT id, zgostitev, sol FROM uporabnik
            WHERE ime = ?
        """
        try:
            id, zgostitev, sol = conn.execute(sql, [ime]).fetchone()
            if preveri_geslo(geslo, zgostitev, sol):
                return Uporabnik(ime, id=id)
        except TypeError:
            pass
        raise LoginError(ime)

    def dodaj_v_bazo(self, geslo):
        """
        V bazo doda uporabnika s podanim geslom.
        """
        assert self.id is None
        zgostitev, sol = sifriraj_geslo(geslo)
        with conn:
            self.id = uporabnik.dodaj_vrstico(ime=self.ime, zgostitev=zgostitev, sol=sol)



class Podjetja(Ekol):
    def __init__(self, ime, id = None):
        self.id = id
        self.ime = ime
   
   
    def __str__(self):
        return self.ime
   
   
    def dodaj_v_bazo(self):
        assert self.id is None
        with conn:
            id = podjetja.dodaj_vrstico(ime=self.ime)
            self.id = id

    @staticmethod
    def ime_podjetja(index):
        '''
            vrne ime podjetja, ki mu pripada dani index
        '''
        return conn.execute(''' SELECT ime FROM podjetje
                            WEHERE id = ?;''', (id)).fetchone()


class Opomba(Ekol):
    def __init__(self, ime, id = None):
        self.id = id
        self.ime = ime
   
   
    def __str__(self):
        return self.ime
   
   
    def dodaj_v_bazo(self):
        assert self.id is None
        with conn:
            id = opomba.dodaj_vrstico(ime=self.ime)
            self.id = id

class VrstaOdpadka(Ekol):
    def __init__(self, klasifikacijska_stevilka, naziv):
        self.klasifikacijska_stevilka = klasifikacijska_stevilka
        self.naziv = naziv
    
    
    def __str__(self):
        return self.naziv
    
    
    def dodaj_v_bazo(self):
        with conn:
            vrsta_odpadka.dodaj_vrstico(klasifikacijska_stevilka=self.klasifikacijska_stevilka, naziv=self.naziv)


class Skladisce(Ekol):
    def __init__(self, id, ime=None):
        self.id = id
        self.ime = ime
    
    
    def __str__(self):
        return self.ime
    
    
    def dodaj_v_bazo(self):
        with conn:
            skladisce.dodaj_vrstico(ime=self.ime, id=self.id)


    @staticmethod
    def teza(id):
        koliko = conn.execute('''
            SELECT SUM(teza) 
                FROM odpadek
                WHERE skladisce = ? AND
                datum_izvoza IS NULL;''',
            [
            id]).fetchone()
        return koliko[0]

    @staticmethod
    def st_kl_skladisce(skladisce):
        sql = '''SELECT vrsta_odpadka.naziv,
                        odpadek.klasifikacijska_stevilka,
                        COUNT(odpadek.klasifikacijska_stevilka) 
                    FROM odpadek
                        JOIN
                        vrsta_odpadka ON odpadek.klasifikacijska_stevilka = vrsta_odpadka.klasifikacijska_stevilka
                    WHERE skladisce = ? AND 
                        datum_izvoza IS NULL
                    GROUP BY odpadek.klasifikacijska_stevilka;
                    '''
        for ime, kl, st in conn.execute(sql, [skladisce]):
            print(f'V skladišči {skladisce} je {ime}({kl}) {st} kosov.')
            # zato da vidim da dela izpišem, za vmesnik bova potrebovala yield pomoje
            #yield (f'V skladišči {skladisce} je {ime}({kl}) {st} kosov.')


    @staticmethod
    def skladisce_kl_st_uvoz_stolpci(skladisce, kl, *stolpci):
        '''
            v *stolpaci so lahko absolutno poimenova stolpci, brez argumentov se uporablja:
            odpadek.id,
            odpadek.klasifikacijska_stevilka,
            odpadek.teza,
            vrsta_odpadka.naziv,
            opomba.ime,
            skladisce.ime,
            podjetje.ime,
            odpadek.datum_uvoza
        '''
        if not stolpci:
            poizvedba = '''SELECT   odpadek.id,
                                    odpadek.klasifikacijska_stevilka,
                                    vrsta_odpadka.naziv,
                                    odpadek.teza,
                                    opomba.ime,
                                    skladisce.ime,
                                    podjetje.ime,
                                    odpadek.datum_uvoza
                                FROM odpadek
                                    JOIN
                                    vrsta_odpadka ON odpadek.klasifikacijska_stevilka = vrsta_odpadka.klasifikacijska_stevilka
                                    LEFT JOIN
                                    opomba ON odpadek.opomba_uvoz = opomba.id
                                    JOIN
                                    skladisce ON odpadek.skladisce = skladisce.id
                                    LEFT JOIN
                                    podjetje ON odpadek.povzrocitelj = podjetje.id
                                WHERE 
                                    odpadek.skladisce = ? AND 
                                    odpadek.klasifikacijska_stevilka = ? AND 
                                    odpadek.datum_izvoza IS NULL;'''
        else:
            poizvedba = '''SELECT {} 
                            FROM odpadek
                                    JOIN
                                    vrsta_odpadka ON odpadek.klasifikacijska_stevilka = vrsta_odpadka.klasifikacijska_stevilka
                                    LEFT JOIN
                                    opomba ON odpadek.opomba_uvoz = opomba.id
                                    JOIN
                                    skladisce ON odpadek.skladisce = skladisce.id
                                    LEFT JOIN
                                    podjetje ON odpadek.povzrocitelj = podjetje.id
                                WHERE 
                                    odpadek.skladisce = ? AND 
                                    odpadek.klasifikacijska_stevilka = ? AND 
                                    odpadek.datum_izvoza IS NULL;''' .format(", ".join(stolpci))
        for vrstica in conn.execute(poizvedba, [skladisce, kl]):
            print((vrstica))


    @staticmethod
    def skladisce_splosno_stolpci(*stolpci):
        '''
            v *stolpaci so lahko absolutno poimenova stolpci, brez argumentov se uporablja:
            odpadek.id,
            odpadek.teza,
            odpadek.klasifikacijska_stevilka,
            vrsta_odpadka.naziv,
            opomba.ime,
            opomba_izvoza.ime, \
            skladisce.ime,      |
            podjetje.ime,       |
            prejemnik.ime, => če vas zanima kaj glede izvoza vpišite to brez parametra
            odpadek.datum_uvoza,
            odpadek.datum_izvoza

            torej po želji lahko kličemo zgolj:
            odpadek.id,
            odpadek.teza,
            odpadek.klasifikacijska_stevilka,
            vrsta_odpadka.naziv,
            opomba.ime,
            skladisce.ime,
            podjetje.ime,
            odpadek.datum_uvoza,
            odpadek.datum_izvoza
        '''
        if not stolpci:
            poizvedba = '''SELECT   odpadek.id,
                                    odpadek.teza,
                                    odpadek.klasifikacijska_stevilka,
                                    vrsta_odpadka.naziv,
                                    opomba.ime,
                                    opomba_izvoza.ime,
                                    skladisce.ime,
                                    podjetje.ime,
                                    prejemnik.ime,
                                    odpadek.datum_uvoza,
                                    odpadek.datum_izvoza
                                FROM odpadek
                                    LEFT JOIN
                                    vrsta_odpadka ON odpadek.klasifikacijska_stevilka = vrsta_odpadka.klasifikacijska_stevilka
                                    LEFT JOIN
                                    opomba ON odpadek.opomba_uvoz = opomba.id
                                    LEFT JOIN
                                    opomba AS opomba_izvoza ON odpadek.opomba_izvoz = opomba_izvoza.id
                                    LEFT JOIN
                                    skladisce ON odpadek.skladisce = skladisce.id
                                    LEFT JOIN
                                    podjetje ON odpadek.povzrocitelj = podjetje.id
                                    LEFT JOIN
                                    podjetje AS prejemnik ON odpadek.prejemnik = prejemnik.id;
                                    '''
        else:
            poizvedba = '''SELECT {} 
                                FROM odpadek
                                LEFT JOIN
                                vrsta_odpadka ON odpadek.klasifikacijska_stevilka = vrsta_odpadka.klasifikacijska_stevilka
                                LEFT JOIN
                                opomba ON odpadek.opomba_uvoz = opomba.id
                                LEFT JOIN
                                skladisce ON odpadek.skladisce = skladisce.id
                                LEFT JOIN
                                podjetje ON odpadek.povzrocitelj = podjetje.id;
                                ''' .format(", ".join(stolpci))
        for vrstica in conn.execute(poizvedba):
            print((vrstica))



class Odpadek(Ekol):
    def __init__(self, teza, klasifikacijska_stevilka, skladisce,
     datum_uvoza, povzrocitelj = None, opomba_uvoz=None):
        self.teza = teza
        if povzrocitelj:
            self.povzrocitelj = povzrocitelj.upper()
        else:
            self.povzrocitelj = None
        self.klasifikacijska_stevilka = klasifikacijska_stevilka
        self.skladisce = skladisce
        self.datum_uvoza = datum_uvoza
        self.opomba_uvoz = opomba_uvoz
        
        # teh pri dodajanju ni -> se jih dodeli kasneje ob predelavi    
        self.datum_izvoza = None
        self.opomba_izvoza = None
        self.prejemnik = None
    

    def dodaj_v_bazo(self):
        sl = dict()
        sl['klasifikacijska_stevilka'] = self.klasifikacijska_stevilka
        sl['teza'] = self.teza 
        sl['datum_uvoza'] = self.datum_uvoza
        sl['opomba_uvoz'] = self.opomba_uvoz       
        # skladišče je vnešeno kot št. {3, 7}
        sl['skladisce'] = self.skladisce

        # potrebujemo index
        if self.povzrocitelj:
            sl['povzrocitelj'] = conn.execute("""
                    SELECT id FROM podjetje
                    WHERE ime = ?;
                """, [self.povzrocitelj]).fetchone()[0]
        else:
            sl['povzrocitelj']  = None
        with conn:
            odpadek.dodaj_vrstico(**sl)


    def izvozi(self, datum_izvoza, opomba_izvoz=None, prejemnik=None):
        self.datum_izvoza = datum_izvoza
        self.opomba_izvoz = opomba_izvoz
        self.prejemnik = prejemnik
        sl = dict()
        if self.prejemnik:
            sl['prejemnik'] = conn.execute("""
                    SELECT id FROM podjetje
                    WHERE ime = ?;
                """, [self.prejemnik.upper()]).fetchone()[0]
        else:
            sl['prejemnik'] = None
        sl['datum_izvoza'] = datum_izvoza
        sl['opomba_izvoz'] = opomba_izvoz
    
        id = conn.execute("""
                    SELECT id FROM odpadek
                    WHERE
                    teza = ? AND
                    datum_uvoza = ? AND
                    klasifikacijska_stevilka = ? AND
                    skladisce = ?
                """, [self.teza,
                    self.datum_uvoza,
                    self.klasifikacijska_stevilka,
                    self.skladisce]).fetchone()[0]
        with conn:
            odpadek.za_izvoz(id, sl)