import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# โหลดค่าจากไฟล์ .env เข้าสู่ Environment Variables
load_dotenv()

# ดึงค่า API Key จาก Environment Variable
# ตรวจสอบให้แน่ใจว่าชื่อ "SENDGRID_API_KEY" ตรงกับในไฟล์ .env
api_key = os.getenv("SENDGRID_API_KEY")

# (แนะนำ) เพิ่มโค้ดสำหรับตรวจสอบเพื่อช่วยหาข้อผิดพลาดในอนาคต
if not api_key:
    print("Error: SENDGRID_API_KEY is not set in the environment.")
    exit() # ออกจากโปรแกรมถ้าไม่เจอคีย์

# --- ส่วนที่เหลือของโค้ดคุณ ---
# ตัวอย่างโค้ดการส่งอีเมล
message = Mail(
    from_email='thegivergold@gmail.com',
    to_emails='worasetrs@gmail.com',
    subject='Sending with Twilio SendGrid is Fun',
    html_content='<strong>and easy to do anywhere, even with Python</strong>')
try:
    sg = SendGridAPIClient(api_key)
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:

    print(f"Error: {e}")
