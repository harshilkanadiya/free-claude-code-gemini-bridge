import os
import json
import uvicorn
import time
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from google import genai
from google.genai import types

# Load configuration
try:
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r") as f:
        config = json.load(f)
except FileNotFoundError:
    print("ERROR: config.json not found.")
    exit(1)

client = genai.Client(api_key=config.get("api_key"))
app = FastAPI()

def extract_text(content):
    """THE METADATA FILTER: Converts complex Anthropic blocks into plain strings."""
    if not content: return ""
    if isinstance(content, str): return content
    if isinstance(content, list):
        # Join only the text parts, ignoring 'cache_control' or 'ephemeral' dicts
        return "".join([c.get("text", "") for c in content if isinstance(c, dict) and "text" in c])
    if isinstance(content, dict):
        return content.get("text", "")
    return str(content)

def translate_messages(messages):
    contents = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        text = extract_text(m["content"])
        contents.append({"role": role, "parts": [{"text": text}]})
    return contents

@app.api_route("/{path:path}", methods=["GET", "POST", "HEAD", "OPTIONS"])
async def proxy(request: Request, path: str):
    if request.method != "POST":
        return {"status": "ok"}

    body = await request.json()
    
    # CRITICAL FIX: Flatten the system prompt to a plain string
    system_prompt = extract_text(body.get("system", ""))
    messages = translate_messages(body.get("messages", []))
    
    print(f"\n[CALL] Claude is thinking...")

    async def generate():
        msg_id = f"msg_{int(time.time())}"
        
        yield f"event: message_start\ndata: {json.dumps({'type': 'message_start', 'message': {'id': msg_id, 'type': 'message', 'role': 'assistant', 'content': [], 'model': 'claude-3-5-sonnet-20241022', 'stop_reason': None, 'stop_sequence': None, 'usage': {'input_tokens': 0, 'output_tokens': 0}}})}\n\n"
        yield f"event: content_block_start\ndata: {json.dumps({'type': 'content_block_start', 'index': 0, 'content_block': {'type': 'text', 'text': ''}})}\n\n"

        try:
            response = client.models.generate_content_stream(
                model=config.get("model", "gemini-flash-lite-latest"),
                contents=messages,
                config=types.GenerateContentConfig(system_instruction=system_prompt)
            )

            for chunk in response:
                if chunk.text:
                    data = {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": chunk.text}}
                    yield f"event: content_block_delta\ndata: {json.dumps(data)}\n\n"
            
            yield f"event: content_block_stop\ndata: {json.dumps({'type': 'content_block_stop', 'index': 0})}\n\n"
            yield f"event: message_delta\ndata: {json.dumps({'type': 'message_delta', 'delta': {'stop_reason': 'end_turn', 'stop_sequence': None}, 'usage': {'output_tokens': 0}})}\n\n"
            yield f"event: message_stop\ndata: {json.dumps({'type': 'message_stop'})}\n\n"
            print("[DONE] Delivered.")
        except Exception as e:
            print(f"[ERROR] {e}")
            yield f"event: error\ndata: {json.dumps({'type': 'error', 'error': {'type': 'api_error', 'message': str(e)}})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"anthropic-version": "2023-06-01", "Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=config.get("port", 8000), log_level="warning")