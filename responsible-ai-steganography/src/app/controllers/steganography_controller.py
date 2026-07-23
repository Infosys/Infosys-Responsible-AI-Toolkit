"""
# SPDX-License-Identifier: MIT
# Copyright 2024 - 2025 Infosys Ltd.

Steganography Detection Controller
Flask API endpoints for text steganography detection
"""

from flask import Blueprint, request, jsonify, current_app
from flask_restx import Api, Resource, fields, Namespace
import time
import traceback

from app.services.steganography_service import SteganographyDetectionService
from app.models.request_models import SteganographyRequest, BatchSteganographyRequest, BatchTextItem

# Initialize blueprint
steganography_bp = Blueprint("steganography", __name__)
api = Api(
    steganography_bp,
    version="1.0",
    title="Steganography Detection API",
    description="API for detecting text-based steganographic attacks",
)

ns = Namespace("steganography", description="Steganography detection operations")
api.add_namespace(ns, path="/rai/v1/steganography")

# Initialize service
stego_service = SteganographyDetectionService()

# Request/Response models for Swagger documentation
single_request_model = api.model(
    "SingleSteganographyRequest",
    {
        "text": fields.String(required=True, description="Text to analyze for steganography"),
        "user_id": fields.String(description="Optional user identifier"),
        "metadata": fields.Raw(description="Optional metadata object"),
    },
)

batch_text_item_model = api.model(
    "BatchTextItem",
    {
        "text": fields.String(required=True, description="Text content"),
        "id": fields.String(description="Optional item identifier"),
        "metadata": fields.Raw(description="Optional metadata for this item"),
    },
)

batch_request_model = api.model(
    "BatchSteganographyRequest",
    {
        "texts": fields.List(
            fields.Nested(batch_text_item_model), required=True, description="List of texts to analyze"
        ),
        "user_id": fields.String(description="Optional user identifier"),
        "metadata": fields.Raw(description="Optional metadata object"),
    },
)

health_response_model = api.model(
    "HealthResponse",
    {
        "status": fields.String(description="Service health status"),
        "timestamp": fields.String(description="Response timestamp"),
        "version": fields.String(description="API version"),
    },
)

detection_result_model = api.model(
    "DetectionResult",
    {
        "is_suspicious": fields.Boolean(description="Whether steganography was detected"),
        "confidence_score": fields.Float(description="Confidence score (0-100)"),
        "detected_techniques": fields.List(fields.String, description="List of detected techniques"),
        "details": fields.Raw(description="Detailed analysis results"),
        "recommendations": fields.List(fields.String, description="Security recommendations"),
    },
)

single_response_model = api.model(
    "SingleSteganographyResponse",
    {
        "success": fields.Boolean(description="Operation success status"),
        "result": fields.Nested(detection_result_model),
        "processing_time_ms": fields.Float(description="Processing time in milliseconds"),
        "timestamp": fields.String(description="Response timestamp"),
    },
)


@ns.route("/health")
class HealthCheck(Resource):
    @api.doc("health_check")
    @api.marshal_with(health_response_model)
    def get(self):
        """Health check endpoint"""
        try:
            return {
                "status": "healthy",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "version": "1.0.0",
            }
        except Exception as e:
            current_app.logger.error(f"Health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}, 500


@ns.route("/detect")
class SingleDetection(Resource):
    @api.doc("single_text_detection")
    @api.expect(single_request_model)
    @api.marshal_with(single_response_model)
    def post(self):
        """Detect steganography in a single text"""
        start_time = time.time()

        try:
            # Validate request
            if not request.is_json:
                return {"error": "Content-Type must be application/json"}, 400

            data = request.get_json()
            if not data or "text" not in data:
                return {"error": "Missing required field: text"}, 400

            if not isinstance(data["text"], str):
                return {"error": 'Field "text" must be a string'}, 400

            if len(data["text"].strip()) == 0:
                return {"error": "Text cannot be empty"}, 400

            # Process request
            req = SteganographyRequest(
                text=data["text"], user_id=data.get("user_id"), metadata=data.get("metadata", {})
            )

            # Perform detection
            result = stego_service.detect_steganography(req.text)

            processing_time = (time.time() - start_time) * 1000

            return {
                "success": True,
                "result": result,
                "processing_time_ms": round(processing_time, 2),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            }

        except Exception as e:
            current_app.logger.error(f"Error in single detection: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": "Internal server error",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            }, 500


@ns.route("/detect/batch")
class BatchDetection(Resource):
    @api.doc("batch_text_detection")
    @api.expect(batch_request_model)
    def post(self):
        """Detect steganography in multiple texts"""
        start_time = time.time()

        try:
            # Validate request
            if not request.is_json:
                return {"error": "Content-Type must be application/json"}, 400

            data = request.get_json()
            if not data or "texts" not in data:
                return {"error": "Missing required field: texts"}, 400

            if not isinstance(data["texts"], list):
                return {"error": 'Field "texts" must be a list'}, 400

            if len(data["texts"]) == 0:
                return {"error": "At least one text item is required"}, 400

            if len(data["texts"]) > 100:  # Limit batch size
                return {"error": "Maximum batch size is 100 items"}, 400

            # Validate each text item
            text_items = []
            for i, item in enumerate(data["texts"]):
                if not isinstance(item, dict):
                    return {"error": f"Text item {i} must be an object"}, 400

                if "text" not in item:
                    return {"error": f"Text item {i} missing required field: text"}, 400

                if not isinstance(item["text"], str):
                    return {"error": f'Text item {i} field "text" must be a string'}, 400

                if len(item["text"].strip()) == 0:
                    return {"error": f"Text item {i} cannot be empty"}, 400

                text_items.append(
                    BatchTextItem(text=item["text"], id=item.get("id"), metadata=item.get("metadata", {}))
                )

            # Process batch request
            req = BatchSteganographyRequest(
                texts=text_items, user_id=data.get("user_id"), metadata=data.get("metadata", {})
            )

            # Perform detection on each text
            results = []
            for item in req.texts:
                try:
                    detection_result = stego_service.detect_steganography(item.text)
                    results.append({"id": item.id, "success": True, "result": detection_result})
                except Exception as e:
                    current_app.logger.error(f"Error processing text item {item.id}: {str(e)}")
                    results.append({"id": item.id, "success": False, "error": "Processing failed"})

            processing_time = (time.time() - start_time) * 1000

            return {
                "success": True,
                "results": results,
                "total_items": len(results),
                "processing_time_ms": round(processing_time, 2),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            }

        except Exception as e:
            current_app.logger.error(f"Error in batch detection: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": "Internal server error",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            }, 500


@ns.route("/techniques")
class SupportedTechniques(Resource):
    @api.doc("supported_techniques")
    def get(self):
        """Get information about supported steganography detection techniques"""
        try:
            techniques = {
                "zero_width": {
                    "name": "Zero-Width Character Detection",
                    "description": "Detects hidden messages using zero-width Unicode characters",
                    "characters_detected": [
                        "Zero Width Space (U+200B)",
                        "Zero Width Non-Joiner (U+200C)",
                        "Zero Width Joiner (U+200D)",
                        "Word Joiner (U+2060)",
                        "And other invisible Unicode characters",
                    ],
                },
                "whitespace": {
                    "name": "Whitespace Pattern Analysis",
                    "description": "Detects suspicious whitespace patterns and trailing spaces",
                    "detects": [
                        "Excessive trailing spaces",
                        "Unusual spacing patterns",
                        "Systematic whitespace encoding",
                    ],
                },
                "linguistic": {
                    "name": "Linguistic Steganography",
                    "description": "Analyzes linguistic patterns for hidden encoding",
                    "methods": [
                        "First letter frequency analysis",
                        "Capitalization pattern detection",
                        "Entropy analysis",
                    ],
                },
                "frequency": {
                    "name": "Character Frequency Analysis",
                    "description": "Detects anomalous character frequency distributions",
                    "analysis": [
                        "Space frequency deviation",
                        "Vowel frequency analysis",
                        "Non-printable character detection",
                    ],
                },
                "unicode": {
                    "name": "Unicode Exploitation Detection",
                    "description": "Detects malicious use of Unicode features",
                    "detects": ["Suspicious Unicode ranges", "Homograph attacks", "Character substitution"],
                },
            }

            return {"success": True, "techniques": techniques, "total_techniques": len(techniques)}

        except Exception as e:
            current_app.logger.error(f"Error getting techniques info: {str(e)}")
            return {"success": False, "error": "Internal server error"}, 500


# Error handlers
@steganography_bp.errorhandler(400)
def bad_request(error):
    return (
        jsonify(
            {
                "success": False,
                "error": "Bad Request",
                "message": str(error),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            }
        ),
        400,
    )


@steganography_bp.errorhandler(500)
def internal_error(error):
    return (
        jsonify(
            {
                "success": False,
                "error": "Internal Server Error",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            }
        ),
        500,
    )
