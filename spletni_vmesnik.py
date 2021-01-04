from model import *
import sqlite3
import os
from bottle import *

app = default_app()


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
@route('/uvoz_odpadka')
@route('/odvoz_odpadka')
@route('/pregled')
def izberi():
    dejavnost = request.forms.get('dejavnost')
    if dejavnost == 'uvoz':
        # return "<p>Preusmerjam ...</p>"
        return template('uvoz_odpadka.html')
    elif dejavnost == 'izvoz':
        return template('izvoz_odpadka.html')
    elif dejavnost == 'pregled':
        return template('pregled.html')
    else:  # dejavnost == ''
        return "<p>Neveljavna izbira!</p>"


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
    print(opomba)
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
def odvoz_odpadka():
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
        return '''<script>alert("Neustrezni vnos! Prosimo, poskusite ponovno.");</script>''', template('izvoz_odpadka.html')
    
    try:
        odpadek = Odpadek(teza, klasifikacijska_stevilka, skladisce,
         datum_uvoza)

        odpadek.izvozi(datum_izvoza, opomba_izvoza, prejemnik)
        return '''<script>alert("Odpadek je izvožen.");</script>''', template('zacetna_stran.html')

    except:
        return '''<script>alert("Izbranega odpadka ni na skladišču. Poskusi znova!");</script>''', template('izvoz_odpadka.html')


# PREGLED SKLADIŠČENIH ODPADKOV --------------------------------------------------------------------------
@get('/pregled')
def pregled():
    return template('pregled.html')


# @route('/izbira_dejavnosti')
# def izbira_dejavnosti():
#     return '''
#         <form action="/izbira_dejavnosti" method="post">
#             <select value="dejavnost" type="text" />
#             <input value="dejavnost" type="submit" />
#         </form>
#     '''

# @route('/izbira_dejavnosti', method='POST')
# @route('/uvoz_odpadka')
# @route('/odvoz_odpadka')
# @route('/pregled')
# def izberi():
#     dejavnost = request.forms.get('dejavnost')
#     if dejavnost == 'uvoz':
#         # return "<p>Preusmerjam ...</p>"
#         return template('uvoz_odpadka.html')
#     elif dejavnost == 'izvoz':
#         return template('izvoz_odpadka.html')
#     elif dejavnost == 'pregled':
#         return template('pregled.html')
#     else:  # dejavnost == ''
#         return "<p>Neveljavna izbira!</p>"


# -----------------------------------------------------------------------------------------------------
# @error(404)
# def error404(error):
#     return 'Nothing here, sorry.'


# ----------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    run(app, host='localhost', port=port, debug=True, reloader=True)

