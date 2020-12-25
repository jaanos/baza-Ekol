import baza
import sqlite3
from geslo import sifriraj_geslo, preveri_geslo

conn = sqlite3.connect('Ekol.sqlite')
baza.ustvari_bazo_ce_ne_obstaja(conn)
conn.execute('PRAGMA foreign_keys = ON')

uporabnik, podjetja, vrsta_odpadka, skladisce, odpadek = baza.pripravi_tabele(conn)


class LoginError(Exception):
    """
    Napaka ob napačnem uporabniškem imenu ali geslu.
    """
    pass


class Uporabnik:
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



class Podjetja:
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


class VrstaOdpadka:
    def __init__(self, klasifikacijska_stevilka, naziv):
        self.klasifikacijska_stevilka = klasifikacijska_stevilka
        self.naziv = naziv
    def __str__(self):
        return self.naziv
    def dodaj_v_bazo(self):
        with conn:
            vrsta_odpadka.dodaj_vrstico(klasifikacijska_stevilka=self.klasifikacijska_stevilka, naziv=self.naziv)

class Skladisce:
    def __init__(self, id, ime):
        self.id = id
        self.ime = ime
    def __str__(self):
        return self.ime
    def dodaj_v_bazo(self):
        with conn:
            skladisce.dodaj_vrstico(ime=self.ime, id=self.id)

class Odpadek:
    def __init__(self, id, teza, povzrocitelj, klasifikacijska_stevilka, skladisce, datum_uvoza, opomba_uvoza=None, datum_izvoza=None, opomba_izvoza=None, prejemnik=None):
        self.id = id
        self.teza = teza
        self.povzrocitelj = povzrocitelj
        self.klasifikacijska_stevilka = klasifikacijska_stevilka
        self.skladisce = skladisce
        self.datumm_uvoza = datum_uvoza
        self.opomba_uvoza = opomba_uvoza
        self.datum_izvoza = datum_izvoza
        self.opomba_izvoza = opomba_izvoza
        self.prejemnik = prejemnik
    def dodaj_v_bazo(self, teza, povzrocitelj, klasifikacijska_stevilka, skladisce, datum_uvoza):
        slo = dict()
        slo['pov'] = povzrocitelj
        slo['pre'] = self.prejemnik
        slo['dat_uv'] = datumm_uvoza
        slo['op_uv'] = self.opomba_uvoza
        slo['dat_iz'] = self.datum_izvoza
        slo['op_iz'] = self.opomba_izvoza
        slo['skl'] = skladisce
        odpadek.dodaj_vrstico(klasifikacijska_stevilka, teza, slo)
