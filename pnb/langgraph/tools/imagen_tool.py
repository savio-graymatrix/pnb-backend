from langchain_core.tools import tool
import google.genai as genai
from google.genai import types
from pnb import LOGGER, SETTINGS
import uuid
import traceback
import boto3

client = boto3.client(
    "s3",
    aws_access_key_id=SETTINGS.AWS_ACCESS_KEY,
    aws_secret_access_key=SETTINGS.AWS_SECRET_KEY,
)


@tool
async def imagen_tool(prompt: str):
    """
    Tool to generate an image using Google's Imagen

    Args:
        prompt(str): The prompt to generate an image
    Returns:
        str: The url of the generated image
    Raises:
        Exception if the image could not be generated
    """
    try:
        GEMINI_API_KEY = SETTINGS.GEMINI_API_KEY
        if not GEMINI_API_KEY:
            raise Exception("Gemini api key not found")

        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_images(
            model=SETTINGS.GEMINI_IMAGE_MODEL,
            prompt=prompt,
            config=types.GenerateImagesConfig(number_of_images=1),
        )

        if not response.generated_images:
            raise Exception("Image could not be generated")

        generated_image = response.generated_images[0]

        image_bytes = generated_image.image.image_bytes
        return await upload_s3(image_bytes)
    except Exception as e:
        return f"Failed to generate image: {e}"


async def upload_s3(image_bytes: bytes):
    image_filename = f"{uuid.uuid4()}.png"
    response = client.put_object(
        Bucket=SETTINGS.AWS_BUCKET,
        Key=image_filename,
        Body=image_bytes,
        ContentType="image/png",
    )
    if not response:
        raise Exception("Image could not be uploaded")
    return f"https://{SETTINGS.AWS_BUCKET_URL}/{image_filename}"

    # return {"image_id": image_filename, "status": "generated"}
