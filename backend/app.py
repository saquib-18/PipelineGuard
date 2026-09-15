# =========================================================
# PIPELINEGUARD v3.0
# MAIN FLASK APPLICATION
# =========================================================

import os
from datetime import datetime

from flask import (
    Flask,
    request,
    jsonify,
    send_file,
    send_from_directory
)

from werkzeug.utils import secure_filename


# =========================================================
# PIPELINE DETECTOR
# =========================================================

from pipeline_detector import detect_pipeline_type


# =========================================================
# PIPELINE VALIDATORS
# =========================================================

from validators.docker_validator import validate_docker
from validators.github_actions_validator import validate_github_actions
from validators.gitlab_validator import validate_gitlab
from validators.jenkins_validator import validate_jenkins
from validators.kubernetes_validator import validate_kubernetes
from validators.security_validator import validate_security
from validators.terraform_validator import validate_terraform
from validators.yaml_validator import validate_yaml


# =========================================================
# REPORT GENERATOR
# =========================================================

from report_generator import generate_pdf


# =========================================================
# HISTORY MANAGER
# =========================================================

from history_manager import (
    add_history,
    get_history,
    get_history_item,
    delete_history_item,
    clear_history,
    get_statistics
)


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# =========================================================
# FOLDERS
# =========================================================

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

REPORT_FOLDER = os.path.join(
    BASE_DIR,
    "reports"
)

FRONTEND_FOLDER = os.path.abspath(
    os.path.join(
        BASE_DIR,
        "..",
        "frontend"
    )
)


# =========================================================
# CREATE REQUIRED FOLDERS
# =========================================================

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    REPORT_FOLDER,
    exist_ok=True
)


# =========================================================
# APPLICATION CONFIGURATION
# =========================================================

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

app.config["MAX_CONTENT_LENGTH"] = (
    5 * 1024 * 1024
)


# =========================================================
# ALLOWED FILE EXTENSIONS
# =========================================================

ALLOWED_EXTENSIONS = {
    "yml",
    "yaml",
    "tf",
    "groovy"
}


# =========================================================
# CHECK ALLOWED FILE
# =========================================================

def allowed_file(filename):

    if not filename:
        return False

    # Jenkinsfile has no extension
    if filename.lower() == "jenkinsfile":
        return True

    if "." not in filename:
        return False

    extension = (
        filename
        .rsplit(".", 1)[1]
        .lower()
    )

    return extension in ALLOWED_EXTENSIONS


# =========================================================
# SAFE INTEGER
# =========================================================

def safe_int(value):

    try:

        return int(
            value or 0
        )

    except (
        TypeError,
        ValueError
    ):

        return 0


# =========================================================
# NORMALIZE PIPELINE RESULT
# =========================================================

def normalize_result(result):

    if not isinstance(
        result,
        dict
    ):

        result = {}


    success = bool(
        result.get(
            "success",
            False
        )
    )


    result.setdefault(
        "success",
        success
    )


    result.setdefault(
        "status",
        (
            "Passed"
            if success
            else "Failed"
        )
    )


    result.setdefault(
        "errors",
        0
    )


    result.setdefault(
        "warnings",
        0
    )


    result.setdefault(
        "issues",
        []
    )


    result.setdefault(
        "recommendations",
        []
    )


    result.setdefault(
        "message",
        "Validation completed."
    )


    return result


# =========================================================
# NORMALIZE SECURITY RESULT
# =========================================================

def normalize_security(result):

    if not isinstance(
        result,
        dict
    ):

        result = {}


    success = bool(
        result.get(
            "success",
            True
        )
    )


    result.setdefault(
        "success",
        success
    )


    result.setdefault(
        "status",
        (
            "Passed"
            if success
            else "Failed"
        )
    )


    result.setdefault(
        "severity",
        "None"
    )


    result.setdefault(
        "errors",
        0
    )


    result.setdefault(
        "warnings",
        0
    )


    result.setdefault(
        "findings",
        []
    )


    result.setdefault(
        "recommendations",
        []
    )


    result.setdefault(
        "message",
        "No security issues detected."
    )


    return result


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    index_file = os.path.join(
        FRONTEND_FOLDER,
        "index.html"
    )


    if os.path.exists(
        index_file
    ):

        return send_from_directory(
            FRONTEND_FOLDER,
            "index.html"
        )


    return jsonify({

        "success":
            True,

        "application":
            "PipelineGuard",

        "version":
            "3.0",

        "message":
            "PipelineGuard backend is running."

    })


# =========================================================
# ANALYTICS PAGE
#
# This fixes:
# /analytics.html
# Endpoint not found
# =========================================================

@app.route("/analytics.html")
def analytics_page():

    analytics_file = os.path.join(
        FRONTEND_FOLDER,
        "analytics.html"
    )


    if os.path.exists(
        analytics_file
    ):

        return send_from_directory(
            FRONTEND_FOLDER,
            "analytics.html"
        )


    return jsonify({

        "success":
            False,

        "message":
            "Analytics page not found."

    }), 404


# =========================================================
# ANALYTICS SHORT URL
#
# Also allows:
# /analytics
# =========================================================

@app.route("/analytics")
def analytics_short_page():

    analytics_file = os.path.join(
        FRONTEND_FOLDER,
        "analytics.html"
    )


    if os.path.exists(
        analytics_file
    ):

        return send_from_directory(
            FRONTEND_FOLDER,
            "analytics.html"
        )


    return jsonify({

        "success":
            False,

        "message":
            "Analytics page not found."

    }), 404


# =========================================================
# FRONTEND CSS
# =========================================================

@app.route(
    "/css/<path:filename>"
)
def frontend_css(filename):

    return send_from_directory(
        os.path.join(
            FRONTEND_FOLDER,
            "css"
        ),
        filename
    )


# =========================================================
# FRONTEND JAVASCRIPT
# =========================================================

@app.route(
    "/js/<path:filename>"
)
def frontend_js(filename):

    return send_from_directory(
        os.path.join(
            FRONTEND_FOLDER,
            "js"
        ),
        filename
    )


# =========================================================
# FRONTEND ASSETS
# =========================================================

@app.route(
    "/assets/<path:filename>"
)
def frontend_assets(filename):

    return send_from_directory(
        os.path.join(
            FRONTEND_FOLDER,
            "assets"
        ),
        filename
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():

    return jsonify({

        "success":
            True,

        "application":
            "PipelineGuard",

        "version":
            "3.0",

        "status":
            "running"

    })


# =========================================================
# API INFORMATION
# =========================================================

@app.route("/api/info")
def api_info():

    return jsonify({

        "application":
            "PipelineGuard",

        "version":
            "3.0",

        "features": {

            "pipeline_detection":
                True,

            "pipeline_validation":
                True,

            "security_analysis":
                True,

            "pdf_reports":
                True,

            "validation_history":
                True,

            "dashboard_statistics":
                True,

            "analytics_page":
                True

        }

    })


# =========================================================
# UPLOAD + VALIDATE PIPELINE
# =========================================================

@app.route(
    "/upload",
    methods=["POST"]
)
def upload_file():

    # -----------------------------------------------------
    # CHECK FILE FIELD
    # -----------------------------------------------------

    if "file" not in request.files:

        return jsonify({

            "success":
                False,

            "overall_success":
                False,

            "message":
                "No file was uploaded."

        }), 400


    uploaded_file = request.files[
        "file"
    ]


    # -----------------------------------------------------
    # CHECK SELECTED FILE
    # -----------------------------------------------------

    if (
        uploaded_file is None
        or
        uploaded_file.filename == ""
    ):

        return jsonify({

            "success":
                False,

            "overall_success":
                False,

            "message":
                "No file selected."

        }), 400


    original_filename = (
        uploaded_file.filename
    )


    # -----------------------------------------------------
    # CHECK FILE TYPE
    # -----------------------------------------------------

    if not allowed_file(
        original_filename
    ):

        return jsonify({

            "success":
                False,

            "overall_success":
                False,

            "message":
                "Unsupported file type. "
                "Supported files are .yml, .yaml, "
                ".tf, .groovy and Jenkinsfile."

        }), 400


    # -----------------------------------------------------
    # CREATE SAFE FILENAME
    # -----------------------------------------------------

    if (
        original_filename.lower()
        ==
        "jenkinsfile"
    ):

        filename = "Jenkinsfile"

    else:

        filename = secure_filename(
            original_filename
        )


    if not filename:

        return jsonify({

            "success":
                False,

            "overall_success":
                False,

            "message":
                "Invalid filename."

        }), 400


    # -----------------------------------------------------
    # SAVE UPLOADED FILE
    # -----------------------------------------------------

    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )


    try:

        uploaded_file.save(
            file_path
        )

    except OSError as error:

        return jsonify({

            "success":
                False,

            "overall_success":
                False,

            "message":
                "Unable to save uploaded file: "
                + str(error)

        }), 500


    # -----------------------------------------------------
    # DETECT PIPELINE TYPE
    # -----------------------------------------------------

    try:

        pipeline_type = detect_pipeline_type(
            file_path,
            original_filename
        )

    except Exception as error:

        return jsonify({

            "success":
                False,

            "overall_success":
                False,

            "message":
                "Pipeline detection failed: "
                + str(error)

        }), 500


    pipeline_key = (
        str(
            pipeline_type
        )
        .strip()
        .lower()
    )


    print(
        "Detected pipeline:",
        pipeline_type
    )


    # -----------------------------------------------------
    # SELECT PIPELINE VALIDATOR
    # -----------------------------------------------------

    try:

        # -------------------------------------------------
        # GITHUB ACTIONS
        # -------------------------------------------------

        if "github" in pipeline_key:

            validation_result = (
                validate_github_actions(
                    file_path
                )
            )


        # -------------------------------------------------
        # GITLAB CI
        # -------------------------------------------------

        elif "gitlab" in pipeline_key:

            validation_result = (
                validate_gitlab(
                    file_path
                )
            )


        # -------------------------------------------------
        # DOCKER COMPOSE
        # -------------------------------------------------

        elif "docker" in pipeline_key:

            validation_result = (
                validate_docker(
                    file_path
                )
            )


        # -------------------------------------------------
        # KUBERNETES
        # -------------------------------------------------

        elif (
            "kubernetes"
            in pipeline_key
            or
            "k8s"
            in pipeline_key
        ):

            validation_result = (
                validate_kubernetes(
                    file_path
                )
            )


        # -------------------------------------------------
        # JENKINS
        # -------------------------------------------------

        elif "jenkins" in pipeline_key:

            validation_result = (
                validate_jenkins(
                    file_path
                )
            )


        # -------------------------------------------------
        # TERRAFORM
        # -------------------------------------------------

        elif "terraform" in pipeline_key:

            validation_result = (
                validate_terraform(
                    file_path
                )
            )


        # -------------------------------------------------
        # GENERIC YAML
        # -------------------------------------------------

        else:

            validation_result = (
                validate_yaml(
                    file_path
                )
            )


    except Exception as error:

        print(
            "Pipeline validation error:",
            error
        )


        validation_result = {

            "success":
                False,

            "status":
                "Failed",

            "errors":
                1,

            "warnings":
                0,

            "issues": [
                str(error)
            ],

            "recommendations": [
                "Check the pipeline configuration."
            ],

            "message":
                "Pipeline validation failed."

        }


    # -----------------------------------------------------
    # NORMALIZE PIPELINE RESULT
    # -----------------------------------------------------

    validation_result = normalize_result(
        validation_result
    )


    # -----------------------------------------------------
    # PIPELINE STATUS
    # -----------------------------------------------------

    pipeline_success = bool(
        validation_result.get(
            "success",
            False
        )
    )


    pipeline_errors = safe_int(
        validation_result.get(
            "errors",
            0
        )
    )


    pipeline_warnings = safe_int(
        validation_result.get(
            "warnings",
            0
        )
    )


    # -----------------------------------------------------
    # SECURITY ANALYSIS
    # -----------------------------------------------------

    try:

        security_result = (
            validate_security(
                file_path
            )
        )

    except Exception as error:

        print(
            "Security validation error:",
            error
        )


        security_result = {

            "success":
                False,

            "status":
                "Failed",

            "severity":
                "High",

            "errors":
                1,

            "warnings":
                0,

            "findings": [
                {
                    "message":
                        str(error)
                }
            ],

            "recommendations": [],

            "message":
                "Security analysis failed."

        }


    # -----------------------------------------------------
    # NORMALIZE SECURITY RESULT
    # -----------------------------------------------------

    security_result = normalize_security(
        security_result
    )


    # -----------------------------------------------------
    # SECURITY STATUS
    # -----------------------------------------------------

    security_success = bool(
        security_result.get(
            "success",
            True
        )
    )


    security_errors = safe_int(
        security_result.get(
            "errors",
            0
        )
    )


    security_warnings = safe_int(
        security_result.get(
            "warnings",
            0
        )
    )


    # -----------------------------------------------------
    # TOTALS
    # -----------------------------------------------------

    total_errors = (
        pipeline_errors
        +
        security_errors
    )


    total_warnings = (
        pipeline_warnings
        +
        security_warnings
    )


    # -----------------------------------------------------
    # OVERALL SUCCESS
    # -----------------------------------------------------

    overall_success = (
        pipeline_success
        and
        security_success
    )


    overall_status = (
        "Passed"
        if overall_success
        else "Failed"
    )


    # -----------------------------------------------------
    # OVERALL MESSAGE
    # -----------------------------------------------------

    if (
        pipeline_success
        and
        security_success
    ):

        overall_message = (
            "Pipeline validation and "
            "security analysis passed."
        )


    elif (
        not pipeline_success
        and
        security_success
    ):

        overall_message = (
            "Pipeline validation failed."
        )


    elif (
        pipeline_success
        and
        not security_success
    ):

        overall_message = (
            "Pipeline validation passed, "
            "but security analysis failed."
        )


    else:

        overall_message = (
            "Pipeline validation and "
            "security analysis failed."
        )


    # -----------------------------------------------------
    # TIMESTAMP
    # -----------------------------------------------------

    timestamp = datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )


    # -----------------------------------------------------
    # CREATE COMPLETE FINAL RESULT
    # -----------------------------------------------------

    result = {

        # FILE INFORMATION

        "filename":
            original_filename,

        "file_type":
            pipeline_type,

        "detected_type":
            validation_result.get(
                "file_type",
                pipeline_type
            ),

        "timestamp":
            timestamp,


        # PIPELINE VALIDATION

        "success":
            pipeline_success,

        "status":
            validation_result.get(
                "status",
                (
                    "Passed"
                    if pipeline_success
                    else "Failed"
                )
            ),

        "errors":
            pipeline_errors,

        "warnings":
            pipeline_warnings,

        "message":
            validation_result.get(
                "message",
                "Validation completed."
            ),

        "issues":
            validation_result.get(
                "issues",
                []
            ),

        "recommendations":
            validation_result.get(
                "recommendations",
                []
            ),


        # SECURITY ANALYSIS

        "security_status":
            security_result.get(
                "status",
                (
                    "Passed"
                    if security_success
                    else "Failed"
                )
            ),

        "security_severity":
            security_result.get(
                "severity",
                "None"
            ),

        "security_errors":
            security_errors,

        "security_warnings":
            security_warnings,

        "security_message":
            security_result.get(
                "message",
                "No security issues detected."
            ),

        "security_findings":
            security_result.get(
                "findings",
                []
            ),

        "security_recommendations":
            security_result.get(
                "recommendations",
                []
            ),


        # TOTALS

        "total_errors":
            total_errors,

        "total_warnings":
            total_warnings,


        # OVERALL

        "overall_success":
            overall_success,

        "overall_status":
            overall_status,

        "overall_message":
            overall_message

    }


    # =====================================================
    # GENERATE PDF REPORT
    # =====================================================

    base_name = os.path.splitext(
        filename
    )[0]


    if not base_name:

        base_name = "pipeline"


    pdf_filename = (
        base_name
        +
        "_report.pdf"
    )


    try:

        generated_report = (
            generate_pdf(
                result,
                pdf_filename
            )
        )


        if isinstance(
            generated_report,
            str
        ):

            returned_name = os.path.basename(
                generated_report
            )


            if returned_name:

                pdf_filename = (
                    returned_name
                )


        result["pdf_file"] = (
            pdf_filename
        )


    except Exception as error:

        print(
            "PDF generation error:",
            error
        )


        result["pdf_file"] = None


    # =====================================================
    # SAVE VALIDATION HISTORY
    # =====================================================

    history_record = {

        "filename":
            original_filename,

        "file_type":
            pipeline_type,

        "detected_type":
            result.get(
                "detected_type",
                pipeline_type
            ),

        "overall_status":
            overall_status,

        "status":
            overall_status,

        "pipeline_status":
            result.get(
                "status",
                (
                    "Passed"
                    if pipeline_success
                    else "Failed"
                )
            ),

        "security_status":
            result.get(
                "security_status",
                "Passed"
            ),

        "security_severity":
            result.get(
                "security_severity",
                "None"
            ),

        "errors":
            total_errors,

        "warnings":
            total_warnings,

        "pipeline_errors":
            pipeline_errors,

        "pipeline_warnings":
            pipeline_warnings,

        "security_errors":
            security_errors,

        "security_warnings":
            security_warnings,

        "total_errors":
            total_errors,

        "total_warnings":
            total_warnings,

        "timestamp":
            timestamp,

        "pdf_file":
            result.get(
                "pdf_file"
            ),

        "issues":
            result.get(
                "issues",
                []
            ),

        "recommendations":
            result.get(
                "recommendations",
                []
            ),

        "security_message":
            result.get(
                "security_message",
                ""
            ),

        "security_findings":
            result.get(
                "security_findings",
                []
            ),

        "security_recommendations":
            result.get(
                "security_recommendations",
                []
            ),

        "message":
            result.get(
                "message",
                ""
            ),

        "overall_message":
            overall_message

    }


    try:

        add_history(
            history_record
        )

    except Exception as error:

        print(
            "History save error:",
            error
        )


    # =====================================================
    # RETURN RESPONSE
    # =====================================================

    return jsonify(
        result
    )


# =========================================================
# GET HISTORY / CLEAR HISTORY
# =========================================================

@app.route(
    "/history",
    methods=[
        "GET",
        "DELETE"
    ]
)
def history():

    try:

        # -------------------------------------------------
        # GET HISTORY
        # -------------------------------------------------

        if request.method == "GET":

            return jsonify(
                get_history()
            )


        # -------------------------------------------------
        # CLEAR ALL HISTORY
        # -------------------------------------------------

        if request.method == "DELETE":

            success = clear_history()


            if success:

                return jsonify({

                    "success":
                        True,

                    "message":
                        "Validation history "
                        "cleared successfully."

                })


            return jsonify({

                "success":
                    False,

                "message":
                    "Unable to clear "
                    "validation history."

            }), 500


    except Exception as error:

        print(
            "History error:",
            error
        )


        return jsonify({

            "success":
                False,

            "message":
                str(error)

        }), 500


# =========================================================
# GET ONE HISTORY RECORD
# =========================================================

@app.route(
    "/history/<int:index>",
    methods=["GET"]
)
def get_history_record(index):

    try:

        record = get_history_item(
            index
        )


        if record is None:

            return jsonify({

                "success":
                    False,

                "message":
                    "History record not found."

            }), 404


        return jsonify({

            "success":
                True,

            "record":
                record

        })


    except Exception as error:

        print(
            "Get history record error:",
            error
        )


        return jsonify({

            "success":
                False,

            "message":
                str(error)

        }), 500


# =========================================================
# DELETE ONE HISTORY RECORD
# =========================================================

@app.route(
    "/history/<int:index>",
    methods=["DELETE"]
)
def delete_history_record(index):

    try:

        success = delete_history_item(
            index
        )


        if not success:

            return jsonify({

                "success":
                    False,

                "message":
                    "History record not found."

            }), 404


        return jsonify({

            "success":
                True,

            "message":
                "History record deleted successfully."

        })


    except Exception as error:

        print(
            "Delete history error:",
            error
        )


        return jsonify({

            "success":
                False,

            "message":
                str(error)

        }), 500


# =========================================================
# DASHBOARD STATISTICS
# =========================================================

@app.route(
    "/statistics",
    methods=["GET"]
)
def statistics():

    try:

        stats = get_statistics()


        return jsonify({

            "success":
                True,

            "statistics":
                stats

        })


    except Exception as error:

        print(
            "Statistics error:",
            error
        )


        return jsonify({

            "success":
                False,

            "message":
                str(error)

        }), 500


# =========================================================
# DOWNLOAD PDF REPORT
# =========================================================

@app.route(
    "/download/<filename>"
)
def download_report(filename):

    safe_name = secure_filename(
        filename
    )


    if not safe_name:

        return jsonify({

            "success":
                False,

            "message":
                "Invalid report filename."

        }), 400


    report_path = os.path.join(
        REPORT_FOLDER,
        safe_name
    )


    if not os.path.exists(
        report_path
    ):

        return jsonify({

            "success":
                False,

            "message":
                "PDF report not found."

        }), 404


    return send_file(
        report_path,
        as_attachment=True
    )


# =========================================================
# FILE TOO LARGE
# =========================================================

@app.errorhandler(413)
def file_too_large(error):

    return jsonify({

        "success":
            False,

        "overall_success":
            False,

        "message":
            "Maximum file size is 5 MB."

    }), 413


# =========================================================
# 404 ERROR
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return jsonify({

        "success":
            False,

        "message":
            "Endpoint not found."

    }), 404


# =========================================================
# 500 ERROR
# =========================================================

@app.errorhandler(500)
def internal_server_error(error):

    return jsonify({

        "success":
            False,

        "message":
            "Internal server error."

    }), 500


# =========================================================
# START PIPELINEGUARD
# =========================================================

if __name__ == "__main__":

    print()

    print("=" * 60)

    print(
        "                 PIPELINEGUARD v3.0"
    )

    print("=" * 60)

    print(
        "Application : http://127.0.0.1:5000"
    )

    print(
        "Analytics   : http://127.0.0.1:5000/analytics.html"
    )

    print(
        "Health      : http://127.0.0.1:5000/health"
    )

    print(
        "History     : http://127.0.0.1:5000/history"
    )

    print(
        "Statistics  : http://127.0.0.1:5000/statistics"
    )

    print(
        "History View: http://127.0.0.1:5000/history/0"
    )

    print("=" * 60)

    print()


    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )