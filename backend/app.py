# ==== imports ด้านบน ====
import os
import logging
from flask import Flask, jsonify, request, url_for, redirect
from flask_cors import CORS

# ถ้ามีการใช้ SendGrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

# โหลด .env (สำหรับรันท้องถิ่น; บน Render ใช้ Dashboard ตั้งค่า ENV)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

app = Flask(__name__)
CORS(app, origins=[os.getenv("FRONTEND_URL") or "*"], supports_credentials=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== ค่า ENV ที่ต้องใช้ =====
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")             # ใส่ใน Render > Environment
SENDER_EMAIL     = os.getenv("SENDER_EMAIL")                  # เช่น no-reply@yourdomain.com
SENDER_NAME      = os.getenv("SENDER_NAME", "Gold Bot Giver")

# ลิงก์ Stripe ที่ฝั่ง template ต้องใช้
STRIPE_LINK_2900 = os.getenv("STRIPE_LINK_2900", "")
STRIPE_LINK_4900 = os.getenv("STRIPE_LINK_4900", "")

# (ถ้ายังมี route ตัวอย่างที่ต้นไฟล์ เปลี่ยน path แล้วนะ)
# @app.post("/submit-quiz-placeholder")
# def submit_quiz_placeholder():
#     ...

@app.post("/submit-quiz-placeholder")
def submit_quiz_placeholder():
    data = request.get_json(silent=True)
    if not data:
        return jsonify(error="Invalid or missing JSON body"), 400

    name = data.get("name")
    email = data.get("email")
    answers = data.get("answers")

    if not isinstance(name, str) or not isinstance(email, str) or not isinstance(answers, list):
        return jsonify(error="Missing or invalid fields: name/email/answers"), 400

    # TODO: ใส่ logic ของคุณ (ตรวจคำตอบ/บันทึก/ส่งอีเมล)
    return jsonify(ok=True, message="Quiz submitted successfully"), 200

# =================================================================
# ===== 2. ฟังก์ชันสำหรับส่งอีเมล =====
# =================================================================

def send_results_email(recipient_email: str, style_name: str, customer_name: str = "ลูกค้า") -> None:
    """
    ส่งอีเมลผลการวิเคราะห์สไตล์การลงทุน พร้อมแนบไฟล์รายงาน 4 period
    """
    if not SENDGRID_API_KEY or not SENDER_EMAIL:
        print("Error: SendGrid API Key or Sender Email is not configured.")
        return

    # สร้าง Link ไปยังหน้ารายงานผล
    # ต้องทำภายใน request context เพื่อให้ url_for ทำงานได้
    with app.app_context():
        fast_profit_url = url_for('result_fast_profit', _external=True)
        stable_growth_url = url_for('result_stable_growth', _external=True)

    subject = ""
    html_content = ""
    attachment_paths = [] 
    sender_name = SENDER_NAME

    if style_name == 'fast':
        subject = f"[ผลวิเคราะห์] สไตล์การลงทุน AI ของคุณคือ 'สายทำกำไรเร็ว (Fast Profit)'"
        
        # (เนื้อหา html_content เหมือนเดิม)
        html_content = f"""
        <p>สวัสดีครับคุณ {customer_name},</p>
        <p>เราได้ทำการวิเคราะห์โปรไฟล์การลงทุนของคุณจากแบบทดสอบเรียบร้อยแล้ว และผลลัพธ์พร้อมให้คุณดูบนหน้าเว็บส่วนตัวของคุณครับ</p>
        <p>สไตล์ของคุณคือ <strong>"สาย 'ทำกำไรเร็ว' (Fast Profit)"</strong></p>
        <p>ซึ่งหมายความว่าคุณมีแนวโน้มที่จะเป็นผู้ที่หัวใจแข็งแกร่งและต้องการเห็นพอร์ตการลงทุนเติบโตอย่างรวดเร็วในเวลาอันสั้นที่สุด</p>
        <p>จากสไตล์ของคุณ นี่คือ Bot 2 ตัวที่ถูกสร้างมาเพื่อตอบโจทย์การทำกำไรอย่างบ้าคลั่งโดยเฉพาะ:</p>
        <ol>
            <li><strong>BOT NAME: The Singularity (จักรกลเร่งความมั่งคั่ง)</strong><br>
                เครื่องจักรเร่งความมั่งคั่งที่ถูกออกแบบมาเพื่อสร้างกำไรอย่างบ้าคลั่ง
                <ul>
                    <li>ผลกำไรสะสมตลอดปี: $65,211.19</li>
                    <li>อัตราเติบโตเฉลี่ย (ต่อไตรมาส): 163.03%</li>
                    <li>Profit Factor: 4.04x (ทุก 1 บาทที่เสียไป จะทวงคืนกลับมา 4.04 บาท)</li>
                </ul>
            </li>
            <br>
            <li><strong>BOT NAME: The Scalpel (คมมีดผ่าตัดกำไร)</strong><br>
                เข้าเทรดด้วยความเร็วและความแม่นยำดุจมีดหมอ เฉือนเอากำไรก้อนโตจากตลาดโดยไม่ต้องรอ
                <ul>
                    <li>ผลกำไรสะสมตลอดปี: $22,186.11</li>
                    <li>อัตราเติบโตเฉลี่ย (ต่อไตรมาส): 55.47%</li>
                    <li>Sharpe Ratio: 2.92 (การันตีการทำกำไรที่คุ้มค่าทุกความเสี่ยง)</li>
                </ul>
            </li>
        </ol>
        <p>ตอนนี้...ไปดูรายงานฉบับเต็ม (พร้อมกราฟและข้อมูลเชิงลึกอื่นๆ) เพื่อดูว่า Bot เทรดตัวไหนที่ "สร้างมาเพื่อคุณ" โดยเฉพาะ</p>
        <a href="{result-fast-profit.html}" style="background-color: #007bff; color: white; padding: 12px 25px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; font-weight: bold;">
            &gt;&gt; คลิกที่นี่เพื่อดูผลวิเคราะห์ฉบับเต็มและ Bot ที่แนะนำสำหรับคุณ &lt;&lt;
        </a>
        <p>ในหน้านั้น ผมได้เตรียมข้อมูลเชิงลึกและข้อเสนอพิเศษสำหรับก้าวต่อไปในการเดินทางสู่การเป็น "ผู้สร้าง" ของคุณไว้ด้วยครับ</p>
        <p>ขอให้สนุกกับการค้นพบนะครับ</p>
        <p>ขอให้ลงทุนอย่างมีระบบ,<br>{sender_name}</p>
        """
    else:  # 'stable'
        subject = f"[ผลวิเคราะห์] สไตล์การลงทุน AI ของคุณคือ 'สายเติบโตมั่นคง (Stable Growth)'"

        
        # (เนื้อหา html_content เหมือนเดิม)
        html_content = f"""
        <p>สวัสดีครับคุณ {customer_name},</p>
        <p>เราได้ทำการวิเคราะห์โปรไฟล์การลงทุนของคุณจากแบบทดสอบเรียบร้อยแล้ว และผลลัพธ์พร้อมให้คุณดูบนหน้าเว็บส่วนตัวของคุณครับ</p>
        <p>สไตล์ของคุณคือ <strong>"สาย 'เติบโตมั่นคง' (Stable Growth)"</strong></p>
        <p>ซึ่งหมายความว่าคุณมีแนวโน้มที่จะเป็นนักลงทุนผู้ชาญฉลาดที่ต้องการสร้างความมั่งคั่งอย่างยั่งยืน ปลอดภัย และมีประสิทธิภาพสูงสุด</p>
        <p>จากสไตล์ของคุณ นี่คือ Bot 2 ตัวที่มอบทั้งความมั่งคั่งและความมั่นคงในหนึ่งเดียว:</p>
        <ol>
            <li><strong>BOT NAME: The Oracle (มหาเทพพยากรณ์แห่งความมั่นคง)</strong><br>
                ถูกสร้างมาเพื่อปกป้องเงินทุนและสั่งสมความมั่งคั่งให้คุณอย่างสบายใจที่สุด
                <ul>
                    <li>ระดับการขาดทุนสูงสุด (Max. Drawdown): 3.34%</li>
                    <li>Sharpe Ratio: 2.74 (การลงทุนที่ชาญฉลาดในทุกการตัดสินใจ)</li>
                    <li>ผลกำไรรวมตลอดปี: $3,537.41 (เฉลี่ย 8.84% ต่อไตรมาส)</li>
                </ul>
            </li>
            <br>
            <li><strong>BOT NAME: The Apex (ที่สุดแห่งการเติบโตที่สมบูรณ์แบบ)</strong><br>
                ผสานการเติบโตที่ทรงพลังเข้ากับการป้องกันความเสี่ยงที่แข็งแกร่งที่สุด
                <ul>
                    <li>Sharpe Ratio: 3.62 (ครองตำแหน่ง Bot ที่ฉลาดที่สุด)</li>
                    <li>ระดับการขาดทุนสูงสุด (Max. Drawdown): 4.93%</li>
                    <li>ผลกำไรรวมตลอดปี: $14,009.15 (เฉลี่ย 35.02% ต่อไตรมาส)</li>
                </ul>
            </li>
        </ol>
        <p>ตอนนี้...ไปดูรายงานฉบับเต็ม (พร้อมกราฟและข้อมูลเชิงลึกอื่นๆ) เพื่อดูว่า Bot เทรดตัวไหนที่ "สร้างมาเพื่อคุณ" โดยเฉพาะ</p>
        <a href={result-stable-growthl.html} style="background-color: #28a745; color: white; padding: 12px 25px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px; font-weight: bold;">
            &gt;&gt; คลิกที่นี่เพื่อดูผลวิเคราะห์ฉบับเต็มและ Bot ที่แนะนำสำหรับคุณ &lt;&lt;
        </a>
        <p>ในหน้านั้น ผมได้เตรียมข้อมูลเชิงลึกและข้อเสนอพิเศษสำหรับก้าวต่อไปในการเดินทางสู่การเป็น "ผู้สร้าง" ของคุณไว้ด้วยครับ</p>
        <p>ขอให้สนุกกับการค้นพบนะครับ</p>
        <p>ขอให้ลงทุนอย่างมีระบบ,<br>{sender_name}</p>
        """

    message = Mail(
        from_email=(SENDER_EMAIL, SENDER_NAME),
        to_emails=recipient_email,
        subject=subject,
        html_content=html_content
    )

    attachments_list = []
    for path in attachment_paths:
        try:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    data = f.read()
                encoded_file = base64.b64encode(data).decode()
                attachedFile = Attachment(
                    FileContent(encoded_file),
                    FileName(os.path.basename(path)),
                    FileType('application/pdf'),
                    Disposition('attachment')
                )
                attachments_list.append(attachedFile)
            else:
                print(f"Warning: Attachment file not found at {path}")
        except Exception as e:
            print(f"An error occurred while attaching file {path}: {e}")
    
    if attachments_list:
        message.attachment = attachments_list

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        print(f"Results email sent to {recipient_email}")
    except Exception as e:
        print(f"Error sending email: {e}")

def send_welcome_email(customer_email: str, purchase_type: str) -> None:
    """
    ฟังก์ชันใหม่สำหรับส่งอีเมลต้อนรับหลังชำระเงิน
    """
    if not SENDGRID_API_KEY or not SENDER_EMAIL:
        print("Error: SendGrid API Key or Sender Email is not configured.")
        return

    subject = ""
    html_content = ""
    sender_name = SENDER_NAME

    if purchase_type == 'fast-track':
        subject = "ยินดีต้อนรับสู่ The Fast-Track Kit!"
        html_content = f"""
        <p>สวัสดีครับ,</p>
        <p>ขอบคุณที่ตัดสินใจเข้าร่วม The Fast-Track Kit ครับ! เราตื่นเต้นที่จะได้ร่วมเดินทางไปกับคุณ</p>
        <p>ในไม่ช้าคุณจะได้รับข้อมูลและสิทธิ์ในการเข้าถึงเครื่องมือทั้งหมด โปรดตรวจสอบอีเมลของคุณในอีกไม่กี่ชั่วโมงข้างหน้า</p>
        <p>ขอให้ลงทุนอย่างมีระบบ,<br>{sender_name}</p>
        """
    else: # 'standard' or 'normal'
        subject = "ขอบคุณสำหรับการสั่งซื้อ! เริ่มต้นเส้นทางการลงทุนของคุณได้เลย"
        html_content = f"""
        <p>สวัสดีครับ,</p>
        <p>ขอบคุณสำหรับการสั่งซื้อ Bot ของเราครับ! เราได้แนบลิงก์สำหรับดาวน์โหลดและคู่มือการติดตั้งมาให้ในอีเมลฉบับถัดไปแล้ว</p>
        <p>ขอให้สนุกกับการสร้างความมั่งคั่งนะครับ</p>
        <p>ขอให้ลงทุนอย่างมีระบบ,<br>{sender_name}</p>
        """
    
    message = Mail(
        from_email=(SENDER_EMAIL, SENDER_NAME),
        to_emails=customer_email,
        subject=subject,
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        print(f"Welcome email sent to {customer_email}")
    except Exception as e:
        print(f"Error sending welcome email: {e}")

# =================================================================
# ===== 3. Flask Routes (ส่วนจัดการหน้าเว็บ) =====
# =================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result-fast-profit')
def result_fast_profit():
    return render_template('result-fast-profit.html', stripe_link_4900=STRIPE_LINK_4900)

@app.route('/result-stable-growth')
def result_stable_growth():
    return render_template('result-stable-growth.html', stripe_link_4900=STRIPE_LINK_4900)

@app.route('/the-fast-track-kit')
def the_fast_track_kit():
    return render_template('The-Fast-Track-Kit.html', stripe_link_2900=STRIPE_LINK_2900, stripe_link_4900=STRIPE_LINK_4900)

@app.route('/thank-you-fast-track')
def thank_you_fast_track():
    return render_template('Thank You - Fast Track.html')

@app.route('/thank-you-standard')
def thank_you_standard():
    return render_template('Thank You - Standard.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    """
    Endpoint to process quiz submissions.
    """
    data = request.get_json(force=True)
    email = data.get('email')
    answers = data.get('answers', [])

    aggressive_keys = {'1B', '2A', '3A'}
    aggressive_count = 0
    for idx, choice in enumerate(answers):
        key = f"{idx+1}{choice}"
        if key in aggressive_keys:
            aggressive_count += 1
    style = 'fast' if aggressive_count >= 2 else 'stable'

    if email:
        try:
            send_results_email(email, style, customer_name=email.split('@')[0])
        except Exception as e:
            print(f"Error calling send_results_email from submit_quiz: {e}")

    redirect_url = url_for('result_fast_profit') if style == 'fast' else url_for('result_stable_growth')
    return jsonify({'redirect_url': redirect_url})

@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """
    Endpoint สำหรับรับ Webhook จาก Stripe
    """
    data = request.get_json(force=True)
    
    # สำหรับการใช้งานจริง ควรมีการตรวจสอบ event type และลายเซ็น (signature) จาก Stripe
    # event = stripe.Webhook.construct_event(payload=request.data, sig_header=request.headers.get('stripe-signature'), secret=YOUR_WEBHOOK_SECRET)
    
    customer_email = data.get('customer_email')
    purchase_type = data.get('purchase_type') # 'standard' or 'fast-track'

    if not customer_email or not purchase_type:
        return jsonify({'error': 'Missing customer_email or purchase_type'}), 400

    try:
        send_welcome_email(customer_email, purchase_type)
        return jsonify({'status': 'success', 'message': 'Welcome email sent.'}), 200
    except Exception as e:
        print(f"Error calling send_welcome_email from webhook: {e}")
        return jsonify({'error': str(e)}), 500

# =================================================================
# ===== 4. ส่วนสำหรับรันแอปพลิเคชัน =====
# =================================================================

if __name__ == '__main__':
    app.run(debug=True)
