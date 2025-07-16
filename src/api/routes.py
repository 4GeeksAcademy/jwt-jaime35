from flask import request, jsonify, Blueprint
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    create_access_token, jwt_required,
    get_jwt_identity, get_jwt
)
from flask_cors import cross_origin

from api.models import db, User, TokenBlocklist

api = Blueprint('api', __name__)
bcrypt = Bcrypt()

# 🔐 Registro
@api.route('/signup', methods=['POST', 'OPTIONS'])
@cross_origin()
def signup():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.get_json()
    if data is None:
        return jsonify({"error": "Missing data"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    if "@" not in email:
        return jsonify({"error": "Invalid email format"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password=hashed_password, is_active=True)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created", "user": new_user.serialize()}), 201

# 🔐 Login
@api.route('/login', methods=['POST'])
@cross_origin()
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"msg": "Invalid email or password"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        "token": access_token,
        "user_id": user.id,
        "email": user.email
    }), 200

# 🔐 Obtener perfil
@api.route("/profile", methods=["GET"])
@jwt_required()
@cross_origin()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify({"user": user.serialize()}), 200

# 🔐 Logout
@api.route("/logout", methods=["POST"])
@jwt_required()
@cross_origin()
def logout():
    jti = get_jwt()["jti"]
    db.session.add(TokenBlocklist(jti=jti))
    db.session.commit()
    return jsonify(msg="Logged out successfully"), 200

# 🔐 Hello
@api.route('/hello', methods=['GET'])
@cross_origin()
def hello():
    return jsonify({"message": "Hello! I'm a message from the backend."}), 200
