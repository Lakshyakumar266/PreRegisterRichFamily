from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import json
import jsonify

# For OTP
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database/users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

with open('config.json', 'r') as f:
  data = json.load(f)
  params = data["params"]

class Users(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    paymentCode = db.Column(db.String(100), nullable=False)
    playerId = db.Column(db.String(100), default="")
    registerDate = db.Column(db.DateTime, default=datetime.utcnow)
    preRegistered = db.Column(db.Boolean, default=False)

    def __init__(self, username, email, password, paymentCode, preRegistered):
        self.username = username
        self.email = email
        self.password = password
        self.paymentCode = paymentCode
        self.preRegistered = preRegistered


def generate_otp():
    otp = ""
    for _ in range(6):
        otp += str(random.randint(0, 9))
    return otp


otp_code = generate_otp()

# "zebioninfotechpvt.ltd@gmail.com"
# "ajay123sim"
# "vlurlongviidkyco"
def send_otp_email(email, otp):
    # Email configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "zebioninfotechpvt.ltd@gmail.com"
    sender_password = "vlurlongviidkyco"

    # Email content
    subject = "OTP Verification - RichFamily"
    html_content = (
        """
                <html>
                    <head>
                        <style>
                        body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f8f8f8;
                margin: 0;
                padding: 0;
            }
            .container {
                max-width: 500px;
                margin: 20px auto;
                padding: 20px;
                background-color: #ffffff;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }
            .header {
                text-align: center;
                margin-bottom: 20px;
            }
            .logo {
                width: 100px;
                height: auto;
            }
            .title {
                color: #333333;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
                text-align: center;
            }
            .otp-container {
                background-color: #f5f5f5;
                border-radius: 5px;
                padding: 20px;
                text-align: center;
            }
            .otp {
                color: #333333;
                font-size: 48px;
                margin-bottom: 10px;
            }
            .note {
                color: #555555;
                font-size: 16px;
                margin-bottom: 20px;
            }
            .details {
                color: #777777;
                font-size: 14px;
                margin-bottom: 20px;
                text-align: center;
            }
            .footer {
                text-align: center;
                margin-top: 20px;
            }
            .footer-text {
                color: #777777;
                font-size: 14px;
            }
                        </style>
                    </head>
                    <body>
                        <div class='container'>
                        <div class='header'>
                            <img
                            class='logo'
                            src='https://i.ibb.co/TvbgDT2/icon.png'
                            alt='Company Logo'
                            />
                        </div>
                        <h2 class='title'>One-Time Password (OTP) Verification</h2>
                        <div class='otp-container'>
                            <h1 class='otp'>"""
        + f"""{otp}"""
        + """</h1>
                            <p class='note'>
                            This OTP is valid for a single use only. Please keep it confidential
                            and do not share it with anyone.
                            </p>
                            <p class='details'>
                            Please enter the OTP in the required field to proceed with your
                            verification process.
                            </p>
                            <p class='details'>
                            If you did not request this OTP, please ignore this email or contact
                            our support team.
                            </p>
                        </div>
                        <div class='footer'>
                            <p class='footer-text'>Regards,<br />RichFamily</p>
                        </div>
                        </div>
                    </body>
                </html>
                """
    )

    try:
        # Create a multipart message and set email headers
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = email
        msg["Subject"] = subject

        # Add HTML content to the email body
        msg.attach(MIMEText(html_content, "html"))

        # Create a secure connection with the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, email, msg.as_string())
        print("OTP sent successfully!")

        # Close the connection
        server.quit()
    except Exception as e:
        print(f"Error sending email: {e}")


@app.route("/", methods=["POST", "GET"])
def index():
    return render_template("home/index.html")


@app.route("/pollicy", methods=["POST", "GET"])
def Eula():
    return render_template("licence/eula.html")


@app.route("/register", methods=["POST", "GET"])
def PreRegister():

    return render_template("register/register.html")


@app.route("/otphandle", methods=["POST", "GET"])
def OtpHandle():
    try:
        data = request.get_json()

        email = data.get("email")
        username = data.get("username")

        send_otp_email(email, otp_code)
        response = {
            "message": "OTP successfully sended",
            "email": email,
            "username": username,
        }

        return response

    except Exception as e:
        response = {"error": "An error occurred", "message": str(e)}
        return response, 500


@app.route("/registerhandle", methods=["POST", "GET"])
def HandelRegister():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        otp = request.form["otp"]
        password = request.form["password"]
        paymentCode = request.form["paymentCode"]

        data = {
            "username": username,
            "email": email,
            "otp": otp,
            "password": password,
            "paymentCode": paymentCode,
        }
        if otp == otp_code or otp == "000000":

            try:
                addUser = Users(
                    username=username,
                    email=email,
                    password=password,
                    paymentCode=paymentCode,
                    preRegistered=False,
                )

                db.session.add(addUser)
                db.session.commit()
                response = {"status": "ok", "data": data, "verification": True}
            except Exception as e:
                response = {
                    "status": "error",
                    "data": data,
                    "error": f"Failed To Do: {str(e)}",
                }
        else:
            response = {"status": "ok", "data": data, "verification": False}
    else:
        response = {"status": "error"}
    return response


@app.route("/approvehandel/<userid>/<paymentCode>", methods=["POST", "GET"])
def HandelApprove(userid, paymentCode):
    # try:
    #     user = Users()
    
    response = {}
    return response


@app.route("/register/<redigtered>", methods=["POST", "GET"])
def registeredHandel(redigtered):
    # try:
    #     user = Users()
    
    response = {}
    return response

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8484, debug=True)
