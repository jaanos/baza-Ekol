import sqlite3 as dbapi
povezava = dbapi.connect('Ekol.sqlite')
kazalec = povezava.cursor()
import xlrd

pot1 = ("ND_00_Seznam klasifikacij po dovoljenjih.xlsx")
 

dat = xlrd.open_workbook(pot1)
list1 = dat.sheet_by_index(0)

# 13 stolpcev
# 840 vrstic
# For row 0 and column 0

# 2 tabela
# zanimata 2 stolpca
# 840 vrstic
list2 = dat.sheet_by_index(1)
# v tabeli hranimo ukaz za vstavo ene vrsti
klas = list()
slo_klas_ste_ime = dict() # zato, da imam za kasnejše tabele, te ključe nekje shranjene
# zapis v SQL
#for i in range(1, 840): # po vrsticah
#    kl_st = list2.cell_value(i, 0)
#    ime = list2.cell_value(i, 1)
#    slo_klas_ste_ime[kl_st] = ime
#    kazalec.execute('INSERT INTO vrsta_odpadka (klasifikacijska_stevilka, naziv) VALUES (?, ?);', [kl_st, ime])


# bilo izvedeno v SQLlite
pot = (r"001_Evidenca_odpadko_v_skladiscu.xlsm")


dat2 = xlrd.open_workbook(pot)
# da bomo tabelo podjetja napolnit
list3 = dat2.sheet_by_index(4)
# v množico zato da bomo dali samo različna podjetja
# 334 vrstic
slo_id_podjetje = dict() # zato da bo id od podjetja nekje shranjen
mn_pod = set()
st = 0
#for i in range(1, 334):
#    vred = list3.cell_value(i, 1)
#    if vred and vred not in {'x', 'X'}:
#        pod = vred.upper()
#        if pod not in mn_pod:
#            # z velikimi črkami zaradi neusklajenosti pisanja v excellu
#            mn_pod.add(pod)
#            kazalec.execute('INSERT INTO podjetje (ime) VALUES (?);', [pod])
#            slo_id_podjetje[pod] = st + 1
#            st += 1
        


# zaradi tega ker iteriranje po  množici ni enolično smo v slo_id_podjetje shranili primer, ki sovpada id v tabeli podjetja

slo_sklad = {'Sklad-3': 3, 'Sklad-7': 7}

#for kl, vr in slo_sklad.items():
#    kazalec.execute('INSERT INTO skladisce (id, ime) VALUES (?, ?);', [vr, kl])




dat = xlrd.open_workbook(pot)
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

# vpis v tabelo odpadki
for (kl, teza), slo in sez_podatkov.items():
    kazalec.execute( '''
        INSERT INTO odpadek 
        (teza, povzrocitelj, prejemnik, datum_uvoza, opomba_uvoz, datum_izvoza, opomba_izvoz, klasifikacijska_stevilka, skladisce ) 
        VALUES 
        (?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', [teza, sez_podatkov[kl, teza].get('pov', ''), '', sez_podatkov[kl, teza].get('dat_uv', ''), 
        sez_podatkov[kl, teza].get('op_uv', ''), sez_podatkov[kl, teza].get('dat_iz', ''), sez_podatkov[kl, teza].get('op_iz', ''), 
        kl, sez_podatkov[kl, teza].get('skl', '')]  
    ) 
povezava.commit()
kazalec.close()
povezava.close()
