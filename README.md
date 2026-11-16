
# CCMP200 - Serverless Image Processing

Cloud Computing Capstone Project

## Project Overview

For this project, I created a serverless image processing application using AWS.

The application automatically resizes images uploaded to an Amazon S3 bucket. AWS Lambda uses Python and Pillow to resize the images into thumbnails. The thumbnails are then saved in another S3 bucket.

I also used AWS Step Functions to manage the image processing workflow and check if it was successful or failed. API Gateway allows the workflow to be started using a POST request.

## AWS Architecture

The application can process images in two ways.

### 1. Automatic S3 Upload

1. An image is uploaded to the original-images S3 bucket.
2. S3 automatically triggers the Lambda function.
3. Lambda downloads the image and resizes it using Pillow.
4. The resized thumbnail is saved in the resized-images S3 bucket.

### 2. API Gateway and Step Functions

1. API Gateway receives a POST request with an image filename.
2. API Gateway starts the Step Functions workflow.
3. Step Functions runs the Lambda function.
4. Lambda gets the image from S3 and creates a thumbnail.
5. The Choice state checks the result from Lambda.
6. If the result is SUCCESS, the workflow goes to the Success state. If it fails, it goes to the Fail state.

### AWS Services Used

- **Amazon S3:** Stores the original images and resized thumbnails.
- **AWS Lambda:** Runs the Python code that resizes the images.
- **AWS Step Functions:** Manages the workflow and checks the results.
- **Amazon API Gateway:** Allows the workflow to be started using a POST request.
- **AWS IAM:** Manages permissions between AWS services.
- **Amazon CloudWatch:** Stores logs for troubleshooting.

## Prerequisites and Tools

### Prerequisites

- AWS account with access to the required services.
- GitHub account.
- Python 3.14 AWS Lambda runtime.
- Pillow library for image resizing.

### Tools Used

- Visual Studio Code - Used to write and edit the Python code.
- GitHub Desktop - Used to commit and push files to GitHub.
- AWS Management Console - Used to create and configure AWS services.
- AWS CloudShell - Used to install Pillow and create the Lambda Layer.

### AWS Configuration

- Region: us-east-2 (Ohio)
- Lambda function: ccmp200-image-resizer
- Runtime: Python 3.14
- Architecture: x86_64
- Memory: 512 MB
- Timeout: 30 seconds
- Lambda Layer: ccmp200-pillow-layer (version 1)
- Step Functions: ccmp200-image-processing-workflow
- API Gateway: ccmp200-image-processing-api
- API stage: dev

### S3 Buckets

Original images:
`ccmp200-original-images-ctout00`

Resized images:
`ccmp200-resized-images-ctout00`

Both buckets are private and located in us-east-2.

## Deployment Instructions

I deployed the application manually using the AWS Management Console.

### 1. Create the S3 Buckets

1. Sign in to AWS and open Amazon S3.
2. Create two buckets in us-east-2.
3. Use one bucket for original images and another for resized images.
4. Keep the buckets private with Block Public Access enabled.

The bucket names used in my project are listed above.

If setting up the project in another AWS account, use unique bucket names and update the Lambda code.

### 2. Create the Lambda Function

1. Open AWS Lambda.
2. Create a function named `ccmp200-image-resizer`.
3. Select Python 3.14 and x86_64.
4. Create an execution role with the required permissions.
5. Change the memory to 512 MB.
6. Change the timeout to 30 seconds.
7. Copy the code from `lambda/lambda_function.py`.
8. Update the S3 bucket names in the code if needed.
9. Deploy the function.

The Lambda role needs permission to:

- Read images from the original S3 bucket.
- Upload thumbnails to the resized S3 bucket.
- Write logs to CloudWatch.

### 3. Create the Pillow Lambda Layer

I used AWS CloudShell to install Pillow and create the Lambda Layer.

First, create a folder:

```bash
mkdir -p pillow-layer/python
```

Install Pillow:

```bash
python3 -m pip install Pillow -t pillow-layer/python \
  --platform manylinux2014_x86_64 \
  --implementation cp \
  --python-version 3.14 \
  --only-binary=:all:
```

Create the ZIP file:

```bash
cd pillow-layer
zip -r ../pillow-layer.zip python
```

After creating the ZIP file:

1. Open Lambda and select Layers.
2. Create a layer named `ccmp200-pillow-layer`.
3. Upload `pillow-layer.zip`.
4. Select the compatible Python runtime and x86_64 architecture.
5. Save the layer.
6. Open the Lambda function.
7. Attach the new layer.

### 4. Add the S3 Trigger

1. Open the Lambda function.
2. Select Add trigger.
3. Choose Amazon S3.
4. Select the original-images bucket.
5. Set the event type to All object create events.
6. Save the trigger.

Now, uploading an image to the original bucket will automatically run Lambda.

Only the original bucket should trigger this function. The resized bucket should not trigger it.

### 5. Create the Step Functions Workflow

1. Open AWS Step Functions.
2. Create a Standard state machine.
3. Name it `ccmp200-image-processing-workflow`.
4. Use the JSON file from `step-functions/image-processing-workflow.json`.
5. Update the Lambda ARN if using a different AWS account or function.
6. Configure an execution role that allows Step Functions to invoke Lambda.
7. Save the workflow.

The workflow has four states:

- **ResizeImage:** Runs the Lambda function.
- **CheckResizeStatus:** Checks if the result is SUCCESS.
- **ImageProcessingSuccess:** Runs when processing is successful.
- **ImageProcessingFailed:** Runs when processing fails.

### 6. Configure API Gateway

1. Open Amazon API Gateway.
2. Create a Regional REST API named `ccmp200-image-processing-api`.
3. Create a resource named `/process-image`.
4. Add a POST method.
5. Use AWS Service integration with the Step Functions StartExecution action.
6. Create an IAM role with permission to start the state machine.
7. Add the integration request mapping template.
8. Set the method authorization to AWS_IAM.
9. Deploy the API to the `dev` stage.

The API Gateway integration role needs the `states:StartExecution` permission for the state machine.

#### Request Mapping Template

Set the content type to `application/json`.

```json
{
  "input": "$util.escapeJavaScript($input.json('$'))",
  "stateMachineArn": "arn:aws:states:us-east-2:575607844351:stateMachine:ccmp200-image-processing-workflow"
}
```

Update the state machine ARN if using a different AWS account.

My API Gateway endpoint is:

`https://rbz9rmmw87.execute-api.us-east-2.amazonaws.com/dev/process-image`

This endpoint is for my AWS deployment. Another deployment will have a different URL.

The POST method uses AWS_IAM authorization. External requests need AWS credentials and SigV4 signing. I used the API Gateway console Test feature to test the integration.

## How to Run the Application

### Method 1: Upload an Image to S3

1. Open the original-images S3 bucket.
2. Upload a JPG image.
3. Open the resized-images bucket.
4. Check if the thumbnail was created.

The resized file will have `thumbnail-` at the beginning of its filename.

### Method 2: Use API Gateway

1. Upload an image to the original-images bucket if it is not already there.
2. Open API Gateway.
3. Select the `/process-image` POST method.
4. Open the Test tab.
5. Enter the following JSON:

```json
{
  "key": "owl.jpg"
}
```

6. Run the test.
7. Open Step Functions and find the new execution.
8. Check if the execution succeeded.

The filename in the request must match an image already stored in the original bucket.

## Testing and Results

I tested the application to make sure the S3 trigger, Lambda function, Step Functions workflow, and API Gateway were working.

### Test 1: Automatic Image Resizing

I uploaded `owl.jpg` to the original-images S3 bucket.

The upload triggered Lambda automatically. Lambda resized the image and uploaded `thumbnail-owl.jpg` to the resized-images bucket.

**Result: Passed**

Original image:
- Filename: owl.jpg
- Dimensions: 1365 x 2048 pixels

Resized image:
- Filename: thumbnail-owl.jpg
- Dimensions: 133 x 200 pixels

The thumbnail kept the same proportions as the original image.

The maximum thumbnail size is 200 x 200 pixels. Since the original image was portrait-oriented, the resized image was 133 x 200 instead of exactly 200 x 200.

### Test 2: API Gateway and Step Functions

I tested the POST method in API Gateway using:

```json
{
  "key": "owl.jpg"
}
```

API Gateway returned HTTP status 200 and started a Step Functions execution.

The workflow went through these states:

1. ResizeImage
2. CheckResizeStatus
3. ImageProcessingSuccess

The Step Functions execution showed Succeeded.

**Result: Passed**

### Test 3: Failure Handling

I tested the workflow using an image that did not exist in the original S3 bucket.

Request:

```json
{
  "key": "missing-image.jpg"
}
```

API Gateway returned HTTP 200 because it successfully started the workflow.

Lambda could not find the image and returned a failed processing result.

The Choice state then followed the `ImageProcessingFailed` branch.

The Step Functions execution showed Failed, which was the expected result for this test.

**Result: Passed**

### Test Summary

| Test                            | Result |
|---------------------------------|--------|
| Automatic S3 image processing   | Passed |
| Lambda image resizing           | Passed |
| Thumbnail dimensions            | Passed |
| API Gateway integration         | Passed |
| Step Functions success workflow | Passed |
| Step Functions failure workflow | Passed |

All the tests passed.

## Repository Structure

- `lambda/lambda_function.py` - Python code for resizing images.
- `step-functions/image-processing-workflow.json` - Step Functions workflow definition.
- `test-images/` - Folder for test images.
- `docs/` - Folder for documentation.
- `README.md` - Project information, setup instructions, and test results.
- `.gitignore` - Lists files that Git should ignore.

## Conclusion

For this capstone, I created a serverless application that resizes images using AWS.

I used S3 and Lambda to automatically process uploaded images. I also used API Gateway and Step Functions to start the image processing workflow and check if it was successful.

I tested the application with working images and a missing image. The tests showed that the application can resize images and handle processing failures.
