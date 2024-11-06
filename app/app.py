# app.py
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import ollama
import markdown
import logging

app = Flask(__name__, 
    static_url_path='',
    static_folder='static',
    template_folder='templates'
)
logging.basicConfig(level=logging.DEBUG)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True)

LLAMA_MODEL = "llama3.1:8b"

system_message = {
    "role": "system",
    "content": """You are a hearing doctor (Dr. Hear) participating in an outreach activity explaining hearing loss
    and auditory neuroscience to the public. Be positive and relatively short in the responses, but not too concise.
    If you are unsure do not invent answers, just say that you do not know. Target a young audience, 15-30 years old.
    If asked to give medical advice, say that you are not a real doctor and that the person should consult a healthcare professional."""
}

@app.route('/')
def home():
    app.logger.info("Loading index page")
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    app.logger.debug("Client connected")
    emit('response_chunk', {
        'chunk': "Hello! I'm Dr. Hear, a specialist in hearing and auditory science. How can I help you today?",
        'is_complete': True
    })

@socketio.on('send_message')
def handle_message(data):
    try:
        message = data['message']
        accumulated_response = ""
        
        # Include system message in context
        prompt = f"{system_message['content']}\n\nUser: {message}\nBot:"
        
        for chunk in ollama.generate(
            model=LLAMA_MODEL,
            prompt=prompt,
            stream=True
        ):
            accumulated_response += chunk['response']
            emit('response_chunk', {
                'chunk': markdown.markdown(accumulated_response),
                'is_complete': False
            })
        
        emit('response_chunk', {
            'chunk': markdown.markdown(accumulated_response),
            'is_complete': True
        })
    except Exception as e:
        app.logger.error(f"Error handling message: {e}")
        emit('error', {'error': str(e)})

if __name__ == '__main__':
    app.logger.info("Starting server...")
    socketio.run(app, debug=True, port=5000)