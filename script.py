"""
See the getting started guide for more information:
https://ai.google.dev/gemini-api/docs/get-started/python
"""

import os
import PyPDF2
import re
import google.generativeai as genai
from glob import glob
import shutil
import time
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("GENAI_API_KEY")

if api_key is None:
    raise ValueError("Missing environment variable: GENAI_API_KEY")

genai.configure(api_key=api_key)

# Set up the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 200,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
]

# modify if needed
system_instruction = """Input: The first page of a scientific journal article.
            Output: Reply with the title of the paper followed by the last name of the first author. 
            Format the response as: "Title of the Paper - First Author's Last Name". 
            Do not include any additional text or information."""


model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",  # change model if needed
    generation_config=generation_config,
    safety_settings=safety_settings,
    system_instruction=system_instruction,
)

if not os.path.exists("Papers"):
    os.makedirs("Papers")

# list of PDF files in the current directory
pdf_files = glob("*.pdf")
print(f"{pdf_files}")

for filename in pdf_files:
    with open(filename, "rb") as pdf:
        reader = PyPDF2.PdfFileReader(pdf)
        content = reader.getPage(0).extractText()  # get content of the first page
        lines = content.split("\n")  # split the content into lines
        first_50_lines = lines[:50]  # get the first 50 lines

    clean_lines = [
        re.sub(r"\W+", " ", line) for line in first_50_lines
    ]  # remove non-alphanumeric characters
    message = " ".join(clean_lines)
    response = model.generate_content(message)  # gemini response
    print(f"{'--'*50}\nModel output: {response.text}")

    # Remove non-alphanumeric characters except for hyphen
    clean_filename = re.sub(r'[\\/:*?"<>|]', "", response.text).strip() + ".pdf"
    os.rename(filename, clean_filename)  # rename the file
    shutil.move(
        clean_filename, "Papers/" + clean_filename
    )  # move the file to the Papers directory
    print(f"Renamed file to: {clean_filename}\n{'--'*50}")
    time.sleep(10) # sleep for 10 seconds to avoid rate limiting in google genai

print("Task Complete.")
