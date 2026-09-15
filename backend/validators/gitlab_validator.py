from datetime import datetime
import yaml


# GitLab reserved top-level keywords
RESERVED_KEYS = {
    "stages",
    "variables",
    "workflow",
    "default",
    "include",
    "image",
    "services",
    "before_script",
    "after_script",
    "cache"
}


def validate_gitlab(file_path):

    errors = []
    warnings = []
    recommendations = []

    try:

        with open(file_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        # =====================================================
        # EMPTY FILE
        # =====================================================

        if data is None:

            errors.append(
                "GitLab CI configuration is empty."
            )

            return build_result(
                errors,
                warnings,
                recommendations
            )

        if not isinstance(data, dict):

            errors.append(
                "GitLab CI configuration must be a YAML mapping."
            )

            return build_result(
                errors,
                warnings,
                recommendations
            )

        # =====================================================
        # STAGES
        # =====================================================

        stages = data.get("stages")

        if stages is None:

            warnings.append(
                "GitLab pipeline does not explicitly define stages."
            )

            recommendations.append(
                "Define stages to make pipeline execution order clear."
            )

        elif not isinstance(stages, list):

            errors.append(
                "'stages' must be a YAML list."
            )

        elif len(stages) == 0:

            errors.append(
                "The stages section is empty."
            )

        # =====================================================
        # FIND JOBS
        # =====================================================

        jobs = {}

        for key, value in data.items():

            if key in RESERVED_KEYS:
                continue

            # Hidden GitLab templates begin with "."
            if str(key).startswith("."):
                continue

            if isinstance(value, dict):
                jobs[key] = value

        if len(jobs) == 0:

            errors.append(
                "GitLab CI configuration does not define any jobs."
            )

            recommendations.append(
                "Add at least one GitLab CI job."
            )

            return build_result(
                errors,
                warnings,
                recommendations
            )

        # =====================================================
        # CHECK JOBS
        # =====================================================

        for job_name, job in jobs.items():

            # -------------------------------------------------
            # SCRIPT
            # -------------------------------------------------

            if (
                "script" not in job
                and "trigger" not in job
            ):

                errors.append(
                    f"Job '{job_name}' does not define script or trigger."
                )

                recommendations.append(
                    f"Add a script to GitLab job '{job_name}'."
                )

            script = job.get("script")

            if script is not None and not isinstance(
                script,
                (str, list)
            ):

                errors.append(
                    f"Job '{job_name}' has an invalid script configuration."
                )

            # -------------------------------------------------
            # STAGE
            # -------------------------------------------------

            job_stage = job.get("stage")

            if job_stage and isinstance(stages, list):

                if job_stage not in stages:

                    errors.append(
                        f"Job '{job_name}' uses undefined stage '{job_stage}'."
                    )

                    recommendations.append(
                        f"Add '{job_stage}' to stages or change the stage used by '{job_name}'."
                    )

            # -------------------------------------------------
            # ALLOW FAILURE
            # -------------------------------------------------

            if job.get("allow_failure") is True:

                warnings.append(
                    f"Job '{job_name}' allows failure."
                )

                recommendations.append(
                    f"Confirm that failures in job '{job_name}' should not fail the pipeline."
                )

            # -------------------------------------------------
            # RETRY
            # -------------------------------------------------

            if "retry" not in job:

                warnings.append(
                    f"Job '{job_name}' does not define retry handling."
                )

                recommendations.append(
                    f"Consider retry for temporary failures in job '{job_name}'."
                )

            # -------------------------------------------------
            # TIMEOUT
            # -------------------------------------------------

            if "timeout" not in job:

                warnings.append(
                    f"Job '{job_name}' does not define a timeout."
                )

                recommendations.append(
                    f"Consider configuring a timeout for job '{job_name}'."
                )

        # =====================================================
        # TEST STAGE
        # =====================================================

        if isinstance(stages, list):

            if not any(
                str(stage).lower() == "test"
                for stage in stages
            ):

                warnings.append(
                    "Pipeline does not define a Test stage."
                )

                recommendations.append(
                    "Consider adding automated testing to the pipeline."
                )

        # =====================================================
        # FINAL RESULT
        # =====================================================

        return build_result(
            errors,
            warnings,
            recommendations
        )

    except yaml.YAMLError as error:

        return {
            "success": False,
            "file_type": "GitLab CI",
            "status": "Failed",
            "errors": 1,
            "warnings": 0,
            "issues": [
                {
                    "type": "error",
                    "message":
                        "Invalid YAML syntax: "
                        + str(error)
                }
            ],
            "recommendations": [
                "Correct the YAML syntax and validate the GitLab pipeline again."
            ],
            "timestamp": current_timestamp(),
            "message":
                "GitLab CI validation failed because the YAML syntax is invalid."
        }

    except Exception as error:

        return {
            "success": False,
            "file_type": "GitLab CI",
            "status": "Error",
            "errors": 1,
            "warnings": 0,
            "issues": [
                {
                    "type": "error",
                    "message": str(error)
                }
            ],
            "recommendations": [
                "Review the GitLab CI configuration and try again."
            ],
            "timestamp": current_timestamp(),
            "message":
                "An error occurred while validating GitLab CI."
        }


def build_result(
    errors,
    warnings,
    recommendations
):

    errors = list(dict.fromkeys(errors))
    warnings = list(dict.fromkeys(warnings))
    recommendations = list(
        dict.fromkeys(recommendations)
    )

    error_count = len(errors)
    warning_count = len(warnings)

    issues = []

    for error in errors:

        issues.append({
            "type": "error",
            "message": error
        })

    for warning in warnings:

        issues.append({
            "type": "warning",
            "message": warning
        })

    if error_count > 0:

        return {
            "success": False,
            "file_type": "GitLab CI",
            "status": "Failed",
            "errors": error_count,
            "warnings": warning_count,
            "issues": issues,
            "recommendations": recommendations,
            "timestamp": current_timestamp(),
            "message":
                f"GitLab CI validation failed with "
                f"{error_count} error(s) and "
                f"{warning_count} warning(s)."
        }

    if warning_count > 0:

        return {
            "success": True,
            "file_type": "GitLab CI",
            "status": "Passed",
            "errors": 0,
            "warnings": warning_count,
            "issues": issues,
            "recommendations": recommendations,
            "timestamp": current_timestamp(),
            "message":
                f"GitLab CI configuration is valid with "
                f"{warning_count} warning(s)."
        }

    return {
        "success": True,
        "file_type": "GitLab CI",
        "status": "Passed",
        "errors": 0,
        "warnings": 0,
        "issues": [],
        "recommendations": [],
        "timestamp": current_timestamp(),
        "message":
            "GitLab CI configuration is valid."
    }


def current_timestamp():

    return datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )