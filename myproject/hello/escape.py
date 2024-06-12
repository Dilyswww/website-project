from markupsafe import escape
from flask import Flask

app = Flask(__name__)
@app.route("/name")
def hello_name(name):
    return f"Hello, {escape(name)}!"