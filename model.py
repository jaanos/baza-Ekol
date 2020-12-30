from baza import *
import sqlite3
from geslo import sifriraj_geslo, preveri_geslo

conn = sqlite3.connect('Ekol.sqlite')
ustvari_bazo_ce_ne_obstaja(conn)
conn.execute('PRAGMA foreign_keys = ON')

uporabnik, podjetja, vrsta_odpadka, skladisce, odpadek = pripravi_tabele(conn)


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
    def __init__(self, id, ime):
        self.id = id
        self.ime = ime
    
    
    def __str__(self):
        return self.ime
    
    
    def dodaj_v_bazo(self):
        with conn:
            skladisce.dodaj_vrstico(ime=self.ime, id=self.id)


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
                """, [self.prejemnik]).fetchone()[0]
        else:
            sl['prejemnik'] = None
        sl['datum_izvoza'] = datum_izvoza
        sl['opomba_izvoz'] = opomba_izvoz
    
        id = conn.execute("""
                    SELECT id FROM odpadek
                    WHERE
                    teza = ? AND
                    datum_uvoza = ? AND
                    opomba_uvoz = ? AND
                    klasifikacijska_stevilka = ? AND
                    skladisce = ?
                """, [self.teza,
                    self.datum_uvoza,
                    self.opomba_uvoz,
                    self.klasifikacijska_stevilka,
                    self.skladisce]).fetchone()[0]
        with conn:
            odpadek.execute('''
                UPDATE odpadek SET 
                prejemnik = ?, 
                datum_izvoza = ?, 
                opomba_izvoz = ?
                WHERE id = ?;''',
                [id,
                sl['prejemnik'],
                sl['datum_izvoza'],
                sl['opomba_izvoz']])