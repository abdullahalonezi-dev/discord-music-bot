from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def health_check():
    return "🎵 Discord Music Bot is running! ✅", 200

@app.route('/health')
def health():
    return {"status": "healthy", "bot": "Discord Music Bot"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
