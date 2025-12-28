"""
LiteLLM Failover Demo

This script demonstrates LiteLLM's automatic failover routing feature.
When the primary model (llama-fp8) becomes unavailable, LiteLLM automatically
routes requests to the fallback model (llama3).

Prerequisites:
- LiteLLM configured with router_settings fallbacks in values.yaml
- Both llama-fp8 and llama3 models available

Usage:
1. Run this script
2. While it's running, manually restart the llama-fp8 service
3. Observe how requests automatically failover to llama3
4. Press Ctrl+C to stop
"""

import time
import signal
from openai import OpenAI


# Configuration
BASE_URL = "https://litellm-hacohen-llmlite.apps.ai-dev02.kni.syseng.devcluster.openshift.com"
API_KEY = "master-key"
PRIMARY_MODEL = "llama-fp8"  # Use model_name for router fallback to work
REQUEST_INTERVAL = 3  # seconds between requests

# Track state
running = True
request_count = 0
successful_requests = 0
failed_requests = 0
failover_detected = False

# Initialize OpenAI client pointing to LiteLLM proxy
client = OpenAI(
    base_url=f"{BASE_URL}/v1",
    api_key=API_KEY,
)


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    global running
    print("\n\n[!] Stopping demo...")
    running = False


def send_request(model: str, prompt: str):
    """Send a completion request via the LiteLLM proxy."""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response


def get_model_from_response(response) -> str:
    """Extract the actual model that served the request from response."""
    if hasattr(response, 'model') and response.model:
        return response.model
    return "unknown"


def print_status_header():
    """Print the demo header."""
    print("=" * 70)
    print("LiteLLM Failover Demo")
    print("=" * 70)
    print(f"  Primary Model: {PRIMARY_MODEL}")
    print("  Fallback Model: llama3 (configured in router_settings)")
    print(f"  Request Interval: {REQUEST_INTERVAL}s")
    print("=" * 70)
    print("\n[*] Sending requests to primary model...")
    print("[*] To test failover: restart the llama-fp8 service in another terminal")
    print("[*] Press Ctrl+C to stop\n")
    print("-" * 70)


def print_summary():
    """Print final summary."""
    print("\n" + "=" * 70)
    print("Demo Summary")
    print("=" * 70)
    print(f"  • Total requests: {request_count}")
    print(f"  • Successful: {successful_requests}")
    print(f"  • Failed: {failed_requests}")
    if failover_detected:
        print("  • Failover: ✓ Detected and handled")
    else:
        print("  • Failover: Not triggered (primary stayed healthy)")
    print("=" * 70)


def main():
    global running, request_count, successful_requests, failed_requests, failover_detected

    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    print_status_header()

    last_model = None
    prompt = "Say 'hello' in one word."

    while running:
        request_count += 1
        timestamp = time.strftime("%H:%M:%S")

        try:
            response = send_request(PRIMARY_MODEL, prompt)
            content = response.choices[0].message.content
            actual_model = get_model_from_response(response)

            # Detect failover
            if last_model is not None and actual_model != last_model:
                failover_detected = True
                print(f"\n{'!'*70}")
                print(f"[!] FAILOVER DETECTED: {last_model} → {actual_model}")
                print(f"{'!'*70}\n")

            # Check if we're on fallback
            is_fallback = "llama3" in actual_model.lower() or "ollama" in actual_model.lower()
            status = "FALLBACK" if is_fallback else "PRIMARY"

            print(f"[{timestamp}] Request #{request_count}: ✓ {status}")
            print(f"           Model: {actual_model}")
            print(f"           Response: {(content or '').strip()[:50]}")
            print()

            successful_requests += 1
            last_model = actual_model

        except Exception as e:
            failed_requests += 1
            error_msg = str(e)[:80]
            print(f"[{timestamp}] Request #{request_count}: ✗ FAILED")
            print(f"           Error: {error_msg}")
            print()

        # Wait before next request
        if running:
            time.sleep(REQUEST_INTERVAL)

    print_summary()


if __name__ == "__main__":
    main()
