from flask import Flask, send_from_directory, request, jsonify, send_file
import os

from validators.yaml_validator import validate_yaml
from validators.jenkins_validator import validate_jenkins
from validators.docker_validator import validate_docker
from validators.kubernetes_validator import validate_kubernetes
from validators.terraform_validator import validate_terraform
from validators.security_validator import validate_security

from report_generator import generate_pdf

app = Flask(
    __name__,
    static_folder="../frontend",
    static_url_path=""
)

UPLOAD_FOLDER = "../uploads"
REPORT_FOLDER = "reports"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)


# ---------------- Home ---------------- #

@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


# ---------------- Health ---------------- #

@app.route("/health")
def health():
    return {
        "status": "Running",
        "project": "PipelineGuard",
        "version": "2.0"
    }


# ---------------- Upload ---------------- #

@app.route("/upload", methods=["POST"])
def upload_file():

    if "file" not in request.files:
        return jsonify({
            "success": False,
            "message": "No file selected."
        })

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "success": False,
            "message": "Filename is empty."
        })

    allowed_extensions = [".yml", ".yaml", ".tf"]

    if not (
        file.filename.endswith(tuple(allowed_extensions))
        or file.filename == "Jenkinsfile"
    ):
        return jsonify({
            "success": False,
            "message": "Only .yml, .yaml, .tf and Jenkinsfile are supported."
        })

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    filename = file.filename.lower()

    # Select Validator
    if file.filename == "Jenkinsfile":
        result = validate_jenkins(filepath)

    elif filename == "docker-compose.yml":
        result = validate_docker(filepath)

    elif "kubernetes" in filename or "k8s" in filename:
        result = validate_kubernetes(filepath)

    elif filename.endswith(".tf"):
        result = validate_terraform(filepath)

    else:
        result = validate_yaml(filepath)

    # Security Scan
    security_result = validate_security(filepath)

    result["security_status"] = security_result.get("status")
    result["security_severity"] = security_result.get("severity")
    result["security_message"] = security_result.get("message")

    # Generate PDF
    if "." in file.filename:
        pdf_name = file.filename.rsplit(".", 1)[0] + "_report.pdf"
    else:
        pdf_name = file.filename + "_report.pdf"

    generate_pdf(result, pdf_name)

    # Send PDF filename to frontend
    result["pdf_file"] = pdf_name

    return jsonify(result)


# ---------------- Download PDF ---------------- #

@app.route("/download/<filename>")
def download_report(filename):

    pdf_path = os.path.join(REPORT_FOLDER, filename)

    if os.path.exists(pdf_path):
        return send_file(
            pdf_path,
            as_attachment=True
        )

    return jsonify({
        "success": False,
        "message": "Report not found."
    }), 404


# ---------------- Run ---------------- #

if __name__ == "__main__":
    app.run(debug=True)