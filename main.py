from flask import Flask, request, jsonify
from engine.engine import Engine
from utils.init_project import InitProject
from sys import argv


INIT_PROJECT = "--init"

engine = Engine()
app = Flask(__name__)


@app.after_request
async def test(_):
    routes = request.url.split("/")[3:]

    if routes[-1] == "":
        routes.pop(-1)

    data = request.json
    response = engine.request(routes, data)

    return jsonify(response)


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
