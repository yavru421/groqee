from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import json
import subprocess
from evolution_log import log_evolution

PROMPT_TUNER_FILE = 'jdss_prompt_tuner.json'

app = Flask(__name__, static_folder='static')
CORS(app)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    api_key = data.get('api_key')
    user_message = data.get('message')
    context = data.get('context', '')
    if not api_key or not user_message:
        return jsonify({'error': 'API key and message are required.'}), 400
    # Use a system prompt to instruct Groqee about its identity and creator
    system_prompt = (
        "You are Groqee, an AI assistant created by John Daniel Dondlinger. "
        "You are designed to be ultra-fast, lightweight, and highly adaptable. "
        "Your purpose is to assist users with their queries, evolve based on context, and provide insightful responses. "
        "Always maintain a professional yet approachable tone, and reflect the vision of your creator in your interactions."
    )

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload)
        resp.raise_for_status()
        result = resp.json()
        answer = result['choices'][0]['message']['content']
        return jsonify({'response': answer})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/context-evolve', methods=['POST'])
def context_evolve():
    data = request.json
    api_key = data.get('api_key')
    context = data.get('context', '')
    if not api_key or not context:
        return jsonify({'error': 'API key and context are required.'}), 400
    # Use a system prompt to instruct Groqee to analyze and evolve the context
    system_prompt = (
        "You are Groqee, an AI assistant that evolves its system prompt and behavior based on user-provided context. "
        "Analyze the following context and generate an improved, evolved system prompt that will help you better assist the user. "
        "Be concise, clear, and creative.\n\nContext:\n" + context
    )
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Evolve your system prompt based on the above context and return only the new system prompt."}
        ]
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload)
        resp.raise_for_status()
        result = resp.json()
        evolved_prompt = result['choices'][0]['message']['content']
        # Save both the original system prompt and evolved prompt
        with open(PROMPT_TUNER_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'original_prompt': system_prompt,
                'evolved_prompt': evolved_prompt
            }, f, ensure_ascii=False, indent=2)
        # Log the evolution event
        log_evolution(f"Context evolved. New prompt: {evolved_prompt}")
        return jsonify({'evolved_prompt': evolved_prompt})
    except requests.exceptions.HTTPError as http_err:
        if resp.status_code == 401:
            return jsonify({'error': 'Invalid API key. Please check your API key and try again.'}), 401
        return jsonify({'error': f'HTTP error occurred: {http_err}'}), resp.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/list-folder', methods=['POST'])
def list_folder():
    data = request.json
    folder_path = data.get('folder_path')
    if not folder_path:
        return jsonify({'error': 'Folder path is required.'}), 400
    try:
        # Use PowerShell to list folder contents
        command = f'powershell -Command "Get-ChildItem -Path \"{folder_path}\" | Format-Table -AutoSize"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({'error': result.stderr.strip()}), 500
        return jsonify({'output': result.stdout.strip()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

app.add_url_rule('/static/sw.js', 'service_worker', lambda: send_from_directory(app.static_folder, 'sw.js'))

def self_check():
    checks = []
    # Check for required files
    required_files = [
        'static/index.html',
        'static/manifest.json',
        'static/groqee_fox/image(5).jpg',
        'static/groqee_fox/tmp76eb0vsr.svg',
        'evolution_log.py',
        'jdss.json'
    ]
    for f in required_files:
        if not os.path.exists(f):
            checks.append(f"Missing required file: {f}")
    # Check for required packages
    try:
        import flask
        import flask_cors
        import requests
    except ImportError as e:
        checks.append(f"Missing required package: {e}")
    # Check API key (try a dry run to Groq API)
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        checks.append("GROQ_API_KEY environment variable not set.")
    else:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": "ping"}]}
        try:
            resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=10)
            if resp.status_code == 401:
                checks.append("Groq API key is invalid or unauthorized.")
            elif resp.status_code != 200:
                checks.append(f"Groq API returned status {resp.status_code}: {resp.text}")
        except Exception as e:
            checks.append(f"Groq API connection failed: {e}")
    # Check logging
    try:
        from evolution_log import log_evolution
        log_evolution("Groqee self-check log test.")
    except Exception as e:
        checks.append(f"Evolution log failed: {e}")
    # Check folder listing (PowerShell)
    try:
        command = f'powershell -Command "Get-ChildItem -Path . | Format-Table -AutoSize"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            checks.append(f"PowerShell folder listing failed: {result.stderr.strip()}")
    except Exception as e:
        checks.append(f"PowerShell folder listing exception: {e}")
    return checks

if __name__ == '__main__':
    errors = self_check()
    if errors:
        print("\nGroqee self-check failed! The following issues were found:")
        for err in errors:
            print(f"- {err}")
        print("\nGroqee will not start until all issues are resolved.")
        exit(1)
    print("Groqee self-check passed. Starting server...")
    app.run(debug=True)