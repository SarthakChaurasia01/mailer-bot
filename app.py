import streamlit as st
import smtplib
from email.message import EmailMessage

st.set_page_config(page_title="Resume Mailer Bot", page_icon="📧")

st.title("📧 Automated Resume Mailer")
st.write("Easily send your resume to multiple recruiters at once.")

# Define Sender Credentials (will be securely stored in deployment)
SENDER_EMAIL = st.secrets["SENDER_EMAIL"]
APP_PASSWORD = st.secrets["APP_PASSWORD"]

with st.form("email_form"):
    # Target Emails
    st.subheader("Recipients")
    recipients_input = st.text_area("Enter Email IDs (comma-separated)", placeholder="hr@company.com, recruiter@tech.com")
    
    # Email Content
    st.subheader("Email Content")
    subject = st.text_input("Subject", "Application for Software Engineering Role")
    body = st.text_area("Email Body", "Hello,\n\nPlease find my resume attached.\n\nBest regards,\n[Your Name]")
    
    # File Attachment
    st.subheader("Attachment")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    
    # Submit Button
    submitted = st.form_submit_button("Send Emails 🚀")

if submitted:
    if not recipients_input or not uploaded_file:
        st.error("Please provide recipient emails and attach a resume.")
    else:
        # Process emails
        recipients_list = [email.strip() for email in recipients_input.split(",") if email.strip()]
        
        try:
            # Setup SMTP Server
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(SENDER_EMAIL, APP_PASSWORD)
                
                progress_bar = st.progress(0)
                total = len(recipients_list)
                
                for index, recipient in enumerate(recipients_list):
                    # Create Message
                    msg = EmailMessage()
                    msg['Subject'] = subject
                    msg['From'] = SENDER_EMAIL
                    msg['To'] = recipient
                    msg.set_content(body)
                    
                    # Attach File
                    file_data = uploaded_file.getvalue()
                    file_name = uploaded_file.name
                    msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)
                    
                    # Send Email
                    smtp.send_message(msg)
                    
                    # Update Progress
                    progress_bar.progress((index + 1) / total)
                
            st.success(f"Successfully sent {total} emails!")
            st.balloons()
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
