from flask import Flask, jsonify, request


app = Flask(__name__)


@app.route("/instance/", methods=["POST"])
def main():
    if not request.method != "POST":
        return "Bad request", 400

    return jsonify({"asd": "asa"}, mimetype="application/json")


if __name__ == "__main__":
    app.run(debug=True)