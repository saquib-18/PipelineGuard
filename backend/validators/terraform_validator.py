from datetime import datetime
import re


# =========================================================
# TERRAFORM VALIDATOR
# =========================================================

def validate_terraform(file_path):

    errors = []
    warnings = []
    recommendations = []

    try:

        # =================================================
        # READ TERRAFORM FILE
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
                "Terraform configuration is empty."
            )

            recommendations.append(
                "Add Terraform provider and resource configuration."
            )

            return build_result(
                errors,
                warnings,
                recommendations,
                0
            )


        # =================================================
        # REMOVE COMMENTS FOR BASIC ANALYSIS
        # =================================================

        clean_content = remove_comments(
            content
        )


        # =================================================
        # BASIC BRACE CHECK
        # =================================================

        opening_braces = clean_content.count("{")
        closing_braces = clean_content.count("}")


        if opening_braces != closing_braces:

            errors.append(
                "Terraform configuration contains unmatched braces."
            )

            recommendations.append(
                "Check opening and closing braces in the Terraform configuration."
            )


        # =================================================
        # PROVIDER BLOCK
        # =================================================

        providers = re.findall(
            r'\bprovider\s+"([^"]+)"\s*\{',
            clean_content,
            re.IGNORECASE
        )


        if len(providers) == 0:

            errors.append(
                "Terraform configuration does not define a provider."
            )

            recommendations.append(
                "Add a provider block such as provider \"aws\" { ... }."
            )


        # =================================================
        # RESOURCE BLOCKS
        # =================================================

        resources = re.findall(
            r'\bresource\s+"([^"]+)"\s+"([^"]+)"\s*\{',
            clean_content,
            re.IGNORECASE
        )


        resource_count = len(resources)


        if resource_count == 0:

            errors.append(
                "Terraform configuration does not define any resources."
            )

            recommendations.append(
                "Add at least one Terraform resource block."
            )


        # =================================================
        # DUPLICATE RESOURCE IDENTIFIERS
        # =================================================

        seen_resources = set()
        duplicate_resources = []


        for resource_type, resource_name in resources:

            resource_id = (
                resource_type.lower(),
                resource_name.lower()
            )

            if resource_id in seen_resources:

                duplicate_resources.append(
                    f"{resource_type}.{resource_name}"
                )

            else:

                seen_resources.add(
                    resource_id
                )


        if duplicate_resources:

            errors.append(
                "Duplicate Terraform resource definition(s): "
                + ", ".join(duplicate_resources)
                + "."
            )

            recommendations.append(
                "Use a unique local name for each resource of the same type."
            )


        # =================================================
        # TERRAFORM BLOCK
        # =================================================

        terraform_block_exists = bool(
            re.search(
                r"\bterraform\s*\{",
                clean_content,
                re.IGNORECASE
            )
        )


        if not terraform_block_exists:

            warnings.append(
                "Terraform configuration does not define a terraform block."
            )

            recommendations.append(
                "Consider adding a terraform block to define required Terraform and provider versions."
            )


        # =================================================
        # REQUIRED TERRAFORM VERSION
        # =================================================

        if not re.search(
            r"\brequired_version\s*=",
            clean_content,
            re.IGNORECASE
        ):

            warnings.append(
                "Terraform version is not constrained."
            )

            recommendations.append(
                "Define required_version to make builds reproducible."
            )


        # =================================================
        # REQUIRED PROVIDERS
        # =================================================

        if not re.search(
            r"\brequired_providers\s*\{",
            clean_content,
            re.IGNORECASE
        ):

            warnings.append(
                "Provider versions are not explicitly constrained using required_providers."
            )

            recommendations.append(
                "Define required_providers and specify compatible provider versions."
            )


        # =================================================
        # HARDCODED CREDENTIAL CHECK
        #
        # Main security scanning is still handled by
        # security_validator.py. This is Terraform-specific.
        # =================================================

        credential_patterns = [
            (
                "access_key",
                r'\baccess_key\s*=\s*"([^"]+)"'
            ),
            (
                "secret_key",
                r'\bsecret_key\s*=\s*"([^"]+)"'
            ),
            (
                "password",
                r'\bpassword\s*=\s*"([^"]+)"'
            ),
            (
                "token",
                r'\btoken\s*=\s*"([^"]+)"'
            )
        ]


        for credential_name, pattern in credential_patterns:

            matches = re.findall(
                pattern,
                clean_content,
                re.IGNORECASE
            )


            for value in matches:

                # Ignore obvious variable/interpolation references
                if (
                    value.startswith("${")
                    or
                    value.startswith("var.")
                    or
                    value.startswith("local.")
                ):
                    continue


                warnings.append(
                    f"Possible hard-coded '{credential_name}' value detected."
                )

                recommendations.append(
                    f"Do not hard-code {credential_name}. Use environment variables, secret managers, or sensitive Terraform variables."
                )


        # =================================================
        # HTTP URL CHECK
        # =================================================

        if re.search(
            r'http://',
            clean_content,
            re.IGNORECASE
        ):

            warnings.append(
                "Terraform configuration contains an insecure HTTP URL."
            )

            recommendations.append(
                "Use HTTPS instead of HTTP where supported."
            )


        # =================================================
        # PUBLIC CIDR
        # =================================================

        if re.search(
            r'0\.0\.0\.0/0',
            clean_content
        ):

            warnings.append(
                "Terraform configuration contains the public CIDR 0.0.0.0/0."
            )

            recommendations.append(
                "Restrict network access to trusted CIDR ranges whenever possible."
            )


        # =================================================
        # AWS-SPECIFIC CHECKS
        # =================================================

        resource_types = [
            resource_type.lower()
            for resource_type, _ in resources
        ]


        # -------------------------------------------------
        # SECURITY GROUP
        # -------------------------------------------------

        if "aws_security_group" in resource_types:

            if "0.0.0.0/0" in clean_content:

                warnings.append(
                    "AWS security group may allow traffic from the entire internet."
                )

                recommendations.append(
                    "Restrict AWS security-group ingress rules to required networks."
                )


        # -------------------------------------------------
        # S3 PUBLIC ACCESS
        # -------------------------------------------------

        if re.search(
            r'\bacl\s*=\s*"public-read"',
            clean_content,
            re.IGNORECASE
        ):

            warnings.append(
                "An S3 resource appears to use the public-read ACL."
            )

            recommendations.append(
                "Avoid public S3 ACLs unless public access is intentionally required."
            )


        if re.search(
            r'\bacl\s*=\s*"public-read-write"',
            clean_content,
            re.IGNORECASE
        ):

            warnings.append(
                "An S3 resource appears to use the public-read-write ACL."
            )

            recommendations.append(
                "Do not use public-read-write for S3 resources."
            )


        # -------------------------------------------------
        # EC2 PUBLIC IP
        # -------------------------------------------------

        if re.search(
            r'\bassociate_public_ip_address\s*=\s*true',
            clean_content,
            re.IGNORECASE
        ):

            warnings.append(
                "An AWS resource explicitly enables a public IP address."
            )

            recommendations.append(
                "Use private networking unless direct internet exposure is required."
            )


        # =================================================
        # VARIABLE CHECKS
        # =================================================

        variables = re.findall(
            r'\bvariable\s+"([^"]+)"\s*\{',
            clean_content,
            re.IGNORECASE
        )


        sensitive_variable_names = [
            "password",
            "secret",
            "token",
            "api_key",
            "apikey",
            "access_key",
            "secret_key"
        ]


        for variable_name in variables:

            variable_lower = (
                variable_name.lower()
            )


            if any(
                sensitive_name in variable_lower
                for sensitive_name
                in sensitive_variable_names
            ):

                block = extract_named_block(
                    clean_content,
                    "variable",
                    variable_name
                )


                if (
                    block
                    and
                    not re.search(
                        r"\bsensitive\s*=\s*true",
                        block,
                        re.IGNORECASE
                    )
                ):

                    warnings.append(
                        f"Sensitive-looking variable '{variable_name}' is not marked sensitive."
                    )

                    recommendations.append(
                        f"Set sensitive = true for variable '{variable_name}'."
                    )


        # =================================================
        # OUTPUT CHECKS
        # =================================================

        outputs = re.findall(
            r'\boutput\s+"([^"]+)"\s*\{',
            clean_content,
            re.IGNORECASE
        )


        for output_name in outputs:

            output_lower = (
                output_name.lower()
            )


            if any(
                sensitive_name in output_lower
                for sensitive_name
                in sensitive_variable_names
            ):

                block = extract_named_block(
                    clean_content,
                    "output",
                    output_name
                )


                if (
                    block
                    and
                    not re.search(
                        r"\bsensitive\s*=\s*true",
                        block,
                        re.IGNORECASE
                    )
                ):

                    warnings.append(
                        f"Sensitive-looking output '{output_name}' is not marked sensitive."
                    )

                    recommendations.append(
                        f"Set sensitive = true for output '{output_name}'."
                    )


        # =================================================
        # FINAL RESULT
        # =================================================

        return build_result(
            errors,
            warnings,
            recommendations,
            resource_count
        )


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as error:

        return {
            "success": False,
            "file_type": "Terraform",
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
                "Review the Terraform configuration and validate it again."
            ],

            "resource_count": 0,

            "timestamp":
                current_timestamp(),

            "message":
                "An unexpected error occurred while validating the Terraform configuration."
        }


# =========================================================
# REMOVE COMMENTS
# =========================================================

def remove_comments(content):

    # Remove /* ... */ comments
    content = re.sub(
        r"/\*.*?\*/",
        "",
        content,
        flags=re.DOTALL
    )

    # Remove // comments
    content = re.sub(
        r"//.*?$",
        "",
        content,
        flags=re.MULTILINE
    )

    # Remove # comments
    content = re.sub(
        r"#.*?$",
        "",
        content,
        flags=re.MULTILINE
    )

    return content


# =========================================================
# EXTRACT A SIMPLE NAMED HCL BLOCK
# =========================================================

def extract_named_block(
    content,
    block_type,
    block_name
):

    pattern = (
        rf'\b{re.escape(block_type)}\s+'
        rf'"{re.escape(block_name)}"\s*\{{'
    )


    match = re.search(
        pattern,
        content,
        re.IGNORECASE
    )


    if not match:

        return None


    start = match.start()

    brace_start = content.find(
        "{",
        match.start()
    )


    if brace_start == -1:

        return None


    depth = 0


    for index in range(
        brace_start,
        len(content)
    ):

        if content[index] == "{":

            depth += 1


        elif content[index] == "}":

            depth -= 1


            if depth == 0:

                return content[
                    start:index + 1
                ]


    return content[start:]


# =========================================================
# BUILD STANDARD RESULT
# =========================================================

def build_result(
    errors,
    warnings,
    recommendations,
    resource_count
):

    # Remove duplicate messages
    errors = list(
        dict.fromkeys(errors)
    )

    warnings = list(
        dict.fromkeys(warnings)
    )

    recommendations = list(
        dict.fromkeys(
            recommendations
        )
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


    # =====================================================
    # FAILED
    # =====================================================

    if error_count > 0:

        return {
            "success": False,
            "file_type": "Terraform",
            "status": "Failed",
            "errors": error_count,
            "warnings": warning_count,
            "issues": issues,
            "recommendations":
                recommendations,
            "resource_count":
                resource_count,
            "timestamp":
                current_timestamp(),
            "message":
                f"Terraform validation failed with {error_count} error(s) and {warning_count} warning(s)."
        }


    # =====================================================
    # PASSED WITH WARNINGS
    # =====================================================

    if warning_count > 0:

        return {
            "success": True,
            "file_type": "Terraform",
            "status": "Passed",
            "errors": 0,
            "warnings": warning_count,
            "issues": issues,
            "recommendations":
                recommendations,
            "resource_count":
                resource_count,
            "timestamp":
                current_timestamp(),
            "message":
                f"Terraform configuration is valid with {warning_count} warning(s)."
        }


    # =====================================================
    # CLEAN PASS
    # =====================================================

    return {
        "success": True,
        "file_type": "Terraform",
        "status": "Passed",
        "errors": 0,
        "warnings": 0,
        "issues": [],
        "recommendations": [],
        "resource_count":
            resource_count,
        "timestamp":
            current_timestamp(),
        "message":
            "Terraform configuration is valid."
    }


# =========================================================
# TIMESTAMP
# =========================================================

def current_timestamp():

    return datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )