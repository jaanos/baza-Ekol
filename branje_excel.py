import sqlite3 as dbapi
povezava = dbapi.connect('Ekol.sqlite')
kazalec = povezava.cursor()
import xlrd

pot1 = (r"c:\Matej\GutHub\baza-Ekol\ND_00_Seznam klasifikacij po dovoljenjih.xlsx")
 

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
#    kazalec.execute('INSERT INTO vrsta_odpadka (klasifikacijska_stevilka, naziv) VALUES ("{0}", "{1}");'.format(kl_st, ime))


# bilo izvedeno v SQLlite
pot2 = (r"c:\Matej\GutHub\baza-Ekol\001_Evidenca_odpadko_v_skladiscu.xlsm")


dat2 = xlrd.open_workbook(pot2)
# da bomo tabelo podjetja napolnit
list3 = dat2.sheet_by_index(4)
# v množico zato da bomo dali samo različna podjetja
pod = set()
slo_vmesni = dict()
# 334 vrstic
slo_id_podjetje = dict() # zato da bo id od podjetja nekje shranjen
for i in range(1, 334):
    vred = list3.cell_value(i, 1)
    if vred and vred not in {'x', 'X'}:
        # z velikimi črkami zaradi neusklajenosti pisanja v excellu
        pod.add('INSERT INTO podjetje (ime) VALUES ("{0}");'.format(vred.upper()))
        slo_vmesni['INSERT INTO podjetje (ime) VALUES ("{0}");'.format(vred.upper())] = vred.upper()
# zapisv SQL
#for id, elt in enumerate(pod):
#    slo_id_podjetje[slo_vmesni[elt]] = id + 1
#    kazalec.execute(elt)
#print(slo_id_podjetje)
# zaradi tega ker iteriranje po  množici ni enolično smo v slo_id_podjetje shranili primer, ki sovpada id v tabeli podjetja
slo_id_podjetje = {'POCLAIN': 1, 'PIPISTERL': 2, 'SREČO': 3, 'DIHTA': 4, 'GEBRUDER WEIS': 5, 'KONICA': 6, 'INTECTIV': 7, 
                    'EKOL': 8, 'AKRAPOVIČ': 9, 'JENKO ZORAN': 10, 'PREIS SEVNICA': 11, 'KOVINC': 12, 'BOSCH': 13, 'LINGVA': 14, 
                    'HELLA': 15, 'TURBOINSTANT': 16, 'LIVAR': 17, 'AUTOCOMMERCE': 18, 'ELAN': 19, 'KNAUF': 20, 'REM': 21, 
                    'SNAGA LJUBLJANA': 22, 'XENON FORTE': 23, 'YUSKAWA': 24, 'EGP': 25, 'ISKRA GALVANIKA': 26, 'ADRIA MOBIL': 27, 
                    'ELGOLINE': 28, 'EKOINŽINIRING': 29, 'LIDL': 30, 'LAKOLIT': 31, 'ISKRA ISD': 32}

slo_sklad = {'Sklad-3': 3, 'Sklad-7': 7}

pot = (r"c:\Matej\GutHub\baza-Ekol\001_Evidenca_odpadko_v_skladiscu.xlsm")


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
            povzrocitelj = povzrocitelj.upper()
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
            sez_podatkov[kl_st, teza]['dat_iz'] = datum_izv
            sez_podatkov[kl_st, teza]['op_iz'] = opomba_izvoz

# vpis v tabelo odpadki
#for (kl, teza), slo in sez_podatkov.items():
#    sql = '''
#        INSERT INTO odpadek 
#        (teza, povzrocitelj, prejemnik, datum_uvoza, opomba_uvoz, datum_izvoza, opomba_izvoz, klasifikacijska_stevilka, skladisce ) 
#        VALUES 
#        ("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}", "{8}");
#        '''.format(teza, sez_podatkov[kl, teza].get('pov', ''), '', sez_podatkov[kl, teza].get('dat_uv', ''), 
#        sez_podatkov[kl, teza].get('op_uv', ''), sez_podatkov[kl, teza].get('dat_iz', ''), sez_podatkov[kl, teza].get('op_iz', ''), 
#        kl, sez_podatkov[kl, teza].get('skl', ''))  
#    kazalec.execute(sql) 
povezava.commit()
kazalec.close()
povezava.close()
