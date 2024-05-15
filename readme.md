# PDF File Renaming with Google Generative AI

This script uses Google's Generative AI (Gemini) to rename PDF files of scientific journal articles based on their title and first author name.

## Requirements

- Python 3
- PyPDF2
- google-generativeai
- Google AI Studio API Key (https://aistudio.google.com/) (Currently it's free)
- python-dotenv

## Setup

1. Install the required Python packages:

    ```bash
    pip install PyPDF2 google-generativeai python-dotenv
    ```

2. Set up your Google Generative AI API key:

    Create a `.env` file in the same directory as the script and add your API key:

    ```env
    GENAI_API_KEY=your_api_key_here
    ```

## Usage

Ensure that the script and the PDF files you want to rename are in the same directory.

To run the script, use the following command in your terminal:

```bash
python script.py
```
If you see an error message saying `google.api_core.exceptions.ResourceExhausted: 429 Resource has been exhausted (e.g. check quota)`, wait a few seconds and then run it again. Or, you can change the wait time in the code `time.sleep(seconds)`."# PDF_file_rename" 
