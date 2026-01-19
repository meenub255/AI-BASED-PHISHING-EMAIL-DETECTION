# AI-Based Phishing Email Detection

An advanced AI-powered system that analyzes emails for phishing risks using a multi-agent approach (Prosecutor, Auditor, and Judge agents). This system can analyze mock data or stream live emails from Gmail.

## Features

- **Multi-Agent Analysis**: Uses three distinct agents to evaluate email content, headers, and sender reputation.
- **PhishGuard Orchestrator**: Manages the analysis pipeline.
- **Live Gmail Integration**: Real-time scanning of incoming emails.
- **Mock Mode**: Built-in test scenarios for development and demonstration.

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.com/) (Required for local LLM inference)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/meenub255/AI-BASED-PHISHING-EMAIL-DETECTION.git
   cd AI-BASED-PHISHING-EMAIL-DETECTION
   ```

2. **Install dependencies:**
   ```bash
    pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install
   ```

## Gmail Setup (Optional for Live Mode)

To use the live Gmail streaming feature:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project and enable the **Gmail API**.
3. Create OAuth 2.0 credentials (Desktop App) and download the file.
4. Rename the file to `credentials.json` and place it in the project root directory.

## Usage

### Run with Mock Data (Default)
Run the analysis on a pre-defined test email to verify the system is working:

```bash
python src/main.py
```

### Run in Live Mode
Stream and analyze emails from your Gmail inbox in real-time:

```bash
python src/main.py --live
```
*Note: On the first run, a browser window will open for you to log in to your Google account.*

## Project Structure

- `src/agents/`: Contains the logic for Prosecutor, Auditor, and Judge agents.
- `src/utils/`: Utility scripts including Gmail service integration.
- `src/main.py`: Main entry point for the application.
