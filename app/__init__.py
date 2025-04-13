from flask import Flask
from app.routes.course_routes import course_bp
from app.http_errors import HTTP_NOT_FOUND

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    app.register_blueprint(course_bp)

    @app.errorhandler(HTTP_NOT_FOUND)
    def not_found(e):
        return "Página no encontrada", 404

    return app