import os
import sys
from openai import OpenAI
import base64
import json
import time
import simpleaudio as sa
import errno
from elevenlabs import generate, play, set_api_key, voices

client = OpenAI()

set_api_key(os.environ.get("ELEVENLABS_API_KEY"))

def encode_image(image_path):
    while True:
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except IOError as e:
            if e.errno != errno.EACCES:
                # Not a "file in use" error, re-raise
                raise
            # File is being written to, wait a bit and retry
            time.sleep(0.1)


def play_audio(text):
    gordonRamsay = "NhLSF6CDcklA15AYmjhQ"
    audio = generate(text, voice=gordonRamsay)

    unique_id = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8").rstrip("=")
    dir_path = os.path.join("narration", unique_id)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, "audio.wav")

    with open(file_path, "wb") as f:
        f.write(audio)

    play(audio)


def generate_new_line(base64_image):
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Criticize this image of food as if you are Gordon Ramsay."},
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}",
                },
            ],
        },
    ]


def analyze_image(base64_image, script):
    while True:
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are Gordon Ramsay. Criticize this image of food.
                    Make it snarky, incredibly mean, and funny.
                    """,
                },
            ]
            + script
            + generate_new_line(base64_image),
            max_tokens=500,
        )
        response_text = response.choices[0].message.content
        if not response_text.startswith("I'm sorry"):
            break
    return response_text


def main():
    script = []

    # path to your image
    image_path_str = sys.argv[1]
    # image_path = os.path.join(os.getcwd(), "./food/food.jpg")
    image_path = os.path.join(os.getcwd(), image_path_str)

    # getting the base64 encoding
    base64_image = encode_image(image_path)

    # analyze posture
    print("Loading...")
    analysis = analyze_image(base64_image, script=script)

    print("🎙️ Gordon says:")
    print(analysis)

    play_audio(analysis)

    script = script + [{"role": "assistant", "content": analysis}]


if __name__ == "__main__":
    main()
