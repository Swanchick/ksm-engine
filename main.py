from flask import Flask, request, jsonify, Response
from engine.engine import Engine
from utils.init_project import InitProject
from utils.response_builder import ResponseBuilder
from utils.http_status import HttpStatus
from sys import argv


INIT_PROJECT = "--init"

engine = Engine()
app = Flask(__name__)

API_ROUTE = "api"


@app.after_request
async def get_all_requests(_):
    routes = request.url.split("/")[3:]
    if routes[0] != API_ROUTE:
        response = ResponseBuilder().status(HttpStatus.HTTP_NOT_FOUND.value).message("Not found!").build()

        flask_response = Response(
            response=engine.encrypt_data(response),
            status=200,
            mimetype="application/json"
        )

        return flask_response

    if routes[-1] == "":
        routes.pop(-1)

    data = request.json
    response = engine.request(routes[1:], data)

    json = engine.encrypt_data(response)

    flask_response = Response(
        response=json,
        status=200,
        mimetype="application/json"
    )

    return flask_response


def main():
    if INIT_PROJECT in argv:
        init_project = InitProject(engine.user_manager)
        init_project.start()

        return

    if engine.debug:
        app.run(port=engine.port)

        return

    engine.start(app)


if __name__ == "__main__":
    main()
