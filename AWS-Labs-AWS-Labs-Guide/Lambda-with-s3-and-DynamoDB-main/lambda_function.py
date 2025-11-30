import boto3
import base64
import os
import uuid
from requests_toolbelt.multipart import decoder

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

BUCKET_NAME = os.environ.get("BUCKET_NAME", "majhidisablewali")
TABLE_NAME = os.environ.get("TABLE_NAME", "reels")
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", "GET")

    # ====================== SERVE FORM ======================
    if method == "GET":
        html_form = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Upload Form</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {
                    background: linear-gradient(135deg, #74ebd5, #ACB6E5);
                    height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .card {
                    border-radius: 20px;
                    box-shadow: 0 8px 20px rgba(0,0,0,0.2);
                }
                h2 {
                    text-align: center;
                    color: #333;
                }
                .btn-custom {
                    background: #6a11cb;
                    background: linear-gradient(to right, #2575fc, #6a11cb);
                    color: white;
                    font-weight: bold;
                    border: none;
                }
                .btn-custom:hover {
                    opacity: 0.9;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="row justify-content-center">
                    <div class="col-md-6">
                        <div class="card p-4">
                            <h2>Upload File 🚀</h2>
                            <form action="" method="post" enctype="multipart/form-data">
                                <div class="mb-3">
                                    <label class="form-label">Name</label>
                                    <input type="text" class="form-control" name="name" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Caption</label>
                                    <input type="text" class="form-control" name="caption" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Choose File</label>
                                    <input type="file" class="form-control" name="file" required>
                                </div>
                                <button type="submit" class="btn btn-custom w-100">Upload</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/html"},
            "body": html_form
        }

    # ====================== HANDLE POST ======================
    elif method == "POST":
        try:
            body = base64.b64decode(event["body"])
            content_type = event["headers"].get("content-type") or event["headers"].get("Content-Type")

            multipart_data = decoder.MultipartDecoder(body, content_type)

            name, caption, file_content, filename = None, None, None, None

            for part in multipart_data.parts:
                cd = part.headers[b'Content-Disposition'].decode()
                if 'name="name"' in cd:
                    name = part.text
                elif 'name="caption"' in cd:
                    caption = part.text
                elif 'name="file"' in cd:
                    file_content = part.content
                    if "filename=" in cd:
                        filename = cd.split("filename=")[1].strip('"')

            if not (name and caption and file_content):
                return {"statusCode": 400, "body": "Missing fields"}

            # Save file to S3
            unique_name = str(uuid.uuid4()) + "_" + (filename or "upload.bin")
            s3_key = f"uploads/{unique_name}"
            s3.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=file_content)

            file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"

            # Save record in DynamoDB
            table.put_item(
                Item={
                    "id": str(uuid.uuid4()),
                    "name": name,
                    "caption": caption,
                    "file_url": file_url
                }
            )

            success_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Upload Successful</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body {{
                        background: #f8f9fa;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        height: 100vh;
                    }}
                    .card {{
                        border-radius: 20px;
                        padding: 20px;
                        box-shadow: 0 6px 15px rgba(0,0,0,0.2);
                        text-align: center;
                    }}
                    a {{
                        color: #2575fc;
                        font-weight: bold;
                    }}
                </style>
            </head>
            <body>
                <div class="card">
                    <h2>✅ Upload Successful!</h2>
                    <p><b>Name:</b> {name}</p>
                    <p><b>Caption:</b> {caption}</p>
                    <p><b>File URL:</b> <a href="{file_url}" target="_blank">{file_url}</a></p>
                    <a href="/" class="btn btn-primary mt-3">Upload Another</a>
                </div>
            </body>
            </html>
            """
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "text/html"},
                "body": success_html
            }

        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "text/plain"},
                "body": f"Error: {str(e)}"
            }
