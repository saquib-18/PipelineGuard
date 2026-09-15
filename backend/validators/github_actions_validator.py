from datetime import datetime
import yaml


def validate_github_actions(file_path):

    errors = []
    warnings = []
    recommendations = []

    try:

        with open(file_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        # =====================================================
        # BASIC STRUCTURE
        # =====================================================

        if data is None:
            errors.append("GitHub Actions workflow is empty.")

            recommendations.append(
                "Add a valid GitHub Actions workflow."
            )

            return build_result(
                errors,
                warnings,
                recommendations
            )

        if not isinstance(data, dict):
            errors.append(
                "GitHub Actions workflow must be a YAML mapping."
            )

            return build_result(
                errors,
                warnings,
                recommendations
            )

        # =====================================================
        # WORKFLOW NAME
        # =====================================================

        if "name" not in data:
            warnings.append(
                "Workflow does not define a name."
            )

            recommendations.append(
                "Add a descriptive workflow name."
            )

        # =====================================================
        # TRIGGER
        # =====================================================

        # PyYAML can sometimes interpret unquoted "on" as Boolean True
        workflow_on = data.get("on")

        if workflow_on is None and True in data:
            workflow_on = data.get(True)

        if workflow_on is None:
            errors.append(
                "Workflow does not define an 'on' trigger."
            )

            recommendations.append(
                "Add an event trigger such as push or pull_request."
            )

        # =====================================================
        # JOBS
        # =====================================================

        jobs = data.get("jobs")

        if not isinstance(jobs, dict) or len(jobs) == 0:

            errors.append(
                "Workflow does not define any jobs."
            )

            recommendations.append(
                "Add at least one job under the jobs section."
            )

            return build_result(
                errors,
                warnings,
                recommendations
            )

        # =====================================================
        # CHECK EACH JOB
        # =====================================================

        for job_name, job in jobs.items():

            if not isinstance(job, dict):

                errors.append(
                    f"Job '{job_name}' must be a YAML mapping."
                )

                continue

            # -------------------------------------------------
            # RUNS-ON
            # -------------------------------------------------

            if "runs-on" not in job:

                errors.append(
                    f"Job '{job_name}' does not define 'runs-on'."
                )

                recommendations.append(
                    f"Specify a runner for job '{job_name}'."
                )

            # -------------------------------------------------
            # STEPS
            # -------------------------------------------------

            steps = job.get("steps")

            if not isinstance(steps, list) or len(steps) == 0:

                errors.append(
                    f"Job '{job_name}' does not define any steps."
                )

                recommendations.append(
                    f"Add at least one step to job '{job_name}'."
                )

                continue

            # -------------------------------------------------
            # CHECK STEPS
            # -------------------------------------------------

            for index, step in enumerate(steps, start=1):

                if not isinstance(step, dict):

                    errors.append(
                        f"Job '{job_name}' step {index} must be a YAML mapping."
                    )

                    continue

                if "uses" not in step and "run" not in step:

                    errors.append(
                        f"Job '{job_name}' step {index} does not contain 'uses' or 'run'."
                    )

                # ---------------------------------------------
                # ACTION VERSION
                # ---------------------------------------------

                action = step.get("uses")

                if isinstance(action, str):

                    if "@" not in action:

                        warnings.append(
                            f"Job '{job_name}' uses action '{action}' without a version."
                        )

                        recommendations.append(
                            "Pin GitHub Actions to an explicit version."
                        )

                    elif action.endswith("@master") or action.endswith("@main"):

                        warnings.append(
                            f"Job '{job_name}' uses action '{action}' from a moving branch."
                        )

                        recommendations.append(
                            "Prefer a stable version tag or commit SHA instead of @main/@master."
                        )

                # ---------------------------------------------
                # CONTINUE ON ERROR
                # ---------------------------------------------

                if step.get("continue-on-error") is True:

                    warnings.append(
                        f"Job '{job_name}' step {index} uses continue-on-error."
                    )

                    recommendations.append(
                        "Use continue-on-error only when failure is intentionally acceptable."
                    )

            # -------------------------------------------------
            # JOB TIMEOUT
            # -------------------------------------------------

            if "timeout-minutes" not in job:

                warnings.append(
                    f"Job '{job_name}' does not define timeout-minutes."
                )

                recommendations.append(
                    f"Consider adding timeout-minutes to job '{job_name}'."
                )

        # =====================================================
        # PERMISSIONS
        # =====================================================

        if "permissions" not in data:

            warnings.append(
                "Workflow does not explicitly define GitHub token permissions."
            )

            recommendations.append(
                "Define least-privilege permissions for GITHUB_TOKEN."
            )

        return build_result(
            errors,
            warnings,
            recommendations
        )

    except yaml.YAMLError as error:

        return {
            "success": False,
            "file_type": "GitHub Actions",
            "status": "Failed",
            "errors": 1,
            "warnings": 0,
            "issues": [
                {
                    "type": "error",
                    "message": "Invalid YAML syntax: " + str(error)
                }
            ],
            "recommendations": [
                "Correct the YAML syntax and validate the workflow again."
            ],
            "timestamp": current_timestamp(),
            "message": "GitHub Actions workflow contains invalid YAML."
        }

    except Exception as error:

        return {
            "success": False,
            "file_type": "GitHub Actions",
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
                "Review the GitHub Actions workflow and try again."
            ],
            "timestamp": current_timestamp(),
            "message": "An error occurred while validating GitHub Actions."
        }


def build_result(errors, warnings, recommendations):

    errors = list(dict.fromkeys(errors))
    warnings = list(dict.fromkeys(warnings))
    recommendations = list(dict.fromkeys(recommendations))

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

    error_count = len(errors)
    warning_count = len(warnings)

    if error_count > 0:

        return {
            "success": False,
            "file_type": "GitHub Actions",
            "status": "Failed",
            "errors": error_count,
            "warnings": warning_count,
            "issues": issues,
            "recommendations": recommendations,
            "timestamp": current_timestamp(),
            "message":
                f"GitHub Actions validation failed with "
                f"{error_count} error(s) and "
                f"{warning_count} warning(s)."
        }

    if warning_count > 0:

        return {
            "success": True,
            "file_type": "GitHub Actions",
            "status": "Passed",
            "errors": 0,
            "warnings": warning_count,
            "issues": issues,
            "recommendations": recommendations,
            "timestamp": current_timestamp(),
            "message":
                f"GitHub Actions workflow is valid with "
                f"{warning_count} warning(s)."
        }

    return {
        "success": True,
        "file_type": "GitHub Actions",
        "status": "Passed",
        "errors": 0,
        "warnings": 0,
        "issues": [],
        "recommendations": [],
        "timestamp": current_timestamp(),
        "message": "GitHub Actions workflow is valid."
    }


def current_timestamp():

    return datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )