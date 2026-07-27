from flask import Flask
from app.routes import api_blueprint
def create_app():
    app = Flask(__name__)
    @app.route("/")
    def home():
        return "App is running!"
    app.register_blueprint(api_blueprint)
    return app