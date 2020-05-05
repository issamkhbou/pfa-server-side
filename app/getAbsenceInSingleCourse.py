# Program to extract a particular row value
import xlrd
import os

#loc = os.getcwd()+ '\\'+'Liste GI2S1 28-04-2020.xlsx'

def getRow (studentName , loc ) :
    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(0)
    for r in range(1, sheet.nrows):
        if sheet.row_values(r)[1] == (studentName): 
            return r 

def countAbs(studentName ,loc, positionInSheet) : 
    count = 0 
    files = [ f for f in os.listdir(loc) if f.endswith("xlsx")]
    dates = []
    for f in files : 
        wb = xlrd.open_workbook(os.path.join (loc,f))
        sheet = wb.sheet_by_index(0)
        if sheet.cell_value(positionInSheet, 2) == "-"  : 
            count+=1 
            dates.append(f.split()[2][:-5])
    return count, dates;

#print(getRow("rafikBougheriw",loc))
#countAbs("rafikBougheriw",loc,3) 


