from flask import Flask, render_template
from config import Config
from models import init_db
from routes.patient_routes import patient_bp
from routes.admin_routes import admin_bp
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(admin_bp,   url_prefix='/admin')

    @app.route('/')
    def home():
        return render_template('index.html')

    init_db()
    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)