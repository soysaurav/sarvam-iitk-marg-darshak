import os
from dotenv import load_dotenv
from sarvamai import SarvamAI

# Load environment variables from .env
load_dotenv()

# Initialize Sarvam client reading SARVAM_API_KEY from environment
client = SarvamAI(api_subscription_key=os.getenv("SARVAM_API_KEY"))

# Make a chat completion call with the sarvam-105b-conversations model
response = client.chat.completions(
    model="sarvam-105b-conversations",
    messages=[
        {"role": "user", "content": "Hello! Introduce yourself in one short sentence."}
    ],
    max_tokens=30,
)

# Print the response reply
print(response.choices[0].message.content)
