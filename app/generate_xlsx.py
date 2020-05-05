import xlsxwriter

""" from issamWS import  User , db 
all = User.query.all()
presents = [User.query.get(11096530),User.query.get(33333333)]
for s in presents : 
    print(s.username) """

def generateXlsx(fileName,studentList,presentStudents) : 
    # Create an new Excel file and add a worksheet.
    presneceWorkbook = xlsxwriter.Workbook(fileName)
    presenceSheet = presneceWorkbook.add_worksheet()

    presenceSheet.write("A1" , "CIN")
    presenceSheet.write("B1" , "Nom complet")
    presenceSheet.write("C1" , "presence")

    for item in range(len(studentList )): 
        presenceSheet.write(item+1,0,studentList[item].id)
        presenceSheet.write(item+1,1,studentList[item].username)
        if studentList[item].exists(presentStudents) : 
            presenceSheet.write(item+1,2,"+")
        else : 
            presenceSheet.write(item+1,2,"-")

    presneceWorkbook.close()

""" content = ["ankit", "rahul", "priya", "harshita", "sumit", "neeraj", "shivam"] 
partOfContent=["rahul", "priya", "harshita"]"""
#generateXlsx('presents.xlsx',all,presents) 