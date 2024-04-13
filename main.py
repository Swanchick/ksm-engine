from flask import Flask, jsonify, request
from server import InstanceManager


instance_manager = InstanceManager()
instance_manager.start()
instance_manager.load_instances()

app = Flask(__name__)


@app.route("/api/instance/call/<method_name>", methods=["POST"])
def instance_requests(method_name: str):
    if request.method != "POST":
        return "Bad request", 400

    data = request.json
    output_data = instance_manager.request(method_name, data["instance_data"])

    return jsonify(output_data)


@app.route("/api/instance/create", methods=["POST"])
def create_instance():
    if request.method != "POST":
        return "Bad request", 400

    # ToDo:
    # 1. Check if user is admin

    data = request.json
    instance_data = data["instance_data"]
    if not ("name" in instance_data and "instance_type" in instance_data):
        return "Bad request", 400

    instance_manager.create_instance(instance_data["name"], instance_data["instance_type"])

    return jsonify({"status": 200})


if __name__ == "__main__":
    app.run(port=5000)
