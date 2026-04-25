# AI Resume Analyzer

A web-based application that evaluates resumes against job descriptions by computing a match score, identifying skill gaps, and generating structured reports.

---

## 🚀 Features

* Compare resume with job description
* Compute match score using text similarity
* Identify matched and missing skills
* Generate downloadable PDF reports
* Provide improvement suggestions using Gemini API

---

## 🛠️ Tech Stack

* **Backend:** Flask (Python)
* **NLP:** scikit-learn (TF-IDF, Cosine Similarity)
* **AI Integration:** Google Gemini API
* **PDF Processing:** pdfplumber
* **Report Generation:** reportlab
* **Frontend:** HTML, CSS, JavaScript

---

## 📂 Project Structure

```
AI-Resume-Analyzer/
│── app.py
│── requirements.txt
│
├── utils/
│   ├── nlp_engine.py
│   ├── pdf_processor.py
│   ├── llm_integration.py
│   ├── report_generator.py
│
├── templates/
│   └── index.html
│
├── static/
│   └── style.css
│
├── uploads/
├── reports/
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```
git clone https://github.com/akashruttala/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer
```

### 2. Create virtual environment

```
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Add environment variables

Create a `.env` file and add:

```
GEMINI_API_KEY=your_api_key_here
```

### 5. Run the application

```
python app.py
```

---

## 📊 How It Works

1. User uploads resume and provides job description
2. Text is extracted from PDF files
3. Text is processed and converted into vectors using TF-IDF
4. Cosine similarity is used to calculate match score
5. Skills are classified into matched and missing
6. Gemini API generates improvement suggestions
7. A structured PDF report is generated

---

## 📌 Key Highlights

* Modular backend design for scalability
* Efficient text similarity-based matching
* Integration of AI for dynamic suggestions
* End-to-end automation from input to report

---

## 📸 Preview
<img width="2079" height="1112" alt="image" src="https://github.com/user-attachments/assets/90105633-103e-44a1-b90e-5da064e8a0d3" />

<img width="1651" height="1110" alt="image" src="https://github.com/user-attachments/assets/908e89b4-3dcb-4be6-ad22-84b83991e0d0" />

<img width="2060" height="1102" alt="image" src="https://github.com/user-attachments/assets/2c1ff409-2266-4f4b-b6d9-6cef1589f092" />

---

## 🔗 Repository

https://github.com/akashruttala/AI-Resume-Analyzer
