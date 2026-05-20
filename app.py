import streamlit as st
import yagmail
import os

st.set_page_config(page_title="Resume Broadcaster Bot", page_icon="✉️", layout="centered")
st.title("✉️ Resume Broadcaster Dashboard")
st.write("Edit your content, add email IDs, and send your resume in bulk securely.")

# 1. Secure Credentials Handling
# It will look for these in your hosted platform's secret manager first
GMAIL_USER = st.secrets.get("GMAIL_USER", "")
GMAIL_PASSWORD = st.secrets.get("GMAIL_PASSWORD", "")

# Fallback text inputs if secrets aren't configured yet
if not GMAIL_USER or not GMAIL_PASSWORD:
    st.warning("⚠️ SMTP Credentials not found in Cloud Secrets. Provide them below temporarily:")
    GMAIL_USER = st.text_input("Your Gmail Address")
    GMAIL_PASSWORD = st.text_input("Your Gmail App Password", type="password")

# 2. Email Customization Area
st.subheader("1. Compose Your Email")
email_subject = st.text_input("Email Subject", value="Application for Software Engineering Role")
email_body = st.text_area("Email Body", value="Dear Hiring Manager,\n\nPlease find my resume attached for your consideration.\n\nBest regards,", height=180)

# 3. Dynamic Resume Upload
st.subheader("2. Attach Resume")
uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])

# 4. Recipient Management Area
st.subheader("3. Recipient Email List")
recipients_input = st.text_area("Paste recipient emails (separate them with a comma or put each on a new line)", placeholder="hr@company.com\nrecruiter@firm.com")

# Processing email string into a clean list
recipients = []
if recipients_input:
    recipients = [email.strip() for email in recipients_input.replace("\n", ",").split(",") if email.strip()]
    st.info(f"📋 Detected {len(recipients)} unique recipient email addresses.")

# 5. Execution Trigger
st.subheader("4. Broadcast")
if st.button("🚀 Start Sending Emails", type="primary"):
    if not GMAIL_USER or not GMAIL_PASSWORD:
        st.error("Missing Gmail credentials. Please fill them out.")
    elif not uploaded_file:
        st.error("Please upload a resume PDF file first.")
    elif not recipients:
        st.error("Your recipient list is empty. Please add at least one email.")
    else:
        try:
            # Temporarily save the uploaded file to disk so yagmail can read its path
            temp_path = uploaded_file.name
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.write("🔄 Establishing secure connection to Gmail...")
            yag = yagmail.SMTP(GMAIL_USER, GMAIL_PASSWORD)
            
            success_count = 0
            progress_bar = st.progress(0)
            
            # Loop through individual recipients
            for index, email in enumerate(recipients):
                try:
                    yag.send(
                        to=email,
                        subject=email_subject,
                        contents=[email_body, temp_path]
                    )
                    st.success(f"✅ Sent to: {email}")
                    success_count += 1
                except Exception as send_err:
                    st.error(f"❌ Failed for {email}: {send_err}")
                
                # Update visual progress indicator
                progress_bar.progress((index + 1) / len(recipients))
            
            st.balloons()
            st.success(f"🎉 Process completed! Successfully broadcasted {success_count}/{len(recipients)} emails.")
            
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        except Exception as conn_err:
            st.error(f"Failed to authenticate connection: {conn_err}")
