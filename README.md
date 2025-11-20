# Medical Report Analyzer 🏥

A professional AI-powered web application that analyzes medical reports (PDFs, Images) to extract test results, provide insights, and check for drug interactions. Built with Flask, Google Gemini AI, and Tailwind CSS.

## 🚀 Features

*   **AI Analysis**: Extracts patient details, dates, and test results from medical reports.
*   **Smart Insights**: Automatically flags High/Low values and provides simplified health insights.
*   **Drug Lookup**: Search for drugs to view brand/generic names, purposes, and FDA warnings.
*   **Interactive UI**: Mobile-responsive design with professional animations.
*   **Manual Correction**: "Something not right?" feature allows users to manually edit AI-extracted data and re-analyze.
*   **PDF Export**: Print or save the analysis results as a PDF.

## 🛠️ Tech Stack

*   **Backend**: Python, Flask
*   **AI Engine**: Google Gemini 2.5 Flash
*   **Frontend**: HTML, Tailwind CSS (Standalone)
*   **PDF Processing**: pdfplumber
*   **Image Processing**: Pillow
*   **External APIs**: openFDA (Drug Search)

## 📋 Prerequisites

*   Python 3.8 or higher
*   A Google Cloud API Key (for Gemini AI)

## ⚙️ Installation

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd medical-analyzer
    ```

2.  **Create a virtual environment**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables**
    Create a `.env` file in the root directory and add your API key:
    ```env
    GOOGLE_API_KEY=your_google_api_key_here
    FLASK_SECRET_KEY=your_secret_key_here
    ```

5.  **Run the application**
    ```bash
    python run.py
    ```

6.  **Access the app**
    Open your browser and go to `http://127.0.0.1:5000`

## 🎨 CSS Development (Optional)

If you want to modify the styles, you need the Tailwind CSS standalone executable.

1.  Download `tailwindcss.exe` and place it in the root directory.
2.  Run the build command:
    ```bash
    .\tailwindcss.exe -i app/static/src/input.css -o app/static/dist/output.css --watch
    ```

## 🔒 Privacy Note

This application processes medical data using an external AI service (Google Gemini). Ensure you comply with local data privacy regulations (like HIPAA or GDPR) before using it with real patient data.

## 📄 License

[MIT License](LICENSE)
