from datetime import datetime
import yaml


def validate_docker(file_path):

    errors = []
    warnings = []
    recommendations = []

    try:

        # =====================================================
        # READ DOCKER COMPOSE FILE
        # =====================================================

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = yaml.safe_load(file)


        # =====================================================
        # EMPTY FILE
        # =====================================================

        if data is None:

            errors.append(
                "Docker Compose file is empty."
            )

            recommendations.append(
                "Add a services section containing at least one service."
            )

            return build_result(
                errors,
                warnings,
                recommendations
            )


        # =====================================================
        # ROOT MUST BE A DICTIONARY
        # =====================================================

        if not isinstance(data, dict):

            errors.append(
                "Docker Compose root configuration must be a mapping."
            )

            recommendations.append(
                "Define the Docker Compose configuration using YAML key-value sections."
            )

            return build_result(
                errors,
                warnings,
                recommendations
            )


        # =====================================================
        # SERVICES SECTION
        # =====================================================

        if "services" not in data:

            errors.append(
                "Missing required 'services' section."
            )

            recommendations.append(
                "Add a services section containing the application containers."
            )

            return build_result(
                errors,
                warnings,
                recommendations
            )


        services = data.get("services")


        # =====================================================
        # SERVICES MUST BE A DICTIONARY
        # =====================================================

        if not isinstance(services, dict):

            errors.append(
                "'services' must contain service definitions."
            )

            recommendations.append(
                "Define each Docker service under the services section."
            )

            return build_result(
                errors,
                warnings,
                recommendations
            )


        # =====================================================
        # AT LEAST ONE SERVICE
        # =====================================================

        if len(services) == 0:

            errors.append(
                "No Docker services are defined."
            )

            recommendations.append(
                "Add at least one service under the services section."
            )

            return build_result(
                errors,
                warnings,
                recommendations
            )


        # =====================================================
        # CHECK EACH SERVICE
        # =====================================================

        for service_name, service in services.items():

            # -------------------------------------------------
            # SERVICE STRUCTURE
            # -------------------------------------------------

            if not isinstance(service, dict):

                errors.append(
                    f"Service '{service_name}' must be a configuration mapping."
                )

                continue


            # -------------------------------------------------
            # IMAGE OR BUILD
            # -------------------------------------------------

            if (
                "image" not in service
                and
                "build" not in service
            ):

                errors.append(
                    f"Service '{service_name}' does not define an image or build configuration."
                )

                recommendations.append(
                    f"Add 'image' or 'build' to service '{service_name}'."
                )


            # -------------------------------------------------
            # IMAGE CHECK
            # -------------------------------------------------

            image = service.get("image")

            if isinstance(image, str):

                # Explicit latest tag
                if image.endswith(":latest"):

                    warnings.append(
                        f"Service '{service_name}' uses the 'latest' image tag."
                    )

                    recommendations.append(
                        f"Use a fixed image version for service '{service_name}' instead of ':latest'."
                    )

                # No explicit tag
                elif ":" not in image:

                    warnings.append(
                        f"Service '{service_name}' does not specify an explicit image tag."
                    )

                    recommendations.append(
                        f"Pin service '{service_name}' to a specific image version."
                    )


            # -------------------------------------------------
            # PRIVILEGED MODE
            # -------------------------------------------------

            if service.get("privileged") is True:

                warnings.append(
                    f"Service '{service_name}' runs in privileged mode."
                )

                recommendations.append(
                    f"Avoid privileged mode for service '{service_name}' unless it is absolutely required."
                )


            # -------------------------------------------------
            # RESTART POLICY
            # -------------------------------------------------

            if "restart" not in service:

                warnings.append(
                    f"Service '{service_name}' does not define a restart policy."
                )

                recommendations.append(
                    f"Consider adding a restart policy to service '{service_name}'."
                )


            # -------------------------------------------------
            # HEALTHCHECK
            # -------------------------------------------------

            if "healthcheck" not in service:

                warnings.append(
                    f"Service '{service_name}' does not define a healthcheck."
                )

                recommendations.append(
                    f"Consider adding a healthcheck to service '{service_name}'."
                )


            # -------------------------------------------------
            # PORT VALIDATION
            # -------------------------------------------------

            if "ports" in service:

                ports = service.get("ports")

                if not isinstance(ports, list):

                    errors.append(
                        f"Service '{service_name}' ports configuration must be a list."
                    )

                    recommendations.append(
                        f"Define ports for service '{service_name}' as a YAML list."
                    )


            # -------------------------------------------------
            # ENVIRONMENT CHECK
            # -------------------------------------------------

            environment = service.get(
                "environment"
            )

            if environment is not None:

                if not isinstance(
                    environment,
                    (dict, list)
                ):

                    errors.append(
                        f"Service '{service_name}' has an invalid environment configuration."
                    )


            # -------------------------------------------------
            # VOLUME CHECK
            # -------------------------------------------------

            volumes = service.get(
                "volumes"
            )

            if (
                volumes is not None
                and
                not isinstance(volumes, list)
            ):

                errors.append(
                    f"Service '{service_name}' volumes configuration must be a list."
                )


        # =====================================================
        # RETURN FINAL RESULT
        # =====================================================

        return build_result(
            errors,
            warnings,
            recommendations
        )


    # =========================================================
    # YAML ERROR
    # =========================================================

    except yaml.YAMLError as error:

        return {
            "success": False,
            "file_type": "Docker Compose",
            "status": "Failed",
            "warnings": 0,
            "errors": 1,

            "issues": [
                "Invalid YAML syntax: "
                + str(error)
            ],

            "recommendations": [
                "Correct the YAML syntax and validate the file again."
            ],

            "timestamp": datetime.now().strftime(
                "%d-%m-%Y %H:%M:%S"
            ),

            "message":
                "Docker Compose validation failed because the YAML syntax is invalid."
        }


    # =========================================================
    # GENERAL ERROR
    # =========================================================

    except Exception as error:

        return {
            "success": False,
            "file_type": "Docker Compose",
            "status": "Error",
            "warnings": 0,
            "errors": 1,

            "issues": [
                str(error)
            ],

            "recommendations": [
                "Review the Docker Compose configuration and try again."
            ],

            "timestamp": datetime.now().strftime(
                "%d-%m-%Y %H:%M:%S"
            ),

            "message":
                "An error occurred while validating the Docker Compose file."
        }


# =============================================================
# BUILD STANDARD RESULT
# =============================================================

def build_result(
    errors,
    warnings,
    recommendations
):

    error_count = len(errors)
    warning_count = len(warnings)


    # Combine errors + warnings for frontend
    issues = []

    for error in errors:

        issues.append(
            {
                "type": "error",
                "message": error
            }
        )


    for warning in warnings:

        issues.append(
            {
                "type": "warning",
                "message": warning
            }
        )


    # Remove duplicate recommendations
    recommendations = list(
        dict.fromkeys(
            recommendations
        )
    )


    # =========================================================
    # FAILED
    # =========================================================

    if error_count > 0:

        return {
            "success": False,
            "file_type": "Docker Compose",
            "status": "Failed",
            "warnings": warning_count,
            "errors": error_count,
            "issues": issues,
            "recommendations": recommendations,

            "timestamp": datetime.now().strftime(
                "%d-%m-%Y %H:%M:%S"
            ),

            "message":
                f"Docker Compose validation failed with {error_count} error(s) and {warning_count} warning(s)."
        }


    # =========================================================
    # PASSED WITH WARNINGS
    # =========================================================

    if warning_count > 0:

        return {
            "success": True,
            "file_type": "Docker Compose",
            "status": "Passed",
            "warnings": warning_count,
            "errors": 0,
            "issues": issues,
            "recommendations": recommendations,

            "timestamp": datetime.now().strftime(
                "%d-%m-%Y %H:%M:%S"
            ),

            "message":
                f"Docker Compose is valid with {warning_count} warning(s)."
        }


    # =========================================================
    # FULL PASS
    # =========================================================

    return {
        "success": True,
        "file_type": "Docker Compose",
        "status": "Passed",
        "warnings": 0,
        "errors": 0,
        "issues": [],
        "recommendations": [],

        "timestamp": datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        ),

        "message":
            "Docker Compose configuration is valid."
    }