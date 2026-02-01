# HelloHealth - Symptoms Analyzer

A modern web application that helps to analyze health symptoms using AI and provides information about possible conditions, treatments, and when to seek medical care.

## Project Overview

**HelloHealth** is a full-stack web application consisting of:
- **Frontend**: Interactive web interface built with HTML, CSS, and JavaScript
- **Backend**: FastAPI server that processes symptom queries using AI models

## Project Structure

```
Prog_Directory/
├── Frontend/
│   ├── index.html          # Main HTML page with symptom checker interface
│   ├── script.js           # JavaScript for interactivity and API calls
│   ├── styles.css          # Custom CSS styling
│   └── README.md           # Frontend specific documentation
├── Backend/
│   ├── main.py             # FastAPI server and symptom analysis logic
│   └── __pycache__/        # Python cache folder
└── Theory/                 # Theory and documentation files
```

## Prerequisites

Make sure you have the following installed:

### For Backend:
- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** - Python package manager (usually comes with Python)

### For Frontend:
- Any modern web browser (Chrome, Firefox, Safari, Edge)
- A local web server (VS Code Live Server extension or Python's http.server)

## Installation & Setup

### Step 1: Install Backend Dependencies

Open a terminal in the `Backend` folder and run:

```bash
# Windows
pip install fastapi uvicorn transformers torch pydantic python-multipart

# macOS/Linux
pip3 install fastapi uvicorn transformers torch pydantic python-multipart
```

**Package Descriptions:**
- `fastapi` - Web framework for building the API
- `uvicorn` - ASGI server to run the FastAPI app
- `transformers` - Hugging Face library for AI models
- `torch` - PyTorch (required for transformers)
- `pydantic` - Data validation library
- `python-multipart` - Required for form data parsing

### Step 2: Verify Installation

Check if all packages are installed correctly:

```bash
pip list
```

You should see all the installed packages including fastapi, uvicorn, and transformers.

## Running the Project

### Step 1: Start the Backend Server

1. Open a terminal/command prompt
2. Navigate to the `Backend` folder:
   ```bash
   cd Backend
   ```
3. Run the FastAPI server:
   ```bash
   # Windows
   python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

   # macOS/Linux
   python3 -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

4. You should see output like:
   ```
   INFO:     Uvicorn running on http://127.0.0.1:8000
   INFO:     Application startup complete
   ```

**Note:** Leave this terminal running! The backend must be active for the frontend to work.

### Step 2: Start the Frontend

You have two options to run the frontend:

#### Option A: Using VS Code Live Server (Recommended)

1. Install the **Live Server** extension in VS Code
2. Right-click on `index.html` in the Frontend folder
3. Select **"Open with Live Server"**
4. Your browser will automatically open to `http://127.0.0.1:5500`

#### Option B: Using Python's Built-in Server

1. Open another terminal and navigate to the `Frontend` folder:
   ```bash
   cd Frontend
   ```
2. Run Python's built-in server:
   ```bash
   # Windows
   python -m http.server 8001

   # macOS/Linux
   python3 -m http.server 8001
   ```
3. Open your browser and go to: `http://localhost:8001`

#### Option C: Using Node.js http-server

If you have Node.js installed:

```bash
npm install -g http-server
cd Frontend
http-server
```

### Step 3: Use the Application

1. Once both the frontend and backend are running, open your browser to the frontend URL
2. You'll see the HealthConnect homepage
3. In the Symptom Checker section:
   - Type a symptom in the search box (e.g., "headache", "fever", "cough")
   - OR click on one of the common symptom tags
4. The app will send your query to the backend and display results:
   - **Possible Diagnosis** - What condition the symptoms might indicate
   - **Confidence** - How confident the AI model is (0-100%)
   - **Next Steps** - Recommendations for what to do

## How It Works

### Frontend → Backend Communication

```
User Input
    ↓
JavaScript captures input
    ↓
Sends POST request to http://127.0.0.1:8000/check-symptoms
    ↓
Backend processes with AI model
    ↓
Returns diagnosis, confidence, and recommendations
    ↓
Frontend displays results to user
```

### API Endpoint Details

**Endpoint:** `POST /check-symptoms`

**Request Format:**
```json
{
  "symptoms": "user's symptom description"
}
```

**Response Format:**
```json
{
  "diagnosis": "Possible condition name",
  "confidence": 0.85,
  "recommendation": "Suggested next steps or treatment"
}
```

## Supported Symptoms

The backend comes with a knowledge base for these common symptoms:

- **Headache** - Tension Headache or Migraine
- **Fever** - Viral Infection
- **Cough** - Common Cold or Bronchitis
- **Fatigue** - Stress or Lack of Sleep
- **Nausea** - Food Poisoning or Digestive Upset
- **General Symptoms** - Fallback for unknown symptoms

For symptoms not in the knowledge base, the AI model will attempt to classify them using Hugging Face's BART model.

## Troubleshooting

### Issue: "Cannot GET /" or Frontend won't load

**Solution:** Make sure you're using a local server, not opening the HTML file directly. File:// URLs don't allow JavaScript to work properly.

### Issue: "Failed to fetch" error in the browser console

**Solution:** 
1. Check that the backend is running on `http://127.0.0.1:8000`
2. Verify the terminal shows "Application startup complete"
3. Check that ports 8000 and 5500/8001 are not blocked by your firewall

### Issue: Backend fails to load the AI model

**Solution:**
1. The first run may take time to download the model (~1-2 GB)
2. Check your internet connection
3. If it fails, the app will still work with the knowledge base fallback
4. Check the terminal for error messages starting with "Error loading"

### Issue: ModuleNotFoundError or ImportError

**Solution:**
1. Make sure all dependencies are installed: `pip install -r requirements.txt`
2. Use the correct Python version (3.8+)
3. Verify you're in the correct virtual environment

### Issue: Port 8000 is already in use

**Solution:**
Change the port in the startup command:
```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8080
```

Then update the frontend URL in `script.js`:
```javascript
const response = await fetch('http://127.0.0.1:8080/check-symptoms', {
```

## Features

✅ **AI-Powered Symptom Analysis** - Uses Hugging Face BART model for intelligent classification

✅ **Quick Common Symptom Tags** - Fast access to frequently searched symptoms

✅ **Confidence Scoring** - Shows how confident the AI is in its diagnosis

✅ **Knowledge Base** - Built-in medical knowledge for common conditions

✅ **Responsive Design** - Works on desktop, tablet, and mobile devices

✅ **Modern UI** - Clean, professional interface using Tailwind CSS

✅ **Emergency Contacts** - Quick access to emergency services

✅ **CORS Enabled** - Secure communication between frontend and backend

## Technology Stack

### Frontend
- **HTML5** - Page structure
- **CSS3** - Styling (with Tailwind CSS framework)
- **JavaScript (ES6+)** - Interactivity and API calls
- **Fetch API** - HTTP requests to backend

### Backend
- **Python 3.8+** - Programming language
- **FastAPI** - Web framework for building APIs
- **Uvicorn** - ASGI server
- **Transformers** - Hugging Face AI models
- **Pydantic** - Data validation
- **CORS Middleware** - Cross-Origin Resource Sharing

## Important Notes

⚠️ **Medical Disclaimer:**
This application is for **educational purposes only** and is NOT a substitute for professional medical advice. Always consult with a qualified healthcare provider for proper diagnosis and treatment. In case of emergency, call 911 (US) or your local emergency number immediately.

⚠️ **AI Limitations:**
- The AI model is trained on general text classification, not specialized medical data
- Confidence scores are estimates and may not be highly accurate
- Always cross-reference results with medical professionals

## Future Improvements

- [ ] User authentication and history tracking
- [ ] More comprehensive medical knowledge base
- [ ] Integration with real medical APIs
- [ ] Mobile app version
- [ ] Multi-language support
- [ ] Appointment booking integration
- [ ] Prescription management
- [ ] Insurance provider integration

## License

This project is created for educational purposes as part of the SkillCred GenAI program.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review the error messages in the browser console (F12)
3. Check the backend terminal for error logs
4. Verify both frontend and backend are running on the correct ports

---

**Last Updated:** 01 Feb, 2026

**Version:** 1.0

Happy healthy checking! 🏥
