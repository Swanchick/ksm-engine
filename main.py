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

    return response


@app.route("/api/instance/create", methods=["POST"])
def create_instance():
    if request.method != "POST":
        return ResponseBuilder().status(400).message("Bad request!").build()

    # ToDo:
    # 1. Check if user is admin

    data = request.json
    instance_data = data["instance_data"]
    if not ("name" in instance_data and "instance_type" in instance_data):
        return jsonify(ResponseBuilder().status(500).message("Invalid data!").build())

    return jsonify(ResponseBuilder().status(200).message("Okay").build())


@app.route("/api/user/create", methods=["POST"])
def create_user():
    if request.method != "POST":
        return ResponseBuilder().status(400).message("Bad request!")

    data = request.json

    response = engine.user_create(data)

    return response


if __name__ == "__main__":
    app.run(port=5000)
