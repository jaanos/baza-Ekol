import xlrd
import json


# zaradi težav z excellom potrebne podatke shraniva v json format

slo_sklad = {'Sklad-3': 3, 'Sklad-7': 7}
IME_DATOTEKE_S_PODATKI1 = "ND_00_Seznam klasifikacij po dovoljenjih.xlsx"
IME_DATOTEKE_S_PODATKI2 = "001_Evidenca_odpadko_v_skladiscu.xlsm"
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
slo_opombe = dict()
sez_podatkov = dict()
stevec_opombe = 1
for i in range(1, 334):
    kl_st = vhod.cell_value(i, 0)
    povzrocitelj = vhod.cell_value(i, 1)
    opomba_uvoz = vhod.cell_value(i, 2)
    teza = vhod.cell_value(i, 3)
    sklad = vhod.cell_value(i, 4)
    datum = vhod.cell_value(i, 5)
    if datum and teza != 1: # teža 1 pomeni napako
        # pomeni ni prazna vrstica
        # spremenimo datum primeren za SQL
        if opomba_uvoz == 'x':
            opomba_uvoz = None
        if opomba_uvoz:
            # če je vsaj kakšen podatek še
            opomba_uvoz = opomba_uvoz.upper()
            if opomba_uvoz not in slo_opombe:
                slo_opombe[opomba_uvoz] = stevec_opombe
                stevec_opombe += 1
        if povzrocitelj.upper() in slo_id_podjetje.keys():
            povzrocitelj = slo_id_podjetje[povzrocitelj.upper()]
        else:
            povzrocitelj = None
        if sklad in slo_sklad.keys():
            sklad = slo_sklad[sklad]
        leto, mesec, dan, h, i, s = xlrd.xldate_as_tuple(datum, dat.datemode)
        sql_datum = str(leto) + '-' + str(mesec) + '-' + str(dan)
        teza = int(teza)
        sez_podatkov[(kl_st, teza)]  = {'povzrocitelj': povzrocitelj, 'opomba_uvoz': slo_opombe.get(opomba_uvoz), 
                                    'skladisce': sklad, 'datum_uvoza': sql_datum}
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
            opomba_izvoz = None
        if opomba_izvoz:
            # če je vsaj kakšen podatek še
            opomba_izvoz = opomba_izvoz.upper()
            if opomba_izvoz not in slo_opombe:
                slo_opombe[opomba_izvoz] = stevec_opombe
                stevec_opombe += 1
        povzrocitelj = povzrocitelj.upper()
        leto1, mesec1, dan1, h, i, s = xlrd.xldate_as_tuple(datum_izv, dat.datemode)
        sql_datum1 = str(leto1) + '-' + str(mesec1) + '-' + str(dan1)
        if (kl_st, teza) in sez_podatkov.keys():
            sez_podatkov[kl_st, teza]['datum_izvoza'] = sql_datum1
            sez_podatkov[kl_st, teza]['opomba_izvoz'] = slo_opombe.get(opomba_izvoz)
slo_opombe['HDPE'] = stevec_opombe
stevec_opombe += 1
slo_opombe['EKO-2'] = stevec_opombe
stevec_opombe += 1
slo_opombe['ZOKI-1'] = stevec_opombe
stevec_opombe += 1
slo_opombe['OSTALO'] = stevec_opombe
skup_slo = {'slo_klas_ste_ime': slo_klas_ste_ime, 
            'slo_id_podjetje': slo_id_podjetje,
            'slo_sklad': slo_sklad,
            'slo_opombe': slo_opombe}
vmesni = dict()
for i, kl in enumerate(sez_podatkov):
    vmesni[str(i)] = list(kl) + list(sez_podatkov[kl].items())
skup_slo['sez_podatkov'] = vmesni
with open("podatki.json", "w") as pisi_podatki:
    json.dump(skup_slo, pisi_podatki)




    