from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = (
    "You are a mental wellness reflection chatbot. "
    "You listen empathetically, reflect emotions, ask gentle questions, "
    "and never give medical or diagnostic advice."
)

conversation_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "Mental Wellness Reflection Bot"
}

def chat_with_bot(user_message):
    conversation_history.append(
        {"role": "user", "content": user_message}
    )

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": conversation_history,
        "temperature": 0.7
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    result = response.json()

    if "choices" not in result:
        return f"API error: {result}"

    bot_reply = result["choices"][0]["message"]["content"]

    conversation_history.append(
        {"role": "assistant", "content": bot_reply}
    )

    return bot_reply


def reflect_on_image(image_url):
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a mental wellness reflection chatbot. "
                    "Gently reflect on the image and ask a supportive, non-diagnostic question."
                )
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Please reflect on this image."},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    }
                ]
            }
        ]
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    result = response.json()

    if "choices" not in result:
        return "I couldn't reflect on the image right now."

    return result["choices"][0]["message"]["content"]


@app.route("/", methods=["GET", "POST"])
def index():
    bot_reply = ""
    image_reply = ""

    if request.method == "POST":
        user_text = request.form.get("user_text")
        image_url = request.form.get("image_url")

        if user_text:
            bot_reply = chat_with_bot(user_text)

        if image_url:
            image_reply = reflect_on_image(image_url)

    return render_template(
        "index.html",
        bot_reply=bot_reply,
        image_reply=image_reply
    )


if __name__ == "__main__":
    app.run()
