# app.py
from flask import Flask

# Import cả hai blueprint
from rules.naming import good_bp
from rules.naming import bad_bp

app = Flask(__name__)

app.register_blueprint(good_bp, url_prefix='/good')

app.register_blueprint(bad_bp, url_prefix='/bad')

@app.route('/')
def index():
    return """
    <h1>API Naming Convention Demo</h1>
    <p>Try accessing endpoints under /good/ and /bad/ prefixes to compare.</p>
    <p><b>Good Example:</b> <a href="/good/v1/users">/good/v1/users</a></p>
    <p><b>Bad Example:</b> <a href="/bad/v1/getAllUsers">/bad/v1/getAllUsers</a></p>
    """

if __name__ == '__main__':
    app.run(debug=True)