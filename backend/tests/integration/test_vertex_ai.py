"""
Quick test script to verify Vertex AI image generation is working.
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.vertex_image_client import get_vertex_image_client
from app.core.config import settings


async def test_vertex_ai():
    """Test Vertex AI image generation."""
    print("=" * 60)
    print("Testing Vertex AI Image Generation")
    print("=" * 60)

    print(f"\n✓ USE_VERTEX_AI: {settings.USE_VERTEX_AI}")
    print(f"✓ Project ID: {settings.VERTEX_AI_PROJECT_ID}")
    print(f"✓ Location: {settings.VERTEX_AI_LOCATION}")
    print(f"✓ Credentials Path: {settings.VERTEX_AI_CREDENTIALS_PATH}")

    # Check if credentials file exists
    creds_path = os.path.join(os.path.dirname(__file__), settings.VERTEX_AI_CREDENTIALS_PATH)
    if os.path.exists(creds_path):
        print(f"✓ Credentials file found at: {creds_path}")
    else:
        print(f"✗ Credentials file NOT found at: {creds_path}")
        return

    try:
        print("\nInitializing Vertex AI client...")
        client = get_vertex_image_client(
            credentials_path=creds_path,
            project_id=settings.VERTEX_AI_PROJECT_ID,
            location=settings.VERTEX_AI_LOCATION
        )
        print("✓ Vertex AI client initialized successfully!")

        print("\nGenerating test image (this may take 10-15 seconds)...")
        print("Prompt: 'a red apple'")

        result = await client.generate_safe_image("a red apple")

        if result:
            print(f"\n✓ SUCCESS! Image generated!")
            print(f"  Image size: {len(result)} characters (base64)")
            print(f"  First 50 chars: {result[:50]}...")
            print("\n🎉 Vertex AI image generation is working perfectly!")
        else:
            print("\n✗ FAILED: Image generation returned None")
            print("Check the logs above for errors.")

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        print("\nPossible issues:")
        print("1. Vertex AI API not enabled in your Google Cloud project")
        print("2. Service account doesn't have proper permissions")
        print("3. Billing not enabled")
        print("\nTo fix:")
        print("- Go to: https://console.cloud.google.com/apis/library/aiplatform.googleapis.com")
        print("- Enable Vertex AI API")
        print("- Make sure billing is enabled")


if __name__ == "__main__":
    asyncio.run(test_vertex_ai())
