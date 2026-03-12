"""
Grok Image Proxy — GET-to-POST bridge for grok2api image generation.
Accepts: GET /generate/<prompt>?width=1024&height=1024
Returns: the generated image (JPEG)

Usage in HTML/CSS:
  <img src="http://localhost:8002/generate/a_cat_in_space_floating_among_stars">
  
Underscores in the prompt are converted to spaces.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
import json
import os
import sys

# Where grok2api is running
GROK2API_URL = os.environ.get("GROK2API_URL", "http://grok2api:8001")
PROXY_PORT = int(os.environ.get("PROXY_PORT", "8002"))

# Try to import requests; if not available, use urllib
try:
    import requests
    USE_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    USE_REQUESTS = False


def fetch_image_url(prompt, width=1024, height=1024):
    """Call grok2api /v1/images/generations and return the image URL."""
    size = f"{width}x{height}"
    payload = {
        "model": "grok-imagine-1.0",
        "prompt": prompt,
        "n": 1,
        "size": size,
        "response_format": "url"
    }
    url = f"{GROK2API_URL}/v1/images/generations"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(payload).encode("utf-8")

    if USE_REQUESTS:
        resp = requests.post(url, json=payload, timeout=120)
        data = resp.json()
    else:
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))

    # Response can be either:
    # 1. Standard OpenAI format: data.data[0].url
    # 2. Chat completion format: choices[0].message.content
    if "data" in data and len(data["data"]) > 0:
        return data["data"][0].get("url", "")
    elif "choices" in data and len(data["choices"]) > 0:
        return data["choices"][0]["message"]["content"]
    return ""


def fetch_raw_image(image_path):
    """Fetch the actual image bytes from grok2api."""
    if image_path.startswith("http"):
        img_url = image_path
    else:
        img_url = f"{GROK2API_URL}{image_path}"

    if USE_REQUESTS:
        resp = requests.get(img_url, timeout=60)
        return resp.content, resp.headers.get("Content-Type", "image/jpeg")
    else:
        req = urllib.request.Request(img_url, method="GET")
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read(), resp.headers.get("Content-Type", "image/jpeg")


class ImageProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        # Health check
        if path == "/" or path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Grok Image Proxy OK")
            return

        # Route: /generate/<prompt>
        if path.startswith("/generate/"):
            raw_prompt = path[len("/generate/"):]
            # Replace underscores with spaces
            prompt = raw_prompt.replace("_", " ")

            # Parse query params for size
            params = parse_qs(parsed.query)
            width = int(params.get("width", ["1024"])[0])
            height = int(params.get("height", ["1024"])[0])

            try:
                print(f"[Proxy] Generating: {prompt[:80]}... ({width}x{height})")
                image_url = fetch_image_url(prompt, width, height)
                if not image_url:
                    raise Exception("Empty image URL from grok2api")

                print(f"[Proxy] Got URL: {image_url}")
                img_bytes, content_type = fetch_raw_image(image_url)

                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(img_bytes)))
                self.send_header("Cache-Control", "public, max-age=86400")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(img_bytes)
                print(f"[Proxy] Served {len(img_bytes)} bytes")

            except Exception as e:
                print(f"[Proxy] Error: {e}", file=sys.stderr)
                self.send_response(500)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(f"Error generating image: {e}".encode())
            return

        # 404 for everything else
        self.send_response(404)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Not found. Use /generate/<prompt>")

    def log_message(self, format, *args):
        print(f"[Proxy] {args[0]}")


if __name__ == "__main__":
    print(f"[Proxy] Starting on port {PROXY_PORT}")
    print(f"[Proxy] Grok2API URL: {GROK2API_URL}")
    print(f"[Proxy] Usage: http://localhost:{PROXY_PORT}/generate/your_prompt_with_underscores")
    server = HTTPServer(("0.0.0.0", PROXY_PORT), ImageProxyHandler)
    server.serve_forever()
