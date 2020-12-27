import xlrd
import os
import sys
#from openpyxl.workbook import Workbook
#from openpyxl.reader.excel import load_workbook, InvalidFileException

IME_DATOTEKE_S_PODATKI_1 = os.path.join(sys.path[0], "ND_00_Seznam klasifikacij po dovoljenjih.xlsx")
IME_DATOTEKE_S_PODATKI_2 = os.path.join(sys.path[0], "001_Evidenca_odpadko_v_skladiscu.xlsm")

print(os.path.exists(IME_DATOTEKE_S_PODATKI_1))
print(os.path.exists(IME_DATOTEKE_S_PODATKI_2))

dat_1 = xlrd.open_workbook(IME_DATOTEKE_S_PODATKI_1)
dat_2 = xlrd.open_workbook(IME_DATOTEKE_S_PODATKI_2)

list1 = dat_1.sheet_by_index(4)
list2 = dat_2.sheet_by_index(1)
print(list1.cell_value(1, 0))
print(list1.cell_value(1, 1))
print(list2.cell_value(1, 0))
print(list2.cell_value(1, 1))

# print(os.path.exists(r'D:\PB1\baza-Ekol\001_Evidenca_odpadko_v_skladiscu.xlsm'))
# print(os.path.exists(os.path.join(sys.path[0], "001_Evidenca_odpadko_v_skladiscu.xlsm")))

# print(list1.ncols)
print(dat_1.sheet_by_index(1).nrows)
print(dat_1.sheet_by_index(4).nrows)
print(dat_2.sheet_by_index(4).nrows)
print(dat_2.sheet_by_index(5).nrows)