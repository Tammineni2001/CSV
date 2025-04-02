from flask import Blueprint, request, jsonify
from main import generate_kpis

kpi_blueprint = Blueprint("kpi_blueprint", __name__)

@kpi_blueprint.route("/generate-kpis", methods=["POST"])
def generate_kpis_endpoint():
    data = request.json
    file_path = data.get("file_path")
    if not file_path:
        return jsonify({"error": "File path is required"}), 400
    response = generate_kpis(file_path)
    return jsonify({"response": response})
