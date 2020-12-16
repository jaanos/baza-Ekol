import os
import sqlite3
import xlrd


def dodaj_vrsta_odpadka(conn, kl_stevilka, ime):
    sql = '''
        INSERT INTO vrsta_odpadka 
        (klasifikacijska_stevilka, naziv) 
        VALUES 
        (?, ?)
    '''
    parametri = [
        kl_stevilka,
        ime,
    ]
    conn.execute(sql, parametri)


def dodaj_podjetje(conn, podjetje):
    sql = '''
        INSERT INTO podjetje 
        (ime) 
        VALUES (?)
    '''
    parametri = [
        podjetje
    ]
    conn.execute(sql, parametri)


def dodaj_skladisce(conn, ime, st):
    sql = '''
        INSERT INTO skladisce 
        (id, ime) 
        VALUES (?, ?)
    '''
    parametri = [
        st,
        ime,
    ]
    conn.execute(sql, parametri)
   


def dodaj_odpadek(conn, kl, teza, sez_podatkov):
    sql = '''
        INSERT INTO odpadek 
        (teza, povzrocitelj, prejemnik, datum_uvoza, opomba_uvoz, datum_izvoza, opomba_izvoz, klasifikacijska_stevilka, skladisce ) 
        VALUES 
        (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    parametri = [
        teza, 
        sez_podatkov.get('pov', ''), 
        '', 
        sez_podatkov.get('dat_uv', ''), 
        sez_podatkov.get('op_uv', ''), 
        sez_podatkov.get('dat_iz', ''), 
        sez_podatkov.get('op_iz', ''), 
        kl, 
        sez_podatkov.get('skl', '')
        ] 
    conn.execute(sql, parametri)

def napolni_tabele(conn, slo_klas_ste_ime, slo_id_podjetje, slo_sklad, sez_podatkov):
    ze_videne_osebe = set()
    idji_zanrov = {}
    ze_videne_oznake = set()
    # najprej napolnimo tabelo z vrsta odpadka
    for kl, ime in slo_klas_ste_ime.items():
        dodaj_vrsta_odpadka(conn, kl, ime)
    for podjetje in slo_id_podjetje:
        dodaj_podjetje(conn, podjetje)
    for ime, st in slo_sklad.items():
        dodaj_skladisce(conn, ime, st)
    for (kl, teza), slo in sez_podatkov.items():
        dodaj_odpadek(conn, kl, teza, slo)
    conn.commit()


def naredi_bazo_ekol(pobrisi_ce_obstaja = False):
    slo_sklad = {'Sklad-3': 3, 'Sklad-7': 7}
    IME_DATOTEKE_Z_BAZO = '../Ekol.sqlite'
    IME_DATOTEKE_Z_SQL_UKAZI = 'ustvari.sql'
    IME_DATOTEKE_S_PODATKI1 = "ND_00_Seznam klasifikacij po dovoljenjih.xlsx"
    IME_DATOTEKE_S_PODATKI2 = "001_Evidenca_odpadko_v_skladiscu.xlsm"
    # Naredimo prazno bazo
    if os.path.exists(IME_DATOTEKE_Z_BAZO):
        if pobrisi_ce_obstaja:
            os.remove(IME_DATOTEKE_Z_BAZO)
        else:
            print('Baza že obstaja in je ne bom spreminjal.')
            return
    conn = sqlite3.connect(IME_DATOTEKE_Z_BAZO)
    # Ustvarimo tabele iz DDL datoteke
    with open(IME_DATOTEKE_Z_SQL_UKAZI, mode = 'r', encoding = "utf8") as datoteka_z_sql_ukazi:
        sql_ukazi = datoteka_z_sql_ukazi.read()
        conn.executescript(sql_ukazi)
    
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
        if datum and teza != 1:
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
    napolni_tabele(conn, slo_klas_ste_ime, slo_id_podjetje, slo_sklad, sez_podatkov)
    conn.execute('VACUUM')

naredi_bazo_ekol()