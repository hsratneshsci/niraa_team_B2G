# 🚀 KazhaiAI - Simplified MVP (48-Hour Hackathon Edition)

KazhaiAI converts voice-based daily income logging into a trusted economic identity for gig workers.

## 🌟 Key Features
1.  **Voice-First Income Logger**: Speak your earnings ("I earned 850 today") -> Auto-logged.
2.  **KazhaiScore**: A proprietary credit score based on income stability measure, not just total earnings.
3.  **SkillMatch AI**: Chat with an AI to find better jobs based on your current skills.
4.  **Local-First Design**: Powered by lightweight SQLite and Local Python logic. No heavy cloud dependencies.

## 🛠️ Tech Stack
-   **Backend**: Flask (Python)
-   **Frontend**: HTML, CSS (Glassmorphism UI), JS (Web Speech API)
-   **Database**: SQLite
-   **AI**: Google Gemini (via API) + Rule-based logic

## 🚀 How to Run
1.  **Prerequisites**: Python 3.10+ installed.
2.  **Double Click**: Run `run_dev.bat`
    *   This will install dependencies (`Flask`, `google-generativeai`, `reportlab`, etc.)
    *   Start the server at `http://127.0.0.1:5000`

## 📱 Usage
1.  **Login**: Enter any phone number (e.g., `9876543210`).
2.  **Dashboard**:
    *   Use the **Microphone** button to speak: "I earned 1200 rupees writing code".
    *   See your **KazhaiScore** update in real-time.
    *   View your income chart.
3.  **SkillMatch**:
    *   Go to "SkillMatch" and type/speak: "I drive a taxi and know all the city routes".
    *   Get instant job recommendations.
4.  **Export**: Click "Download Ledger PDF" for a bank-ready document.

## 🧠 Design Philosophy
"Simple but believable." The app uses premium aesthetics to build trust, while keeping the tech stack rugged and local-friendly.

---
*Built for the [Hackathon Name] by Antigravity*
