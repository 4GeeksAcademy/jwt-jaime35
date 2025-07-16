import os
from datetime import timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

from flask_swagger import swagger

from api.utils import APIException, generate_sitemap
from api.models import db, TokenBlocklist
from api.routes import api
from api.admin import setup_admin
from api.commands import setup_commands

# Detect environment
ENV = "development" if os.getenv("FLASK_DEBUG") == "1" else "production"

# Static files directory (frontend)
static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../public')

# Create Flask app
app = Flask(__name__)
app.url_map.strict_slashes = False

# Enable CORS
CORS(app, origins="*", supports_credentials=True)

# Database setup
db_url = os.getenv("DATABASE_URL")
if db_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# JWT configuration
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
app.config["JWT_SECRET_KEY"] = os.getenv("FLASK_APP_KEY", "super-secret")

# Initialize extensions
db.init_app(app)
Migrate(app, db, compare_type=True)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(api, url_prefix='/api')

# Setup admin and CLI commands
setup_admin(app)
setup_commands(app)

# Token blocklist check
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return TokenBlocklist.query.filter_by(jti=jti).first() is not None

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "error": "Token revoked",
        "message": "Please log in again"
    }), 401

# Error handler
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Sitemap (only in dev)
@app.route('/')
def sitemap():
    if ENV == "development":
        return generate_sitemap(app)
    return send_from_directory(static_file_dir, 'index.html')

# Serve static frontend files
@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    full_path = os.path.join(static_file_dir, path)
    if not os.path.isfile(full_path):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0
    return response

# Entry point
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)