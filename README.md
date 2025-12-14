# agent-sortmyemails
Smart email sorter using OpenAI GPT and Gmail API.

## Features
- **Dynamic Categorization**: Uses GPT-3.5 to automatically categorize your recent emails into useful folders.
- **Smart Filtering**: Automatically creates Gmail filters for senders, so future emails go directly to the right category.
- **Secure**: Handles credentials securely using environment variables and `credentials.json`.

## Setup

### Prerequisites
1. **Python 3.8+**
2. **Google Cloud Project** with Gmail API enabled.
   - Download `credentials.json` and place it in the root directory.
3. **OpenAI API Key**.

### Installation
1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   # Or if using uv/pip-tools
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client openai python-dotenv
   ```
3. Set up environment variables:
   Create a `.env` file in the root directory:
   ```
   OPENAI_API_KEY=sk-your-openai-api-key
   ```

## Usage
Run the main script:
```bash
python agent-sortmyemails/main.py
```
- On first run, it will open a browser window to authenticate with Google.
- It scans the last 7 days of emails (checking 50 at a time).
- It categorizes them and creates labels/filters in your Gmail.

## Testing
Run unit tests:
```bash
python -m unittest discover -s tests
```
