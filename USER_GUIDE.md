# 📖 User Guide: Healthcare AI Assistant

**Welcome!** This guide will help you use the Healthcare AI Assistant effectively.

---

## 🚀 Quick Start

### Option 1: Simple UI (Recommended)

```bash
streamlit run streamlit_app/app_v2.py
```

**Best for**: First-time users, demos, quick access

### Option 2: Full UI (same as Option 1)

```bash
streamlit run streamlit_app/app_healthcare.py --server.port 8501
```

**Best for**: Power users, technical demos, full features

---

## 🏠 Home Page

When you first open the app, you'll see:

### Quick Actions
- **💬 Start Chat** - Ask health questions
- **📄 Upload Now** - Analyze medical reports
- **📊 View History** - See past conversations

**Just click any button to get started!**

---

## 💬 Chat Page

### How to Use

1. **Type your question** in the text box
2. **Click "Send Question"**
3. **Wait 3-5 seconds** for the response
4. **Read the answer** with sources

### Example Questions

**Symptoms**:
- "What are the symptoms of diabetes?"
- "I have a headache and fever, what could it be?"

**Medications**:
- "What is metformin used for?"
- "What are the side effects of ibuprofen?"

**General Health**:
- "How can I lower my blood pressure naturally?"
- "What foods are good for heart health?"

### Features

- **Smart Routing**: System automatically detects what type of question you're asking
- **Multi-Step Reasoning**: Complex questions get 5-step analysis
- **Sources**: See where the information comes from
- **Emergency Detection**: Urgent symptoms trigger immediate warnings

---

## 📄 Upload Report Page

### How to Upload

1. **Click "Choose a file"**
2. **Select your report** (PDF, JPG, or PNG)
3. **Click "Analyze Report"**
4. **Wait 30-60 seconds** for analysis

### What You'll See

- **Patient Information**: Name, age, gender
- **Lab Results**: All values with normal/abnormal flags
- **Health Recommendations**: Personalized advice based on results
- **Abnormal Values**: Highlighted in red/yellow

### Supported Files

- ✅ PDF lab reports
- ✅ Photos of lab reports (JPG, PNG)
- ✅ Scanned medical documents
- ✅ Max file size: 10MB

---

## 📊 My History Page

### What You'll See

- **Total Queries**: How many questions you've asked
- **Average Confidence**: How confident the AI was
- **Recent Conversations**: Your last 10 chats

### How to Use

- **Click on any conversation** to see details
- **Review past answers** anytime
- **Track your health questions** over time

---

## ⚙️ Settings Page

### Login

**Demo Accounts** (for testing):
- `admin@healthcare.ai` / `admin123` (Admin)
- `doctor@healthcare.ai` / `doctor123` (Doctor)
- `patient@healthcare.ai` / `patient123` (Patient)

### How to Login

1. Go to **Settings**
2. Enter **email** and **password**
3. Click **Login**
4. You're logged in!

### User Preferences

- Enable notifications
- Save conversation history
- Show confidence scores

---

## 🚨 Emergency Detection

The system automatically detects **14 emergency symptoms**:

- Chest pain
- Difficulty breathing
- Severe bleeding
- Loss of consciousness
- Stroke symptoms
- Seizure
- Suicidal thoughts
- Severe allergic reaction
- And more...

**If detected**: You'll see a **red warning** telling you to call 911 immediately.

---

## 🔒 Privacy & Security

### Your Data is Safe

- ✅ **Encrypted storage**: All data is encrypted
- ✅ **HIPAA-compliant**: Audit logs track all access
- ✅ **No sharing**: Your data is never shared
- ✅ **Local processing**: Can run entirely offline

### What We Track

- Your questions and answers (for history)
- Uploaded reports (for your records)
- Login activity (for security)
- System usage (for improvements)

### What We DON'T Track

- ❌ Your personal health information outside the app
- ❌ Your identity (unless you login)
- ❌ Your location
- ❌ Your browsing history

---

## ⚡ Tips for Best Results

### Asking Questions

**Good Questions**:
- "What are the symptoms of diabetes?"
- "I have a persistent cough for 2 weeks, what should I do?"
- "Can I take ibuprofen with aspirin?"

**Better Questions**:
- "I'm 45 years old with high blood pressure. What are safe exercises?"
- "My lab report shows glucose at 180 mg/dL. What does this mean?"
- "I'm taking metformin. What foods should I avoid?"

**Why Better**: More context = more personalized answers!

### Uploading Reports

**Best Practices**:
- ✅ Use clear, readable scans
- ✅ Ensure text is visible
- ✅ Upload one report at a time
- ✅ Wait for analysis to complete

**Avoid**:
- ❌ Blurry photos
- ❌ Handwritten notes (hard to read)
- ❌ Multiple reports in one file

---

## 🆘 Troubleshooting

### "System Offline" in Sidebar

**Problem**: Can't connect to API  
**Solution**: 
1. Check if API is running: `curl http://localhost:8000/health`
2. Restart API: `uvicorn api.main:app --port 8000`

### "Analysis Timed Out"

**Problem**: Report analysis taking too long  
**Solution**:
1. Wait a bit longer (complex reports need 60+ seconds)
2. Try a simpler report
3. Check if API is responding: Visit `/health` endpoint

### "Invalid Credentials"

**Problem**: Can't login  
**Solution**:
1. Use demo credentials: `admin@healthcare.ai` / `admin123`
2. Check if you typed email correctly
3. Try registering a new account

### "No History Found"

**Problem**: Can't see past conversations  
**Solution**:
1. Make sure you're using the same session
2. Try asking a question first
3. Check if database is initialized

---

## 📱 Mobile Use

The app works on mobile browsers!

**Tips**:
- Use landscape mode for better layout
- Tap buttons instead of hover
- Use voice-to-text for questions
- Upload photos directly from camera

---

## 🎓 Advanced Features

### For Power Users

1. **Multi-Step Reasoning**: Ask complex questions (>15 words) to trigger 5-step analysis
2. **Knowledge Graph**: Mention diseases/drugs to get enhanced context
3. **Feedback**: Rate responses to help improve the system
4. **API Access**: Request API key for programmatic access

### For Clinicians

- Login with clinician account for specialized features
- Access admin panel for system management
- Generate API keys for integrations
- View audit logs for compliance

---

## 💡 Best Use Cases

### 1. Understanding Lab Reports
**Upload** → **Analyze** → **Get explanations** → **Receive recommendations**

### 2. Symptom Checking
**Describe symptoms** → **Get possible causes** → **Know when to see doctor**

### 3. Medication Information
**Ask about drug** → **Learn uses** → **Understand side effects** → **Check interactions**

### 4. Health Education
**Ask general questions** → **Get evidence-based answers** → **See sources**

---

## ⚠️ Important Disclaimers

### This AI Assistant:

✅ **CAN**:
- Provide general health information
- Explain medical terms
- Analyze lab reports
- Suggest when to see a doctor
- Give evidence-based answers

❌ **CANNOT**:
- Diagnose diseases
- Prescribe medications
- Replace your doctor
- Provide emergency medical care
- Make treatment decisions

### Always Remember:

**This is an educational tool, not a replacement for professional medical advice.**

For emergencies: **Call 911**  
For medical decisions: **Consult your doctor**

---

## 🆘 Getting Help

### In the App

- Check **System Status** in sidebar
- Review **error messages** carefully
- Try **refreshing** the page

### Technical Support

- GitHub Issues: https://github.com/Santhakumarramesh/healthcare-rag-agent/issues
- Email: (your email)

---

## 🎯 Quick Reference

### Demo Credentials
```
admin@healthcare.ai / admin123
doctor@healthcare.ai / doctor123
patient@healthcare.ai / patient123
```

### File Types Supported
- PDF: Lab reports, medical documents
- JPG/PNG: Photos of reports, scans

### Response Times
- Simple questions: 3-5 seconds
- Complex reasoning: 9-12 seconds
- Report analysis: 30-60 seconds

### System Requirements
- Modern web browser (Chrome, Firefox, Safari)
- Internet connection (for API access)
- JavaScript enabled

---

## 🎉 Enjoy!

You now have a powerful AI health assistant at your fingertips. Ask questions, upload reports, and get instant, evidence-based answers!

**Stay healthy!** 🏥💙
