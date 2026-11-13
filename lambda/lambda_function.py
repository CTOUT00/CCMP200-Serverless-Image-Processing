import boto3
from PIL import Image
import io

# Create an S3 client
s3 = boto3.client("s3")

def lambda_handler(event, context):

    # S3 bucket names
    source_bucket = "ccmp200-original-images-ctout00"
    destination_bucket = "ccmp200-resized-images-ctout00"

    try:
        # Get the image name from the event
        image_key = event["key"]

        print("Processing image:", image_key)

        # Download the original image from S3
        response = s3.get_object(Bucket=source_bucket, Key=image_key)
        image_data = response["Body"].read()

        # Open the image using Pillow
        image = Image.open(io.BytesIO(image_data))

        # Resize the image to a thumbnail
        image.thumbnail((200, 200))

        print("Image resized successfully")

        # Save the resized image in memory
        output = io.BytesIO()
        image.convert("RGB").save(output, format="JPEG")

        # Create a filename for the thumbnail
        thumbnail_name = "thumbnail-" + image_key.rsplit("/", 1)[-1].rsplit(".", 1)[0] + ".jpg"

        # Upload the thumbnail to the resized images bucket
        s3.put_object(
            Bucket=destination_bucket,
            Key=thumbnail_name,
            Body=output.getvalue(),
            ContentType="image/jpeg"
        )

        print("Thumbnail uploaded:", thumbnail_name)

        # Return the result
        return {
            "status": "SUCCESS",
            "thumbnail": thumbnail_name
        }

    except Exception as error:
        print("Error processing image:", error)

        return {
            "status": "FAILED",
            "error": str(error)
        }