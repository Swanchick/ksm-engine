from flask import Flask


app = Flask(__name__)


@app.route("/")
def main():
    print("Client has connected to the main page")

    return "<h1>Hello from test_web2</h1>"


@app.route("/test")
def test():
    print("Client has connected to the test page")

    return "<h1>Test page from test_web2</h1>"


@app.route("/hello")
def hello():
    print("Client has connected to the hello page")

    return "<h1>HELLO</h1>"


if __name__ == "__main__":
    app.run(port=50001)
