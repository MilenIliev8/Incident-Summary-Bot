import os
from slack_bolt import App
from openai import OpenAI
from docx import Document
import requests

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)

def extract_text(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

def summarize(text):
    response = client.responses.create(
        model="gpt-5.3",
        input=f"""
Summarize this incident report in simple, non-technical language.
Write in paragraph form (no bullet points).

{text}
"""
    )
    return response.output_text

@app.event("message")
def handle_message(body, say):
    event = body["event"]

    if "files" in event:
        file = event["files"][0]

        if file["name"].endswith(".docx"):
            url = file["url_private_download"]

            headers = {
                "Authorization": f"Bearer {os.environ['SLACK_BOT_TOKEN']}"
            }

            r = requests.get(url, headers=headers)

            with open("file.docx", "wb") as f:
                f.write(r.content)

            text = extract_text("file.docx")
            summary = summarize(text)

            say(summary)
