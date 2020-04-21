
import smtplib
from email.message import EmailMessage

SENDER_EMAIL = "issamkha123@gmail.com"
EMAIL_PASSWORD = "danger123456789"


def send_mail_with_excel(recipient_email,classe, excel_file):
    subject =  "Liste de présence de "+classe 
    content = "Bonjour ,\nvous trouvez ci joint la liste de présence des étudients  pour votre cours \nCordialement. "

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email #recipient_email==SENDER_EMAIL for testing
    msg.set_content(content)

    with open(excel_file, 'rb') as f:
        file_data = f.read()
    msg.add_attachment(file_data, maintype="application", subtype="xlsx", filename=excel_file)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SENDER_EMAIL, EMAIL_PASSWORD)
        smtp.send_message(msg)

#first arg should be added from the json object 
# last arg should be obtained when generating the excel file : it is presence.xlsx for tests purposes 
#send_mail_with_excel(SENDER_EMAIL,subject,content,'presence.xlsx')

