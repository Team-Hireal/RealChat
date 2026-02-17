"""
RealChat — Authentication module
JWT-based auth with SQLite/Postgres user storage
"""

import os
import uuid
import logging
from datetime import datetime, timezone, timedelta

import bcrypt
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from sqlalchemy import create_engine, Column, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

logger = logging.getLogger(__name__)

Base = declarative_base()


# ── User model ──────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=True)
    api_token = Column(String(64), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "api_token": self.api_token,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ── Database setup ──────────────────────────────────────────

db_session = None
engine = None


def init_db(app):
    """Initialize database and create tables."""
    global db_session, engine

    db_url = os.getenv("DATABASE_URL", "sqlite:///realchat.db")
    # Railway Postgres uses postgres:// but SQLAlchemy needs postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    engine = create_engine(db_url, echo=False)
    session_factory = sessionmaker(bind=engine)
    db_session = scoped_session(session_factory)

    Base.metadata.create_all(engine)
    logger.info(f"Auth database initialized ({db_url.split('://')[0]})")

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if db_session:
            db_session.remove()


# ── JWT setup ───────────────────────────────────────────────

jwt = JWTManager()


def init_auth(app):
    """Initialize JWT and auth blueprint on the Flask app."""
    app.config["JWT_SECRET_KEY"] = app.config.get(
        "SECRET_KEY", "change-me-in-production"
    )
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

    jwt.init_app(app)
    init_db(app)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    logger.info("Auth system initialized")


# ── Auth blueprint ──────────────────────────────────────────

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    name = data.get("name", "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if db_session.query(User).filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(email=email, name=name or None, api_token=uuid.uuid4().hex)
    user.set_password(password)
    db_session.add(user)
    db_session.commit()

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    logger.info(f"New user registered: {email}")
    return jsonify({
        "user": user.to_dict(),
        "access_token": access_token,
        "refresh_token": refresh_token,
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = db_session.query(User).filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        "user": user.to_dict(),
        "access_token": access_token,
        "refresh_token": refresh_token,
    })


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = db_session.query(User).get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()})


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify({"access_token": access_token})
