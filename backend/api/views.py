from django.http import HttpResponse
import time
import boto3
import uuid
import os
from datetime import datetime

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .recommend_engine import recommend_standards, populate_database, MODEL_NAME


@api_view(["POST"])
def get_recommendations(request):
    # Ensure the model / index is ready (idempotent - trains or loads once, then reuses)
    populate_database()

    tender_text = request.data.get("tender_text", "")

    if not tender_text:
        return Response({"error": "tender_text field is required"}, status=400)

    n_results = int(request.data.get("n_results", 5))

    # Time ONLY the model inference step (excludes one-time DB/model warm-up)
    start = time.perf_counter()
    recommendations = recommend_standards(tender_text, n_results=n_results)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

    # --- AWS DYNAMODB LOGGING ---
    try:
        # Initialize boto3 DynamoDB resource using environment variables securely
        dynamodb = boto3.resource(
            'dynamodb', 
            region_name='ap-southeast-2',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), 
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        table = dynamodb.Table('bis_search_logs')
        
        # Write the search log to AWS
        table.put_item(
            Item={
                'id': str(uuid.uuid4()),  # Generates a unique ID for the database row
                'query': tender_text,
                'timestamp': datetime.utcnow().isoformat(),
                'inference_ms': str(elapsed_ms)
            }
        )
        print("✅ Successfully logged search to DynamoDB!")
    except Exception as e:
        print(f"❌ Failed to log to AWS: {e}")
    # ----------------------------

    return Response(
        {
            "status": "success",
            "query": tender_text,
            "model": MODEL_NAME,
            "inference_time_ms": elapsed_ms,
            "recommendations": recommendations,
        }
    )


def browser_test_page(request):
    html = f"""
    <h2>Test the AI Recommendation Engine</h2>
    <p>Active model: <b>{MODEL_NAME}</b></p>
    <form action="/api/recommend/" method="POST">
        <textarea name="tender_text" rows="4" cols="50" placeholder="Type a procurement requirement here (e.g., 100W LED street lights)..."></textarea><br><br>
        <button type="submit">Search Standards</button>
    </form>
    """
    return HttpResponse(html)