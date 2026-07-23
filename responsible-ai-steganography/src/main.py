"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Main Flask application for Steganography Detection Service
"""

import os
import logging
from flask import Flask
from flask_cors import CORS
from app.controllers.steganography_controller import steganography_bp


def create_app():
    """
    Application factory function
    """
    app = Flask(__name__)

    # Configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    app.config["DEBUG"] = os.getenv("DEBUG", "False").lower() == "true"

    # CORS configuration
    CORS(app, origins=os.getenv("CORS_ORIGINS", "*").split(","))

    # Logging configuration
    if not app.debug:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    # Register blueprints
    app.register_blueprint(steganography_bp)

    # Health check route
    @app.route("/health")
    def health_check():
        return {"status": "healthy", "service": "steganography-detection"}

    # Default route
    @app.route("/")
    def index():
        return {
            "service": "Responsible AI Steganography Detection",
            "version": "1.0.0",
            "endpoints": [
                "/rai/v1/steganography/health",
                "/rai/v1/steganography/detect",
                "/rai/v1/steganography/detect/batch",
                "/rai/v1/steganography/techniques",
                "/rai/v1/steganography/docs",
            ],
        }

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 5001))
    host = os.getenv("HOST", "0.0.0.0")

    print(f"Starting Steganography Detection Service on {host}:{port}")
    print(f"Swagger documentation available at: http://{host}:{port}/rai/v1/steganography/")

    app.run(host=host, port=port, debug=app.config["DEBUG"])
