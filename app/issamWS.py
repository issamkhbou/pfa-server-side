from flask import Flask, flash, request, redirect, url_for, jsonify
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import base64
from json import dumps
from base64 import b64encode
import datetime
import face_recognition

from app.facerec_from_webcam import detect_faces_in_image
from app.generate_xlsx import generateXlsx
from app.send_email_to_teacher import send_mail_with_excel
from app.getAbsenceInSingleCourse import countAbs , getRow

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
#BASE_DIR = os.getcwd()
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER  = os.path.join(BASE_DIR, 'uploads')

UPLOAD_FOLDER_STUDENTS = os.path.join(BASE_DIR,"students")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pfa.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    classe = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    
    def serialize(self):
        return {"id": self.id,
                "username": self.username,
                "classe": self.classe,
                "email": self.email,
                "password": self.password,
                "image_file": self.image_file,} 
    
    def equals (self,otherStudent) : 
        return  self.id == otherStudent.id 

    def exists (self , studentList) : 
        for s in studentList : 
            if self.equals(s) : 
                return True 
        return False 



@app.route("/")
@cross_origin()
def helloWorld():
  return "Hello, world! welcome to our PFA project"


# image uploaded by the teacher 
@cross_origin()
@app.route('/uploadAndDetectionImage', methods=['GET', 'POST'])
def api_save_base64_image():
    data = request.json
    file = data['img']
    course = data['course']
    classe=data['classe']
    id = data['id'] # adding this to the file name 
    starter = file.find(',')
    image_data = file[starter+1:]
    image_data = bytes(image_data, encoding="ascii")
    newFileName = 'test'+str(id)+".jpg"
    with open(os.path.join(UPLOAD_FOLDER , newFileName), 'wb') as fh:
        fh.write(base64.decodebytes(image_data))

    frame = face_recognition.load_image_file(os.path.join(UPLOAD_FOLDER,newFileName))
    studentsNames = detect_faces_in_image(frame)
    print(studentsNames)


    presents=[]
    for studentName in studentsNames :
        """ user = User.query.filter_by(username=studentsName).first() """
        presents.append(User.query.filter_by(username=studentName).first())
    print(presents , type(presents))

    d = datetime.datetime.today()
    #PATH_TO_COURSE_CLASSE = os.path.join(os.getcwd(),'courses',course,classe)
    excelFileName =os.path.join(BASE_DIR,'courses',course,classe,"Liste "+classe+" "+d.strftime('%d-%m-%Y')+".xlsx")    
    #TODO should be replaced by all = User.query.all(class) 
    all = list(User.query.filter_by(classe=classe))
    generateXlsx(excelFileName,all,presents)

    recipient_email="issamkha123@gmail.com"
    #send_mail_with_excel(recipient_email,classe,excelFileName)


    # generating a spreadsheet containing all student-class list with non presents and sending it to an email 
    # non presents : ([allStudents(GI2S1)] - [presenStudents]) 
    # + presents in the list => order by name => saving in the spreadsheet => sending to teacher email  
    # email teacher is mentioned in the json object along side with the test image as well as its id  

    #return jsonify({'students' : presents})
    return jsonify({"students" : list(map(lambda user: user.serialize(), presents  ))}) 



@app.route('/addStudent', methods=['POST', 'GET'])
@cross_origin()
def addStudent():
    req_data = request.json
    id = req_data['id']
    username = req_data['username']
    classe = req_data['classe']
    email = req_data['email']
    password = req_data['password']
    #print(id)

    file = req_data['img']
    starter = file.find(',')
    image_data = file[starter+1:]
    image_data = bytes(image_data, encoding="ascii")
    newFileName = req_data['username'] + ".jpg"
    with open( os.path.join("students",newFileName) , 'wb') as fh:
        fh.write(base64.decodebytes(image_data))

    student = User(id=id , username = username , classe = classe , email = email , password = password , image_file =os.path.join("students",newFileName)   )
    db.session.add(student)
    db.session.commit()
    print (User.query.all())
    return jsonify({
        "msg": "student added"})


#get all students
@cross_origin()
@app.route('/getAllStudents', methods=['POST', 'GET'])
def getAllStudents():
    users = User.query.all()
    output = []
    for user in users : 
        userData = {}
        userData['id'] = user.id
        userData['username'] = user.username
        userData['email'] = user.email
        userData['classe'] = user.classe
        userData['password'] = user.password

        img = os.path.join(UPLOAD_FOLDER_STUDENTS,user.username+".jpg") 

        with open(img, "rb") as img_file:
            userImageConvertedTobase64String = base64.b64encode(img_file.read()).decode("utf-8")
        

        userData['image_file'] = userImageConvertedTobase64String 
        output.append(userData)
    #print ([i['username'] for i in output])
    return jsonify({'users' : output}) 

    #return jsonify({"students" : list(map(lambda user: user.serialize(), User.query.all()))}) 


#get the details of one user :
@cross_origin()
@app.route('/getOneStudent/<int:id>', methods=['GET'])
def getOneStudent(id):
    user = User.query.filter_by(id=id).first()
    if not user : 
        return jsonify({'message'  : 'No user found!'})
    userData = {}
    userData['id'] = user.id
    userData['username'] = user.username
    userData['email'] = user.email
    userData['classe'] = user.classe
    userData['password'] = user.password

    img = os.path.join(UPLOAD_FOLDER_STUDENTS,user.username+".jpg") 

    with open(img, "rb") as img_file:
        userImageConvertedTobase64String = base64.b64encode(img_file.read()).decode("utf-8")

    userData['image_file'] = userImageConvertedTobase64String 
    return jsonify({'user' : userData})


@cross_origin()
@app.route('/student/<int:id>', methods=['DELETE'])
def deleteStudent(id):
    student = User.query.get(id)

    img = os.path.join(UPLOAD_FOLDER_STUDENTS,student.username+".jpg") 

    os.remove(img)
    db.session.delete(student)
    db.session.commit()
    return jsonify({'result': student.username +" deleted successfully"})


#update a student
@cross_origin()
@app.route('/student/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)

    user.id = request.json.get('id', user.id) #2nd is for the default 
    #rename the image if the name is changed
    newName= request.json.get('username') 
    if newName  : 
        user.username = newName
        #s= os.path.normpath(user.image_file).split(os.path.sep)[:-1]
       # newImagePath= os.path.join(*s ,newName+".jpg" )
        newImagePath= os.path.join(UPLOAD_FOLDER_STUDENTS ,newName+".jpg" )
        os.rename(user.image_file, newImagePath)
        user.image_file = newImagePath
        db.session.commit()


    user.classe = request.json.get('classe', user.classe) #2nd is for the default 
    user.email = request.json.get('email', user.email) #2nd is for the default 
    user.password = request.json.get('password', user.password) #2nd is for the default 

    #change the image (remove the old and save the new)
    file = request.json.get('img')
    if file :
        os.remove(user.image_file)
        starter = file.find(',')
        image_data = file[starter+1:]
        image_data = bytes(image_data, encoding="ascii")
        newFileName = user.username + ".jpg"
        with open( os.path.join(UPLOAD_FOLDER_STUDENTS ,newFileName ), 'wb') as fh:
            fh.write(base64.decodebytes(image_data)) 

    db.session.commit()
    return jsonify({'user': user.serialize()})



# parcours des fichiers excel et recherche des abscence pour un étudient
# retourner le resultat 
@cross_origin()
@app.route('/getAbsenceInSingleCourse', methods=['GET'])
def getAbsence():
    req_data = request.json
    #id = req_data['id']
    username = req_data['username']
    classe = req_data['classe']
    course = req_data['course']

    path =  os.path.join(BASE_DIR,"courses",course, classe)
     
    all = list(User.query.filter_by(classe=classe))

    files = os.listdir(path) 
    #getting the student pos in stylesheet(feuille d'appel)
    positionInSheet = getRow(username, os.path.join(path,files[0]) )
    count ,dates = countAbs(username,path,positionInSheet)
    output = {
        "abscenceTimes" : count ,
        "dates" : dates
    }
    return jsonify(output)


