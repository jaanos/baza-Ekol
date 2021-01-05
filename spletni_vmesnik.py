from model import *
import sqlite3
import os
from bottle import *

app = default_app()


def template(predloga, /, opozorilo=None, **kwargs):
    """
    Povožena funkcija za predloge s podajanjem spremenljivke opozorilo.
    """
    from bottle import template
    return template(predloga, opozorilo=opozorilo, **kwargs)


# STATIC -----------------------------------------------------------------------------------------------
@get('/static/<filename:path>')
def server_static(filename):
    return static_file(filename, root='static')


# -------------------------------------------------------------------------------------------------------
# SPLETNE STRANI ----------------------------------------------------------------------------------------

# ZAČETNA STRAN -----------------------------------------------------------------------------------------
@route('')
@route('/')
def zacetna_stran():
    return template('zacetna_stran.html')


@route('/izbira_dejavnosti')
def izbira_dejavnosti():
    return '''
        <form action="/izbira_dejavnosti" method="post">
            <select value="dejavnost" type="text" />
            <input value="dejavnost" type="submit" />
        </form>
    '''

@route('/izbira_dejavnosti', method='POST')
def izberi():
    pot = {'uvoz': '/uvoz_odpadka',
           'izvoz': '/izvoz_odpadka',
           'pregled': '/pregled'}.get(request.forms.get('dejavnost'), None)
    if pot is None:
        return template('zacetna_stran.html', opozorilo="Neveljavna izbira! Prosimo, poskusite ponovno.")
    redirect(pot)


# UVOZ ODPADKA ------------------------------------------------------------------------------------------
@get('/uvoz_odpadka')
def uvoz_odpadka():
    return template('uvoz_odpadka.html')


@route('/podatki_o_odpadku')
def podatki_o_odpadku():
    return '''
        <form action="/podatki_o_odpadku" method="post">

            <select value="teza" type="int" />
            <input value="teza" type="submit" />

            <select value="povzrocitelj" type="text" />
            <input value="povzrocitelj" type="submit" />

            <select value="datum_uvoza" type="date" />
            <input value="datum_uvoza" type="submit" />

            <select value="klasifikacijska_stevilka" type="text" />
            <input value="klasifikacijska_stevilka" type="submit" />

            <select value="skladisce" type="int" />
            <input value="skladisce" type="submit" />

            <select value="opomba_uvoza" type="text" />
            <input value="opomba_uvoza" type="submit" />

        </form>
    '''


@route('/podatki_o_odpadku', method='POST')
def dodaj_odpadek():
    teza = request.forms.get('teza')
    povzrocitelj = request.forms.get('povzrocitelj')
    datum_uvoza = request.forms.get('datum_uvoza')
    klasifikacijska_stevilka = request.forms.get('klasifikacijska_stevilka')
    skladisce = request.forms.get('skladisce')
    opomba_uvoza = request.forms.get('opomba_uvoza')   
    
    if opomba_uvoza == '':
        opomba_uvoza = None
    if povzrocitelj == '':
        povzrocitelj = None
    
    if teza == '' or datum_uvoza == '' or klasifikacijska_stevilka == '' or skladisce == '':
        return '''<script>alert("Neustrezni vnos! Prosimo, poskusite ponovno.");</script>''', template('uvoz_odpadka.html')
    
    odpadek = Odpadek(teza, klasifikacijska_stevilka, skladisce,
     datum_uvoza, povzrocitelj, opomba_uvoza)
    
    odpadek.dodaj_v_bazo()
    
    return '''<script>alert("Odpadek je uvožen.");</script>''', template('zacetna_stran.html')


# ODVOZ ODPADKA -----------------------------------------------------------------------------------------
@get('/izvoz_odpadka')
def izvoz_odpadka():
    return template('izvoz_odpadka.html')


@route('/podatki_o_odpadku_izvoz')
def podatki_o_odpadku_izvoz():
    return '''
        <form action="/podatki_o_odpadku" method="post">

            <select value="teza" type="int" />
            <input value="teza" type="submit" />

            <select value="klasifikacijska_stevilka" type="text" />
            <input value="klasifikacijska_stevilka" type="submit" />

            <select value="datum_uvoza" type="date" />
            <input value="datum_uvoza" type="submit" />

            <select value="skladisce" type="int" />
            <input value="skladisce" type="submit" />

            <select value="prejemnik" type="text" />
            <input value="prejemnik" type="submit" />

            <select value="datum_izvoza" type="date" />
            <input value="datum_izvoza" type="submit" />

            <select value="opomba_izvoza" type="text" />
            <input value="opomba_izvoza" type="submit" />

        </form>
    '''


@route('/podatki_o_odpadku_izvoz', method='POST')
def izvozi_odpadek():
    teza = request.forms.get('teza')
    klasifikacijska_stevilka = request.forms.get('klasifikacijska_stevilka')
    datum_uvoza = request.forms.get('datum_uvoza')
    skladisce = request.forms.get('skladisce')
    datum_izvoza = request.forms.get('datum_izvoza')
    prejemnik = request.forms.get('prejemnik')
    opomba_izvoza = request.forms.get('opomba_izvoza')
    
    if opomba_izvoza == '':
        opomba_izvoza = None
    if prejemnik == '':
        prejemnik = None

    if datum_izvoza == '' or teza == '' or datum_uvoza == '' or klasifikacijska_stevilka == '' or skladisce == '':
        return template('izvoz_odpadka.html', opozorilo="Neustrezni vnos! Prosimo, poskusite ponovno.")
    
    try:
        odpadek = Odpadek(teza, klasifikacijska_stevilka, skladisce,
         datum_uvoza)

        odpadek.izvozi(datum_izvoza, opomba_izvoza, prejemnik)
        returntemplate('zacetna_stran.html', opozorilo="Odpadek je izvožen.")

    except:
        return template('izvoz_odpadka.html', opozorilo="Izbranega odpadka ni na skladišču. Poskusi znova!")


# PREGLED SKLADIŠČENIH ODPADKOV --------------------------------------------------------------------------
@get('/pregled')
def pregled():
    return template('pregled.html')


@route('/filtriraj')
def filtriraj():
    return '''
        <form action="/filtriraj" method="post">
            <select value="pregled" type="text" />
            <input value="pregled" type="submit" />
        </form>
    '''

@route('/filtriraj', method='POST')
def filtriraj_odpadke():
    pot = {'kolicina': '/kolicina',
           'skupna_teza': '/skupna_teza',
           'vsi': '/vsi',
           'zadnji': '/zadnji'}.get(request.forms.get('pregled'), None)
    if pot is None:  # dejavnost == ''
        return template('pregled.html', opozorilo="Neveljavna izbira! Prosimo, poskusite ponovno.")
    redirect(pot)


# KOLIČINA POSAMEZNIH ODPADKOV (GLEDE NA KLAS. ŠT.) ------------------------------------------------------------------------------
@get('/kolicina')
def kolicina_odpadkov():
    return template('kolicina.html')


# SKUPNA TEŽA POSAMEZNIH ODPADKOV V NEKEM SKLADIŠČU -------------------------------------------------------------------------------
@get('/skupna_teza')
def skupna_teza_odpadkov():
    return template('skupna_teza.html')


# VSI ODPADKI V SKLADIŠČU ---------------------------------------------------------------------------------------------------------
@get('/vsi')
def vsi_odpadki():
    return template('vsi.html')


# ZADNJI IZVOZ ZA POSAMEZNO KLAS. ŠT. ODPADKA -------------------------------------------------------------------------------------
@get('/zadnji')
def zadnji_odpadki():
    return template('zadnji.html')




# -----------------------------------------------------------------------------------------------------
# @error(404)
# def error404(error):
#     return 'Nothing here, sorry.'


# ----------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    run(app, host='localhost', port=port, debug=True, reloader=True)

