from flask import Blueprint, Response

learn_bp = Blueprint('learn', __name__)

LEARN_MARKDOWN = '''
# ICI Chat: Lessons Learned & Deployment Nuggets

## SSL & HTTPS for Local Dev
- Many browser APIs (like screenshot capture) require HTTPS, even for localhost.
- Use Flask's SSL support with self-signed certs for local testing.
- Automate cert generation with OpenSSL in your launcher script.
- If OpenSSL is missing, fail fast and print a clear error.

## OpenSSL on Windows
- Download from [slproweb.com](https://slproweb.com/products/Win32OpenSSL.html)
- Add the `bin` directory to your PATH so Python can find `openssl.exe`.

## Cloud Run Deployment
- Use a `Dockerfile` based on `python:3.9-slim`.
- Expose port 8080 and use HTTPS (Cloud Run handles certs).
- For LLMs, use small models (DistilGPT2, quantized Llama) to fit memory/CPU limits.
- Cold starts can be slow if loading models—consider using a health check endpoint.

## AI Chat & Memory
- Small LLMs are limited: use prompt engineering, repetition penalty, and post-processing to improve output.
- For best results, use OpenAI/Gemini API or a larger local model if resources allow.
- Store user memories and include them in the prompt for context.
- For screenshots, use OCR to extract text and store as memory.

## Admin & Wallets
- Admin UI allows wallet creation and management.
- Use `/client/new-wallet` endpoint for new crypto addresses.

---

_Last updated: May 25, 2025_
'''

@learn_bp.route('/learn')
def learn():
    return Response(LEARN_MARKDOWN, mimetype='text/markdown')
