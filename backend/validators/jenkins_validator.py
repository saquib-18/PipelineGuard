from datetime import datetime
import re


# =========================================================
# JENKINS PIPELINE VALIDATOR
# =========================================================

def validate_jenkins(file_path):

    errors = []
    warnings = []
    recommendations = []

    try:

        # =================================================
        # READ JENKINSFILE
        # =================================================

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as file:

            content = file.read()


        # =================================================
        # EMPTY FILE
        # =================================================

        if not content.strip():

            errors.append(
                "Jenkinsfile is empty."
            )

            recommendations.append(
                "Add a Jenkins Declarative Pipeline configuration."
            )

            return build_result(
                errors,
                warnings,
                recommendations
            )


        content_lower = content.lower()


        # =================================================
        # REQUIRED PIPELINE BLOCK
        # =================================================

        if not re.search(
            r"\bpipeline\s*\{",
            content,
            re.IGNORECASE
        ):

            errors.append(
                "Missing required 'pipeline' block."
            )

            recommendations.append(
                "Wrap the Jenkins configuration inside a pipeline { } block."
            )


        # =================================================
        # AGENT
        # =================================================

        if not re.search(
            r"\bagent\b",
            content,
            re.IGNORECASE
        ):

            errors.append(
                "Pipeline does not define an agent."
            )

            recommendations.append(
                "Add an agent declaration such as 'agent any'."
            )


        # =================================================
        # STAGES BLOCK
        # =================================================

        if not re.search(
            r"\bstages\s*\{",
            content,
            re.IGNORECASE
        ):

            errors.append(
                "Missing required 'stages' block."
            )

            recommendations.append(
                "Add a stages { } block containing pipeline stages."
            )


        # =================================================
        # STAGE
        # =================================================

        stages = re.findall(
            r"\bstage\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
            content,
            re.IGNORECASE
        )


        if len(stages) == 0:

            errors.append(
                "Pipeline does not define any stages."
            )

            recommendations.append(
                "Add at least one stage such as Build, Test or Deploy."
            )


        # =================================================
        # STEPS BLOCK
        # =================================================

        if not re.search(
            r"\bsteps\s*\{",
            content,
            re.IGNORECASE
        ):

            errors.append(
                "Pipeline does not contain a steps block."
            )

            recommendations.append(
                "Add steps { } inside each pipeline stage."
            )


        # =================================================
        # DUPLICATE STAGE NAMES
        # =================================================

        duplicate_stages = []

        seen_stages = set()


        for stage in stages:

            stage_lower = stage.lower()

            if stage_lower in seen_stages:

                duplicate_stages.append(
                    stage
                )

            else:

                seen_stages.add(
                    stage_lower
                )


        if duplicate_stages:

            warnings.append(
                "Duplicate Jenkins stage name(s): "
                + ", ".join(duplicate_stages)
                + "."
            )

            recommendations.append(
                "Use unique stage names to make pipeline execution easier to understand."
            )


        # =================================================
        # POST BLOCK
        # =================================================

        if not re.search(
            r"\bpost\s*\{",
            content,
            re.IGNORECASE
        ):

            warnings.append(
                "Pipeline does not define a post block."
            )

            recommendations.append(
                "Add a post block for cleanup, success, failure or notification actions."
            )


        # =================================================
        # TIMEOUT
        # =================================================

        if not re.search(
            r"\btimeout\s*\(",
            content,
            re.IGNORECASE
        ):

            warnings.append(
                "Pipeline does not configure a timeout."
            )

            recommendations.append(
                "Configure a timeout to prevent pipeline jobs from running indefinitely."
            )


        # =================================================
        # RETRY
        # =================================================

        if not re.search(
            r"\bretry\s*\(",
            content,
            re.IGNORECASE
        ):

            warnings.append(
                "Pipeline does not configure retry handling."
            )

            recommendations.append(
                "Consider using retry for steps that may fail because of temporary network or service problems."
            )


        # =================================================
        # BUILD STAGE
        # =================================================

        if not any(
            "build" in stage.lower()
            for stage in stages
        ):

            warnings.append(
                "Pipeline does not contain a Build stage."
            )

            recommendations.append(
                "Consider adding a Build stage."
            )


        # =================================================
        # TEST STAGE
        # =================================================

        if not any(
            "test" in stage.lower()
            for stage in stages
        ):

            warnings.append(
                "Pipeline does not contain a Test stage."
            )

            recommendations.append(
                "Consider adding automated testing before deployment."
            )


        # =================================================
        # HARDCODED CREDENTIAL-LIKE VALUES
        #
        # The separate security scanner will perform the
        # main secret scan. This check provides a Jenkins-
        # specific warning.
        # =================================================

        credential_patterns = [

            r"""password\s*=\s*['"][^'"]+['"]""",

            r"""token\s*=\s*['"][^'"]+['"]""",

            r"""api[_-]?key\s*=\s*['"][^'"]+['"]"""

        ]


        credential_detected = False


        for pattern in credential_patterns:

            if re.search(
                pattern,
                content,
                re.IGNORECASE
            ):

                credential_detected = True
                break


        if credential_detected:

            warnings.append(
                "Pipeline may contain hard-coded credential values."
            )

            recommendations.append(
                "Store secrets in Jenkins Credentials and access them using credentials() or withCredentials()."
            )


        # =================================================
        # CREDENTIAL HANDLING
        # =================================================

        if (
            "password" in content_lower
            or
            "secret" in content_lower
            or
            "token" in content_lower
        ):

            if (
                "withcredentials" not in content_lower
                and
                "credentials(" not in content_lower
            ):

                warnings.append(
                    "Credential-related values are referenced without Jenkins credential management."
                )

                recommendations.append(
                    "Use Jenkins Credentials with credentials() or withCredentials() instead of storing sensitive values directly."
                )


        # =================================================
        # DISABLE CONCURRENT BUILDS
        # =================================================

        if (
            "disableconcurrentbuilds"
            not in content_lower
        ):

            warnings.append(
                "Concurrent pipeline executions are not explicitly controlled."
            )

            recommendations.append(
                "Consider disableConcurrentBuilds() if simultaneous executions could conflict."
            )


        # =================================================
        # FINAL RESULT
        # =================================================

        return build_result(
            errors,
            warnings,
            recommendations,
            len(stages)
        )


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as error:

        return {

            "success": False,

            "file_type":
                "Jenkins Pipeline",

            "status":
                "Error",

            "warnings":
                0,

            "errors":
                1,

            "issues": [

                {
                    "type": "error",
                    "message": str(error)
                }

            ],

            "recommendations": [

                "Review the Jenkinsfile and validate it again."

            ],

            "stage_count":
                0,

            "timestamp":
                current_timestamp(),

            "message":
                "An unexpected error occurred while validating the Jenkins pipeline."

        }


# =========================================================
# BUILD STANDARD RESULT
# =========================================================

def build_result(
    errors,
    warnings,
    recommendations,
    stage_count
):

    error_count = len(errors)
    warning_count = len(warnings)


    # =====================================================
    # BUILD ISSUES ARRAY
    # =====================================================

    issues = []


    for error in errors:

        issues.append({

            "type":
                "error",

            "message":
                error

        })


    for warning in warnings:

        issues.append({

            "type":
                "warning",

            "message":
                warning

        })


    # =====================================================
    # REMOVE DUPLICATE RECOMMENDATIONS
    # =====================================================

    recommendations = list(
        dict.fromkeys(
            recommendations
        )
    )


    # =====================================================
    # FAILED
    # =====================================================

    if error_count > 0:

        return {

            "success":
                False,

            "file_type":
                "Jenkins Pipeline",

            "status":
                "Failed",

            "errors":
                error_count,

            "warnings":
                warning_count,

            "issues":
                issues,

            "recommendations":
                recommendations,

            "stage_count":
                stage_count,

            "timestamp":
                current_timestamp(),

            "message":
                f"Jenkins Pipeline validation failed with {error_count} error(s) and {warning_count} warning(s)."

        }


    # =====================================================
    # PASSED WITH WARNINGS
    # =====================================================

    if warning_count > 0:

        return {

            "success":
                True,

            "file_type":
                "Jenkins Pipeline",

            "status":
                "Passed",

            "errors":
                0,

            "warnings":
                warning_count,

            "issues":
                issues,

            "recommendations":
                recommendations,

            "stage_count":
                stage_count,

            "timestamp":
                current_timestamp(),

            "message":
                f"Jenkins Pipeline is valid with {warning_count} warning(s)."

        }


    # =====================================================
    # CLEAN PASS
    # =====================================================

    return {

        "success":
            True,

        "file_type":
            "Jenkins Pipeline",

        "status":
            "Passed",

        "errors":
            0,

        "warnings":
            0,

        "issues":
            [],

        "recommendations":
            [],

        "stage_count":
            stage_count,

        "timestamp":
            current_timestamp(),

        "message":
            "Jenkins Pipeline is valid."

    }


# =========================================================
# TIMESTAMP
# =========================================================

def current_timestamp():

    return datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )