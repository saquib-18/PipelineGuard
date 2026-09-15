from datetime import datetime
import yaml


# =========================================================
# KUBERNETES VALIDATOR
# =========================================================

def validate_kubernetes(file_path):

    errors = []
    warnings = []
    recommendations = []

    try:

        # =================================================
        # READ YAML
        # Supports multiple Kubernetes documents
        # =================================================

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            documents = list(
                yaml.safe_load_all(file)
            )


        # Remove empty YAML documents
        documents = [
            document
            for document in documents
            if document is not None
        ]


        # =================================================
        # EMPTY FILE
        # =================================================

        if len(documents) == 0:

            errors.append(
                "Kubernetes manifest is empty."
            )

            recommendations.append(
                "Add at least one Kubernetes resource."
            )

            return build_result(
                errors,
                warnings,
                recommendations
            )


        # =================================================
        # VALIDATE EVERY YAML DOCUMENT
        # =================================================

        for index, data in enumerate(
            documents,
            start=1
        ):

            resource_prefix = (
                f"Document {index}"
            )


            # =============================================
            # ROOT STRUCTURE
            # =============================================

            if not isinstance(data, dict):

                errors.append(
                    f"{resource_prefix}: Kubernetes resource must be a YAML mapping."
                )

                continue


            # =============================================
            # REQUIRED FIELDS
            # =============================================

            api_version = data.get(
                "apiVersion"
            )

            kind = data.get(
                "kind"
            )

            metadata = data.get(
                "metadata"
            )


            if not api_version:

                errors.append(
                    f"{resource_prefix}: Missing required 'apiVersion'."
                )

                recommendations.append(
                    f"{resource_prefix}: Add the Kubernetes API version."
                )


            if not kind:

                errors.append(
                    f"{resource_prefix}: Missing required 'kind'."
                )

                recommendations.append(
                    f"{resource_prefix}: Specify the Kubernetes resource kind."
                )


            if not metadata:

                errors.append(
                    f"{resource_prefix}: Missing required 'metadata' section."
                )

                recommendations.append(
                    f"{resource_prefix}: Add metadata including a resource name."
                )


            # =============================================
            # METADATA VALIDATION
            # =============================================

            resource_name = None


            if metadata is not None:

                if not isinstance(
                    metadata,
                    dict
                ):

                    errors.append(
                        f"{resource_prefix}: 'metadata' must be a mapping."
                    )

                else:

                    resource_name = (
                        metadata.get("name")
                    )


                    if not resource_name:

                        errors.append(
                            f"{resource_prefix}: metadata.name is required."
                        )

                        recommendations.append(
                            f"{resource_prefix}: Add a unique name under metadata."
                        )


            # =============================================
            # BETTER RESOURCE LABEL
            # =============================================

            if kind and resource_name:

                resource_prefix = (
                    f"{kind} '{resource_name}'"
                )

            elif kind:

                resource_prefix = kind


            # =============================================
            # POD-BASED WORKLOADS
            # =============================================

            workload_kinds = [
                "Deployment",
                "StatefulSet",
                "DaemonSet",
                "ReplicaSet",
                "Job"
            ]


            if kind in workload_kinds:

                validate_workload(
                    data,
                    resource_prefix,
                    errors,
                    warnings,
                    recommendations
                )


            # =============================================
            # CRONJOB
            # =============================================

            elif kind == "CronJob":

                validate_cronjob(
                    data,
                    resource_prefix,
                    errors,
                    warnings,
                    recommendations
                )


            # =============================================
            # POD
            # =============================================

            elif kind == "Pod":

                spec = data.get("spec")

                validate_pod_spec(
                    spec,
                    resource_prefix,
                    errors,
                    warnings,
                    recommendations
                )


            # =============================================
            # SERVICE
            # =============================================

            elif kind == "Service":

                validate_service(
                    data,
                    resource_prefix,
                    errors,
                    warnings,
                    recommendations
                )


            # =============================================
            # CONFIGMAP
            # =============================================

            elif kind == "ConfigMap":

                validate_config_map(
                    data,
                    resource_prefix,
                    warnings,
                    recommendations
                )


            # =============================================
            # SECRET
            # =============================================

            elif kind == "Secret":

                validate_secret(
                    data,
                    resource_prefix,
                    warnings,
                    recommendations
                )


        # =================================================
        # FINAL RESULT
        # =================================================

        return build_result(
            errors,
            warnings,
            recommendations
        )


    # =====================================================
    # YAML ERROR
    # =====================================================

    except yaml.YAMLError as error:

        return {
            "success": False,
            "file_type": "Kubernetes",
            "status": "Failed",
            "warnings": 0,
            "errors": 1,

            "issues": [
                {
                    "type": "error",
                    "message":
                        "Invalid YAML syntax: "
                        + str(error)
                }
            ],

            "recommendations": [
                "Correct the YAML syntax and validate the manifest again."
            ],

            "timestamp":
                current_timestamp(),

            "message":
                "Kubernetes validation failed because the YAML syntax is invalid."
        }


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as error:

        return {
            "success": False,
            "file_type": "Kubernetes",
            "status": "Error",
            "warnings": 0,
            "errors": 1,

            "issues": [
                {
                    "type": "error",
                    "message": str(error)
                }
            ],

            "recommendations": [
                "Review the Kubernetes manifest and try again."
            ],

            "timestamp":
                current_timestamp(),

            "message":
                "An unexpected error occurred while validating the Kubernetes manifest."
        }


# =========================================================
# WORKLOAD VALIDATION
# Deployment / StatefulSet / DaemonSet / Job etc.
# =========================================================

def validate_workload(
    data,
    resource,
    errors,
    warnings,
    recommendations
):

    spec = data.get("spec")


    if not isinstance(spec, dict):

        errors.append(
            f"{resource}: Missing or invalid 'spec' section."
        )

        recommendations.append(
            f"{resource}: Add a valid workload spec."
        )

        return


    # -----------------------------------------------------
    # POD TEMPLATE
    # -----------------------------------------------------

    template = spec.get(
        "template"
    )


    if not isinstance(
        template,
        dict
    ):

        errors.append(
            f"{resource}: Missing required pod template."
        )

        recommendations.append(
            f"{resource}: Add spec.template to define the Pods."
        )

        return


    template_spec = template.get(
        "spec"
    )


    validate_pod_spec(
        template_spec,
        resource,
        errors,
        warnings,
        recommendations
    )


    # -----------------------------------------------------
    # DEPLOYMENT SELECTOR
    # -----------------------------------------------------

    if data.get("kind") in [
        "Deployment",
        "StatefulSet",
        "DaemonSet",
        "ReplicaSet"
    ]:

        selector = spec.get(
            "selector"
        )


        if not isinstance(
            selector,
            dict
        ):

            errors.append(
                f"{resource}: Missing required spec.selector."
            )

            recommendations.append(
                f"{resource}: Define a selector matching the Pod labels."
            )


# =========================================================
# CRONJOB VALIDATION
# =========================================================

def validate_cronjob(
    data,
    resource,
    errors,
    warnings,
    recommendations
):

    spec = data.get("spec")


    if not isinstance(spec, dict):

        errors.append(
            f"{resource}: Missing or invalid spec."
        )

        return


    if not spec.get("schedule"):

        errors.append(
            f"{resource}: CronJob schedule is missing."
        )

        recommendations.append(
            f"{resource}: Define spec.schedule using a cron expression."
        )


    job_template = spec.get(
        "jobTemplate"
    )


    if not isinstance(
        job_template,
        dict
    ):

        errors.append(
            f"{resource}: Missing jobTemplate."
        )

        return


    job_spec = job_template.get(
        "spec"
    )


    if not isinstance(
        job_spec,
        dict
    ):

        errors.append(
            f"{resource}: Invalid jobTemplate.spec."
        )

        return


    template = job_spec.get(
        "template"
    )


    if not isinstance(
        template,
        dict
    ):

        errors.append(
            f"{resource}: Missing Pod template."
        )

        return


    validate_pod_spec(
        template.get("spec"),
        resource,
        errors,
        warnings,
        recommendations
    )


# =========================================================
# POD SPEC VALIDATION
# =========================================================

def validate_pod_spec(
    spec,
    resource,
    errors,
    warnings,
    recommendations
):

    if not isinstance(
        spec,
        dict
    ):

        errors.append(
            f"{resource}: Missing or invalid Pod spec."
        )

        recommendations.append(
            f"{resource}: Define a valid Pod specification."
        )

        return


    containers = spec.get(
        "containers"
    )


    # =====================================================
    # CONTAINERS
    # =====================================================

    if not isinstance(
        containers,
        list
    ) or len(containers) == 0:

        errors.append(
            f"{resource}: No containers are defined."
        )

        recommendations.append(
            f"{resource}: Add at least one container."
        )

        return


    # =====================================================
    # CHECK EACH CONTAINER
    # =====================================================

    for index, container in enumerate(
        containers,
        start=1
    ):

        if not isinstance(
            container,
            dict
        ):

            errors.append(
                f"{resource}: Container {index} must be a mapping."
            )

            continue


        container_name = (
            container.get("name")
            or
            f"container-{index}"
        )


        # -------------------------------------------------
        # NAME
        # -------------------------------------------------

        if not container.get("name"):

            errors.append(
                f"{resource}: Container {index} is missing a name."
            )


        # -------------------------------------------------
        # IMAGE
        # -------------------------------------------------

        image = container.get(
            "image"
        )


        if not image:

            errors.append(
                f"{resource}: Container '{container_name}' does not define an image."
            )

            recommendations.append(
                f"{resource}: Specify an image for container '{container_name}'."
            )


        elif isinstance(image, str):

            if image.endswith(
                ":latest"
            ):

                warnings.append(
                    f"{resource}: Container '{container_name}' uses the 'latest' image tag."
                )

                recommendations.append(
                    f"{resource}: Pin container '{container_name}' to a specific image version."
                )


            elif ":" not in image:

                warnings.append(
                    f"{resource}: Container '{container_name}' does not specify an explicit image tag."
                )

                recommendations.append(
                    f"{resource}: Use a fixed image tag for container '{container_name}'."
                )


        # -------------------------------------------------
        # RESOURCES
        # -------------------------------------------------

        resources = container.get(
            "resources"
        )


        if not isinstance(
            resources,
            dict
        ):

            warnings.append(
                f"{resource}: Container '{container_name}' does not define resource requests or limits."
            )

            recommendations.append(
                f"{resource}: Configure CPU and memory requests/limits for container '{container_name}'."
            )

        else:

            requests = resources.get(
                "requests"
            )

            limits = resources.get(
                "limits"
            )


            if not requests:

                warnings.append(
                    f"{resource}: Container '{container_name}' does not define resource requests."
                )


            if not limits:

                warnings.append(
                    f"{resource}: Container '{container_name}' does not define resource limits."
                )


        # -------------------------------------------------
        # SECURITY CONTEXT
        # -------------------------------------------------

        security_context = (
            container.get(
                "securityContext"
            )
        )


        if isinstance(
            security_context,
            dict
        ):

            if (
                security_context.get(
                    "privileged"
                )
                is True
            ):

                warnings.append(
                    f"{resource}: Container '{container_name}' runs in privileged mode."
                )

                recommendations.append(
                    f"{resource}: Disable privileged mode unless absolutely necessary."
                )


            if (
                security_context.get(
                    "runAsNonRoot"
                )
                is not True
            ):

                warnings.append(
                    f"{resource}: Container '{container_name}' does not enforce runAsNonRoot."
                )

                recommendations.append(
                    f"{resource}: Set securityContext.runAsNonRoot to true."
                )

        else:

            warnings.append(
                f"{resource}: Container '{container_name}' has no securityContext."
            )

            recommendations.append(
                f"{resource}: Add a securityContext and enforce non-root execution."
            )


        # -------------------------------------------------
        # READINESS PROBE
        # -------------------------------------------------

        if (
            "readinessProbe"
            not in container
        ):

            warnings.append(
                f"{resource}: Container '{container_name}' has no readinessProbe."
            )

            recommendations.append(
                f"{resource}: Add a readinessProbe for reliable traffic routing."
            )


        # -------------------------------------------------
        # LIVENESS PROBE
        # -------------------------------------------------

        if (
            "livenessProbe"
            not in container
        ):

            warnings.append(
                f"{resource}: Container '{container_name}' has no livenessProbe."
            )

            recommendations.append(
                f"{resource}: Add a livenessProbe to detect unhealthy containers."
            )


    # =====================================================
    # HOST NETWORK
    # =====================================================

    if spec.get(
        "hostNetwork"
    ) is True:

        warnings.append(
            f"{resource}: Pod uses the host network."
        )

        recommendations.append(
            f"{resource}: Avoid hostNetwork unless specifically required."
        )


    # =====================================================
    # HOST PID
    # =====================================================

    if spec.get(
        "hostPID"
    ) is True:

        warnings.append(
            f"{resource}: Pod uses the host PID namespace."
        )

        recommendations.append(
            f"{resource}: Avoid hostPID unless specifically required."
        )


# =========================================================
# SERVICE VALIDATION
# =========================================================

def validate_service(
    data,
    resource,
    errors,
    warnings,
    recommendations
):

    spec = data.get("spec")


    if not isinstance(
        spec,
        dict
    ):

        errors.append(
            f"{resource}: Missing or invalid Service spec."
        )

        return


    ports = spec.get(
        "ports"
    )


    if not isinstance(
        ports,
        list
    ) or len(ports) == 0:

        errors.append(
            f"{resource}: Service does not define any ports."
        )

        recommendations.append(
            f"{resource}: Add at least one Service port."
        )


    service_type = spec.get(
        "type",
        "ClusterIP"
    )


    if (
        service_type
        == "LoadBalancer"
    ):

        warnings.append(
            f"{resource}: Service is publicly exposable through LoadBalancer."
        )

        recommendations.append(
            f"{resource}: Confirm that external LoadBalancer exposure is required."
        )


    if (
        service_type
        == "NodePort"
    ):

        warnings.append(
            f"{resource}: Service uses NodePort."
        )

        recommendations.append(
            f"{resource}: Prefer ClusterIP with an Ingress when appropriate."
        )


# =========================================================
# CONFIGMAP VALIDATION
# =========================================================

def validate_config_map(
    data,
    resource,
    warnings,
    recommendations
):

    config_data = data.get(
        "data"
    )


    if not config_data:

        warnings.append(
            f"{resource}: ConfigMap contains no data."
        )

        recommendations.append(
            f"{resource}: Add configuration entries or remove the unused ConfigMap."
        )


# =========================================================
# SECRET VALIDATION
# =========================================================

def validate_secret(
    data,
    resource,
    warnings,
    recommendations
):

    secret_type = data.get(
        "type"
    )


    if not secret_type:

        warnings.append(
            f"{resource}: Secret does not explicitly define a type."
        )


    if data.get(
        "stringData"
    ):

        warnings.append(
            f"{resource}: Secret uses stringData containing plain-text values in the manifest."
        )

        recommendations.append(
            f"{resource}: Avoid committing sensitive Secret values to source control."
        )


# =========================================================
# BUILD STANDARD RESULT
# =========================================================

def build_result(
    errors,
    warnings,
    recommendations
):

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


    # Remove duplicate recommendations
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
            "success": False,
            "file_type": "Kubernetes",
            "status": "Failed",
            "warnings": warning_count,
            "errors": error_count,
            "issues": issues,
            "recommendations":
                recommendations,
            "timestamp":
                current_timestamp(),
            "message":
                f"Kubernetes validation failed with {error_count} error(s) and {warning_count} warning(s)."
        }


    # =====================================================
    # PASSED WITH WARNINGS
    # =====================================================

    if warning_count > 0:

        return {
            "success": True,
            "file_type": "Kubernetes",
            "status": "Passed",
            "warnings": warning_count,
            "errors": 0,
            "issues": issues,
            "recommendations":
                recommendations,
            "timestamp":
                current_timestamp(),
            "message":
                f"Kubernetes manifest is valid with {warning_count} warning(s)."
        }


    # =====================================================
    # CLEAN PASS
    # =====================================================

    return {
        "success": True,
        "file_type": "Kubernetes",
        "status": "Passed",
        "warnings": 0,
        "errors": 0,
        "issues": [],
        "recommendations": [],
        "timestamp":
            current_timestamp(),
        "message":
            "Kubernetes manifest is valid."
    }


# =========================================================
# TIMESTAMP
# =========================================================

def current_timestamp():

    return datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )