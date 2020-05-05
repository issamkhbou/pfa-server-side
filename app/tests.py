import base64
import os

#for decoding
base64_img = 'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsTAAA' \
            'LEwEAmpwYAAAB1klEQVQ4jY2TTUhUURTHf+fy/HrjhNEX2KRGiyIXg8xgSURuokX' \
            'LxFW0qDTaSQupkHirthK0qF0WQQQR0UCbwCQyw8KCiDbShEYLJQdmpsk3895p4aS' \
            'v92ass7pcfv/zP+fcc4U6kXKe2pTY3tjSUHjtnFgB0VqchC/SY8/293S23f+6VEj' \
            '9KKwCoPDNIJdmr598GOZNJKNWTic7tqb27WwNuuwGvVWrAit84fsmMzE1P1+1TiK' \
            'MVKvYUjdBvzPZXCwXzyhyWNBgVYkgrIow09VJMznpyebWE+Tdn9cEroBSc1JVPS+' \
            '6moh5Xyjj65vEgBxafGzWetTh+rr1eE/c/TMYg8hlAOvI6JP4KmwLgJ4qD0TIbli' \
            'TB+sunjkbeLekKsZ6Zc8V027aBRoBRHVoduDiSypmGFG7CrcBEyDHA0ZNfNphC0D' \
            '6amYa6ANw3YbWD4Pn3oIc+EdL36V3od0A+MaMAXmA8x2Zyn+IQeQeBDfRcUw3B+2' \
            'PxwZ/EdtTDpCPQLMh9TKx0k3pXipEVlknsf5KoNzGyOe1sz8nvYtTQT6yyvTjIax' \
            'smHGB9pFx4n3jIEfDePQvCIrnn0J4B/gA5J4XcRfu4JZuRAw3C51OtOjM3l2bMb8' \
            'Br5eXCsT/w/EAAAAASUVORK5CYII='

""" 
base64_img_bytes = base64_img.encode('utf-8')
with open('decoded_image.png', 'wb') as file_to_save:
    decoded_image_data = base64.decodebytes(base64_img_bytes)
    file_to_save.write(decoded_image_data) """


#for encoding 
""" with open("issamKhbou.jpg", "rb") as img_file:
    my_string = base64.b64encode(img_file.read())
    #print(my_string.decode('utf-8'))
    #print(base64.decodebytes(my_string))


jpgtxt = base64.encodestring(open("issamKhbou.jpg","rb").read())

f = open("issamkhbou.txt", "w")
f.write(jpgtxt)
f.close() """


""" newjpgtxt = open("jpg1_b64.txt","rb").read()

g = open("out.jpg", "w")
g.write(base64.decodestring(newjpgtxt))
g.close() """

s = "D:\\2019\\python\\face_recognition-master\\face_recognition-master\\examples\\samiBHH.jpg"
#print((os.path.normpath(p).split(os.path.sep)[:-1]))
s= os.path.normpath(s).split(os.path.sep)[:-1]
newImagePath= os.path.join(*s ,"newName"+".jpg" )
#print(newImagePath)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.getcwd()
print(APP_ROOT)
print(BASE_DIR)


