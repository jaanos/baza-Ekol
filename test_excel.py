import xlrd
import os
import sys
from openpyxl.workbook import Workbook
from openpyxl.reader.excel import load_workbook, InvalidFileException

IME_DATOTEKE_S_PODATKI_1 = os.path.join(sys.path[0], "ND_00_Seznam klasifikacij po dovoljenjih.xlsx")
IME_DATOTEKE_S_PODATKI_2 = os.path.join(sys.path[0], "001_Evidenca_odpadko_v_skladiscu.xlsm")

print(os.path.exists(IME_DATOTEKE_S_PODATKI_1))
print(os.path.exists(IME_DATOTEKE_S_PODATKI_2))

dat_1 = xlrd.open_workbook(IME_DATOTEKE_S_PODATKI_1)
dat_2 = xlrd.open_workbook(IME_DATOTEKE_S_PODATKI_2)

# print(os.path.exists(r'D:\PB1\baza-Ekol\001_Evidenca_odpadko_v_skladiscu.xlsm'))
# print(os.path.exists(os.path.join(sys.path[0], "001_Evidenca_odpadko_v_skladiscu.xlsm")))

# print(sheet.nrows)
# print(sheet.ncols)