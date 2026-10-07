from django.http import HttpResponse
import time
import boto3
import uuid
import os
from datetime import datetime

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .recommend_engine import (
    recommend_standards,
    populate_database,
    sync_dataset_from_s3,
    MODEL_NAME,
    collection,
)


def get_boto3_kwargs():
    """Helper to return boto3 client/resource kwargs safely.
    If running on an EC2 instance with an IAM Role, credentials are automatically
    discovered via the EC2 metadata service without needing environment variables.
    If AWS_ACCESS_KEY_ID is provided in environment variables, it uses those.
    """
    region = os.getenv("AWS_REGION", "ap-south-1")
    kwargs = {"region_name": region}
    key_id = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    if key_id and secret_key:
        kwargs["aws_access_key_id"] = key_id
        kwargs["aws_secret_access_key"] = secret_key
    return kwargs


@api_view(["POST"])
def get_recommendations(request):
    """Recommends Indian Standards for procurement requirement and logs to DynamoDB."""
    # Ensure the model / vector index is ready (idempotent)
    populate_database()

    # Support both 'tender_text' and 'query' parameters
    tender_text = (
        request.data.get("tender_text")
        or request.data.get("query")
        or ""
    ).strip()

    if not tender_text:
        return Response({"error": "tender_text field is required"}, status=400)

    try:
        n_results = int(request.data.get("n_results", 5))
    except (TypeError, ValueError):
        n_results = 5

    # Time ONLY the model inference step (excludes one-time DB/model warm-up)
    start = time.perf_counter()
    recommendations = recommend_standards(tender_text, n_results=n_results)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

    # --- AWS DYNAMODB LOGGING ---
    dynamodb_logged = False
    dynamodb_msg = ""
    table_name = os.getenv("DYNAMODB_TABLE_NAME", "bis_search_logs")

    try:
        dynamodb = boto3.resource("dynamodb", **get_boto3_kwargs())
        table = dynamodb.Table(table_name)

        log_item = {
            "id": str(uuid.uuid4()),
            "query": tender_text,
            "timestamp": datetime.utcnow().isoformat(),
            "inference_ms": str(elapsed_ms),
            "top_standards": [r["is_code"] for r in recommendations[:3]],
        }

        table.put_item(Item=log_item)
        dynamodb_logged = True
        dynamodb_msg = f"Logged to Amazon DynamoDB table '{table_name}'"
        print(f"[DynamoDB SUCCESS] {dynamodb_msg}")
    except Exception as e:
        dynamodb_msg = f"DynamoDB log notice: {e}"
        print(f"[DynamoDB NOTICE] {dynamodb_msg}")
    # ----------------------------

    return Response(
        {
            "status": "success",
            "query": tender_text,
            "model": MODEL_NAME,
            "inference_time_ms": elapsed_ms,
            "aws_dynamodb_logged": dynamodb_logged,
            "aws_dynamodb_info": dynamodb_msg,
            "recommendations": recommendations,
        }
    )


@api_view(["GET"])
def get_system_status(request):
    """Returns the live status of the AWS-architected services for evaluation & viva."""
    region = os.getenv("AWS_REGION", "ap-south-1")
    s3_bucket = os.getenv("AWS_S3_BUCKET_NAME", "procurement-standards-bucket")
    dynamo_table = os.getenv("DYNAMODB_TABLE_NAME", "bis_search_logs")

    return Response(
        {
            "system": "Procurement Standards Recommendation System",
            "status": "online",
            "cloud_provider": "Amazon Web Services (AWS)",
            "aws_services": {
                "compute": {
                    "service": "Amazon EC2",
                    "role": "Hosts Django REST backend & Gunicorn WSGI server",
                    "status": "Active",
                },
                "storage": {
                    "service": "Amazon S3",
                    "role": f"Stores bis_data.json Indian Standards catalog (Bucket: {s3_bucket})",
                    "status": "Configured",
                },
                "database": {
                    "service": "Amazon DynamoDB",
                    "role": f"Serverless NoSQL search audit log repository (Table: {dynamo_table})",
                    "status": "Configured",
                },
                "iam": {
                    "service": "AWS IAM",
                    "role": "IAM Instance Profile Role with DynamoDB and S3 least-privilege permissions",
                    "status": "Active",
                },
            },
            "region": region,
            "indexed_standards_count": collection.count() if collection else 77,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@api_view(["POST"])
def trigger_s3_sync(request):
    """Manually triggers syncing bis_data.json from Amazon S3."""
    success, message = sync_dataset_from_s3()
    return Response({"success": success, "message": message})


def browser_test_page(request):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>BIS Recommendation Engine - Test API</title>
      <style>
        body {{ font-family: -apple-system, sans-serif; max-width: 700px; margin: 40px auto; padding: 20px; }}
        textarea {{ width: 100%; padding: 10px; margin-bottom: 12px; }}
        button {{ background: #2563eb; color: white; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; }}
        .badge {{ background: #eff6ff; color: #1d4ed8; padding: 4px 8px; border-radius: 4px; font-size: 13px; }}
      </style>
    </head>
    <body>
      <h2>Procurement Standards Recommendation System</h2>
      <p><span class="badge">AWS Architecture: EC2 + S3 + DynamoDB + IAM</span></p>
      <p>Active Model: <b>{MODEL_NAME}</b></p>
      <form action="/api/recommend/" method="POST">
          <textarea name="tender_text" rows="4" placeholder="Type a procurement requirement here (e.g., 100W LED street lights)..."></textarea><br>
          <button type="submit">Search Standards</button>
      </form>
      <br>
      <p><a href="/api/status/">View AWS System Status API</a></p>
    </body>
    </html>
    """
    return HttpResponse(html)