from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return """
    <h2>Hash Cracking Lab</h2>
    <p>Bu SHA1 hash'i kır: <b>5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8</b></p>
    """

@app.route("/flag")
def flag():
    return "FLAG{password123}"
