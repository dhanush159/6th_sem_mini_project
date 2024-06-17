import os
import requests
import io
from PIL import Image
import random
from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import FewShotPromptTemplate, PromptTemplate

# Set the environment variable for Hugging Face API token
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"

# Initialize the LLM with the specified parameters
llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.3",
    temperature=0.5,
    max_length=1024,
    max_new_tokens=500
)

# Define the Hugging Face API URL and headers for image generation
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": "Bearer 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"}

def create_payload(prompt, seed):
    return {
        "inputs": prompt,
        "options": {
            "seed": seed
        }
    }

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response

def save_image(image_bytes, file_name):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.save(file_name)  # Save the image
        return file_name
    except IOError:
        print("Cannot identify image file")
        return None

# Function to extract content after a specified marker
def extract_content_after_marker(text, marker):
    marker_position = text.find(marker)
    if marker_position != -1:
        return text[marker_position + len(marker):].strip()
    return "Marker not found in text."

# Define the process_llm function
def process_llm(article_text, url):
    examples = [
        {
            "title": "this is example 1🚀 Transforming Digital Marketing in 2024! 🚀",
            "description": """I am excited to share my latest article on the future of digital marketing. In this piece, we explore the latest trends, including AI-driven analytics, personalized content strategies, and multi-channel engagement.

    ✨ Highlights include:
    - The rise of AI in marketing
    - Personalized customer journeys
    - Effective multi-channel strategies

    This is a must-read for marketers looking to stay ahead of the game!

    👉 Read the full article here: [link]

    #DigitalMarketing #MarketingTrends #AI #Personalization #Innovation #2024Trends"""
        },
        {
            "title": "this is example 2🌟 Revolutionizing Healthcare with Technology 🌟",
            "description": """Check out my new article on how technology is transforming healthcare. We delve into groundbreaking advancements such as telemedicine, AI diagnostics, and personalized treatment plans.

    🔍 Key points covered:
    - The growth of telemedicine
    - AI in disease diagnosis
    - Personalized healthcare solutions

    Healthcare professionals, don't miss out on these insights!

    👉 Read more: [link]

    #Healthcare #HealthTech #AIinHealthcare #Telemedicine #Innovation #MedicalTrends"""
        }
    ]

    example_prompt = PromptTemplate(
        input_variables=["title", "description"],
        template="{title}\n\n{description}"
    )

    prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        prefix="Read the following article text and create a LinkedIn post description that highlights the key points and insights. The post should be engaging, professional, and encourage readers to read the full article. Include a call-to-action and relevant hashtags. Below are examples of similar posts. aslo in place of link add the url given",
        suffix="Your Turn:\n\nArticle Text:\n\n{article_text}\n\nURL of the article: {url}",
        input_variables=["article_text", "url"]
    )

    final_prompt = prompt.format(article_text=article_text, url=url)
    res = llm.invoke(final_prompt)

    marker_text = "LinkedIn Post:"
    content_after_marker = extract_content_after_marker(res, marker_text)

    prompt_2 = f"{content_after_marker} form a simple prompt for a text to image model to generate an image with simple imagination avoid text for this linkedin description given above, just give the prompt do not generate pictures urself"
    prompt_image = llm.invoke(prompt_2).strip()

    image_files = []
    for i in range(3):
        seed = random.randint(0, 1000000)  # Generate a random seed
        payload = create_payload(prompt_image, seed)
        response = query(payload)
        if response.status_code == 200:
            image_bytes = response.content
            file_name = f"image_{i+1}.png"
            saved_file = save_image(image_bytes, file_name)
            if saved_file:
                image_files.append(saved_file)
        else:
            print(f"Failed to retrieve image. Status code: {response.status_code}")
            print(response.text)  # Print the error message if any

    return res, image_files
