from flask import Flask, jsonify, request
from server import InstanceManager


instance_manager = InstanceManager()
instance_manager.start()
instance_manager.load_instances()

app = Flask(__name__)


@app.route("/instance/<method_name>", methods=["POST"])
def instance_requests(method_name: str):
    if request.method != "POST":
        return "Bad request", 400

    data = request.json
    output_data = instance_manager.request(method_name, data["instance_data"])

    return jsonify(output_data)


if __name__ == "__main__":
    app.run(port=5000)
