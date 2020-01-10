import os
from flask import *

app = Flask(__name__)

@app.route('/')
def hello_world():
    return jsonify({"hoge": 2})

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))