from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = FastAPI()

class EmailSchema(BaseModel):
    email: EmailStr
    subject: str
    message: str

class EmailCallBack(EmailSchema):
    url_callback: str


def send_email_background(subject: str, email: str, message: str, url_callback: str = ''):
    try:
        sender_email =  "haidangkhtn@gmail.com"
        receiver_email = email
        password =os.getenv("MAIL_PASSWORD", "lnireuwgpxbeauht")

        # Create a multipart message and set headers
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject

        # Add body to email
        msg.attach(MIMEText(f"{message} <br/><a href=\"{url_callback}\">Link</a>", "html"))

        # Log in to server using secure context and send email
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Error sending email: {e}")


@app.post("/send-email/")
async def send_email(email: EmailCallBack, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email_background, email.subject, email.email, email.message, email.url_callback)
    return {"message": "Email has been sent"}

@app.post("/process-json/")
async def process_json(json_data: dict, background_tasks: BackgroundTasks):
    try:
        submission = json_data['mautic.form_on_submit'][0]['submission']['results']
        email_address = submission['nhap_thong_tin_email']
        phone_number = submission['nhap_thong_tin_sdt']
        job_position = submission['vui_long_nhap_chuc_vu_cua']

        subject = "Thông tin liên hệ"
        message = f"""
        <html>
        <body>
            <h2>Thông tin liên hệ</h2>
            <p><b>Chức vụ:</b> {job_position}</p>
            <p><b>Email:</b> {email_address}</p>
            <p><b>Số điện thoại:</b> {phone_number}</p>
        </body>
        </html>
        """

        background_tasks.add_task(send_email_background, subject, email_address, message)
        return {"message": "Email has been sent"}
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing key: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
