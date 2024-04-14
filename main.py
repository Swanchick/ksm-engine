from flask import Flask, jsonify, request
from engine import Engine
from utils import ResponseBuilder


engine = Engine()
app = Flask(__name__)


@app.route("/api/instance/call/<method_name>", methods=["POST"])
def instance_requests(method_name: str):
    if request.method != "POST":
        return ResponseBuilder().status(400).message("Bad request!").build()

    data = request.json
    response = engine.instance_call(method_name, data)

    return jsonify(response)


@app.route("/api/instance/create", methods=["POST"])
def create_instance():
    if request.method != "POST":
        return ResponseBuilder().status(400).message("Bad request!").build()

    data = request.json

    response = engine.instance_create(data)

    return jsonify(response)


@app.route("/api/user/create", methods=["POST"])
def create_user():
    if request.method != "POST":
        return ResponseBuilder().status(400).message("Bad request!")

    data = request.json

    response = engine.user_create(data)

    return jsonify(response)


if __name__ == "__main__":
    app.run(port=5000)
