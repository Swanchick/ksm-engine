from flask import Flask, request
from engine import Engine
from utils import ResponseBuilder, HttpStatus


engine = Engine()
app = Flask(__name__)


@app.route("/api/instance/call/<method_name>/", methods=["POST"])
async def instance_requests(method_name: str):
    if request.method != "POST":
        return engine.encrypt_data(
            ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad request!").build()
        )

    data = request.json
    response = engine.instance_call(method_name, data)

    return engine.encrypt_data(response)


@app.route("/api/instance/create/", methods=["POST"])
async def create_instance():
    if request.method != "POST":
        return engine.encrypt_data(
            ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad request!").build()
        )

    data = request.json

    response = engine.instance_create(data)

    return engine.encrypt_data(response)


@app.route("/api/instance/get/", methods=["POST"])
async def get_instances():
    if request.method != "POST":
        return engine.encrypt_data(
            ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad request!").build()
        )

    data = request.json
    response = engine.get_instances(data)

    return engine.encrypt_data(response)


@app.route("/api/instance/get_instance/", methods=["POST"])
async def get_instance_data():
    if request.method != "POST":
        return engine.encrypt_data(
            ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad request!").build()
        )

    data = request.json
    response = engine.get_instance(data)

    return engine.encrypt_data(response)


@app.route("/api/instance/types/", methods=["POST"])
async def get_instance_types():
    if request.method != "POST":
        return engine.encrypt_data(
            ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad request!").build()
        )

    data = request.json
    response = engine.get_instance_types(data)
    return engine.encrypt_data(response)


@app.route("/api/user/create/", methods=["POST"])
async def create_user():
    if request.method != "POST":
        return engine.encrypt_data(
            ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad request!").build()
        )

    data = request.json
    response = engine.user_create(data)

    return engine.encrypt_data(response)


@app.route("/api/user/authorization/", methods=["POST"])
async def authorization():
    if request.method != "POST":
        return engine.encrypt_data(
            ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad request!").build()
        )

    data = request.json
    response = engine.authorize_user(data)

    return engine.encrypt_data(response)


@app.route("/api/user/get/", methods=["POST"])
async def get_users():
    if request.method != "POST":
        return engine.encrypt_data(
            ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad request!").build()
        )

    data = request.json
    response = engine.get_users(data)

    return engine.encrypt_data(response)


@app.route("/api/user/get_user/", methods=["POST"])
async def get_user():
    if request.method != "POST":
        return engine.encrypt_data(
            ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad request!").build()
        )

    data = request.json
    response = engine.get_user(data)

    return engine.encrypt_data(response)


@app.route("/api/permission/get/", methods=["POST"])
async def get_permissions():
    if request.method != "POST":
        return engine.encrypt_data(
            ResponseBuilder().status(HttpStatus.HTTP_BAD_REQUEST.value).message("Bad request!").build()
        )

    data = request.json
    response = engine.get_permissions(data)

    return engine.encrypt_data(response)


@app.route("/api/touch_some_grass/")
async def ping():
    return engine.encrypt_data(ResponseBuilder().status(HttpStatus.HTTP_SUCCESS.value).message("Nope").build())


if __name__ == "__main__":
    engine.start(app)
