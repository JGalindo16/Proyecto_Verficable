from flask import Flask, render_template
from app.routes.course_routes import course_bp
from app.routes.professor_routes import professor_bp
from app.routes.student_routes import student_bp
from app.http_errors import HTTP_NOT_FOUND

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    app.register_blueprint(course_bp)
    app.register_blueprint(professor_bp)
    app.register_blueprint(student_bp)

    @app.errorhandler(HTTP_NOT_FOUND)
    def not_found(e):
        return render_template("global/404.html"), HTTP_NOT_FOUND

    return app