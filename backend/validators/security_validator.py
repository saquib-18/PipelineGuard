from datetime import datetime
import re


# =========================================================
# PIPELINEGUARD SECURITY VALIDATOR
# =========================================================

def validate_security(file_path):

    findings = []
    recommendations = []

    try:

        # =================================================
        # READ FILE
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

            return build_result(
                findings,
                recommendations
            )

        # =================================================
        # 1. PRIVATE KEY
        # =================================================

        private_key_patterns = [
            r"-----BEGIN PRIVATE KEY-----",
            r"-----BEGIN RSA PRIVATE KEY-----",
            r"-----BEGIN EC PRIVATE KEY-----",
            r"-----BEGIN OPENSSH PRIVATE KEY-----"
        ]

        for pattern in private_key_patterns:

            match = re.search(
                pattern,
                content,
                re.IGNORECASE
            )

            if match:

                add_finding(
                    findings,
                    "Critical",
                    "Private key detected in configuration file.",
                    get_line_number(
                        content,
                        match.start()
                    )
                )

                recommendations.append(
                    "Remove private keys from configuration files and store them in a secure secret manager."
                )

                break

        # =================================================
        # 2. HARDCODED PASSWORD
        # =================================================

        password_patterns = [
            r"""password\s*[:=]\s*["']([^"'${}\s][^"']*)["']""",
            r"""passwd\s*[:=]\s*["']([^"'${}\s][^"']*)["']""",
            r"""pwd\s*[:=]\s*["']([^"'${}\s][^"']*)["']"""
        ]

        find_hardcoded_secret(
            content,
            password_patterns,
            findings,
            recommendations,
            "High",
            "Possible hard-coded password detected.",
            "Store passwords in a secure secret manager or CI/CD credential store."
        )

        # =================================================
        # 3. HARDCODED API KEY
        # =================================================

        api_key_patterns = [
            r"""api[_-]?key\s*[:=]\s*["']([^"'${}\s][^"']*)["']""",
            r"""apikey\s*[:=]\s*["']([^"'${}\s][^"']*)["']"""
        ]

        find_hardcoded_secret(
            content,
            api_key_patterns,
            findings,
            recommendations,
            "High",
            "Possible hard-coded API key detected.",
            "Move API keys to a secure secret store instead of embedding them directly in configuration."
        )

        # =================================================
        # 4. HARDCODED TOKEN
        # =================================================

        token_patterns = [
            r"""token\s*[:=]\s*["']([^"'${}\s][^"']*)["']""",
            r"""access[_-]?token\s*[:=]\s*["']([^"'${}\s][^"']*)["']""",
            r"""auth[_-]?token\s*[:=]\s*["']([^"'${}\s][^"']*)["']"""
        ]

        find_hardcoded_secret(
            content,
            token_patterns,
            findings,
            recommendations,
            "High",
            "Possible hard-coded access token detected.",
            "Store access tokens in the CI/CD platform's credential or secret-management system."
        )

        # =================================================
        # 5. AWS ACCESS KEY
        # =================================================

        match = re.search(
            r"\bAKIA[0-9A-Z]{16}\b",
            content
        )

        if match:

            add_finding(
                findings,
                "Critical",
                "Possible AWS access key ID detected.",
                get_line_number(
                    content,
                    match.start()
                )
            )

            recommendations.append(
                "Remove AWS credentials from the file and rotate exposed credentials immediately."
            )

        # =================================================
        # 6. GITHUB TOKEN
        # =================================================

        github_patterns = [
            r"\bghp_[A-Za-z0-9]{20,}\b",
            r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"
        ]

        for pattern in github_patterns:

            match = re.search(
                pattern,
                content
            )

            if match:

                add_finding(
                    findings,
                    "Critical",
                    "Possible GitHub access token detected.",
                    get_line_number(
                        content,
                        match.start()
                    )
                )

                recommendations.append(
                    "Remove and rotate the GitHub token and use GitHub Secrets instead."
                )

                break

        # =================================================
        # 7. JWT TOKEN
        # =================================================

        match = re.search(
            r"\beyJ[A-Za-z0-9_-]{10,}\."
            r"[A-Za-z0-9_-]{10,}\."
            r"[A-Za-z0-9_-]{10,}\b",
            content
        )

        if match:

            add_finding(
                findings,
                "High",
                "Possible JWT token detected.",
                get_line_number(
                    content,
                    match.start()
                )
            )

            recommendations.append(
                "Do not store authentication tokens directly in configuration files."
            )

        # =================================================
        # 8. DATABASE URL WITH CREDENTIALS
        # =================================================

        database_pattern = (
            r"(?:mysql|postgres|postgresql|mongodb|redis)"
            r"://[^:\s/@]+:[^@\s/]+@"
        )

        match = re.search(
            database_pattern,
            content,
            re.IGNORECASE
        )

        if match:

            add_finding(
                findings,
                "High",
                "Database connection URL appears to contain embedded credentials.",
                get_line_number(
                    content,
                    match.start()
                )
            )

            recommendations.append(
                "Store database credentials separately and inject them securely at runtime."
            )

        # =================================================
        # 9. INSECURE HTTP
        # =================================================

        for match in re.finditer(
            r"http://[^\s\"']+",
            content,
            re.IGNORECASE
        ):

            url = match.group(0).lower()

            # Local development URLs are ignored
            if (
                "localhost" in url
                or
                "127.0.0.1" in url
            ):
                continue

            add_finding(
                findings,
                "Medium",
                "Insecure HTTP URL detected.",
                get_line_number(
                    content,
                    match.start()
                )
            )

            recommendations.append(
                "Use HTTPS for external services whenever supported."
            )

        # =================================================
        # 10. PUBLIC NETWORK EXPOSURE
        # =================================================

        for match in re.finditer(
            r"0\.0\.0\.0/0",
            content
        ):

            add_finding(
                findings,
                "High",
                "Configuration allows network access from 0.0.0.0/0.",
                get_line_number(
                    content,
                    match.start()
                )
            )

            recommendations.append(
                "Restrict public network access to trusted CIDR ranges whenever possible."
            )

        # =================================================
        # 11. PRIVILEGED CONTAINER
        # =================================================

        privileged_patterns = [
            r"\bprivileged\s*:\s*true\b",
            r"\bprivileged\s*=\s*true\b"
        ]

        for pattern in privileged_patterns:

            match = re.search(
                pattern,
                content,
                re.IGNORECASE
            )

            if match:

                add_finding(
                    findings,
                    "High",
                    "Privileged container execution detected.",
                    get_line_number(
                        content,
                        match.start()
                    )
                )

                recommendations.append(
                    "Avoid privileged containers unless elevated host access is absolutely required."
                )

                break

        # =================================================
        # 12. ROOT USER
        # =================================================

        root_patterns = [
            r"\brunasuser\s*:\s*0\b",
            r"\buser\s*:\s*root\b",
            r"\buser\s*=\s*['\"]?root['\"]?"
        ]

        for pattern in root_patterns:

            match = re.search(
                pattern,
                content,
                re.IGNORECASE
            )

            if match:

                add_finding(
                    findings,
                    "High",
                    "Configuration may run a workload as root.",
                    get_line_number(
                        content,
                        match.start()
                    )
                )

                recommendations.append(
                    "Run containers and workloads as a non-root user whenever possible."
                )

                break

        # =================================================
        # 13. LATEST IMAGE TAG
        # =================================================

        for match in re.finditer(
            r"\bimage\s*:\s*[^\s]+:latest\b",
            content,
            re.IGNORECASE
        ):

            add_finding(
                findings,
                "Low",
                "Container image uses the 'latest' tag.",
                get_line_number(
                    content,
                    match.start()
                )
            )

            recommendations.append(
                "Pin container images to a specific version or immutable digest."
            )

        # =================================================
        # 14. CURL PIPE TO SHELL
        # =================================================

        match = re.search(
            r"\bcurl\b[^\n|]*\|\s*(?:sh|bash)\b",
            content,
            re.IGNORECASE
        )

        if match:

            add_finding(
                findings,
                "High",
                "Command downloads content with curl and pipes it directly to a shell.",
                get_line_number(
                    content,
                    match.start()
                )
            )

            recommendations.append(
                "Download and verify scripts before executing them instead of piping remote content directly to a shell."
            )

        # =================================================
        # 15. WGET PIPE TO SHELL
        # =================================================

        match = re.search(
            r"\bwget\b[^\n|]*\|\s*(?:sh|bash)\b",
            content,
            re.IGNORECASE
        )

        if match:

            add_finding(
                findings,
                "High",
                "Command downloads content with wget and pipes it directly to a shell.",
                get_line_number(
                    content,
                    match.start()
                )
            )

            recommendations.append(
                "Download and verify scripts before executing them."
            )

        # =================================================
        # FINAL RESULT
        # =================================================

        return build_result(
            findings,
            recommendations
        )

    # =====================================================
    # ERROR
    # =====================================================

    except Exception as error:

        return {
            "success": False,
            "file_type": "Security Scan",
            "status": "Error",
            "severity": "Unknown",
            "warnings": 0,
            "errors": 1,

            "findings": [
                {
                    "severity": "Unknown",
                    "message": str(error),
                    "line": None
                }
            ],

            "recommendations": [
                "Review the uploaded file and run the security scan again."
            ],

            "timestamp": current_timestamp(),

            "message":
                "An error occurred during security analysis."
        }


# =========================================================
# FIND HARDCODED SECRET + LINE NUMBER
# =========================================================

def find_hardcoded_secret(
    content,
    patterns,
    findings,
    recommendations,
    severity,
    message,
    recommendation
):

    for pattern in patterns:

        for match in re.finditer(
            pattern,
            content,
            re.IGNORECASE
        ):

            # Captured secret value
            value = match.group(1).strip()

            if not value:
                continue

            # =============================================
            # IGNORE SECRET REFERENCES
            # =============================================

            value_lower = value.lower()

            safe_references = [
                "${{",
                "${",
                "secrets.",
                "vars.",
                "env.",
                "var.",
                "local.",
                "credentials(",
                "withcredentials",
                "secretkeyref",
                "valuefrom"
            ]

            if any(
                reference in value_lower
                for reference in safe_references
            ):
                continue

            # =============================================
            # IGNORE PLACEHOLDERS
            # =============================================

            placeholders = {
                "password",
                "your-password",
                "your_password",
                "changeme",
                "change-me",
                "example",
                "example-token",
                "example-key",
                "dummy",
                "test",
                "placeholder",
                "xxxxx",
                "xxxxxx"
            }

            if value_lower in placeholders:
                continue

            # =============================================
            # IGNORE VERY SHORT VALUES
            # =============================================

            if len(value) < 4:
                continue

            # =============================================
            # ADD FINDING
            # =============================================

            line_number = get_line_number(
                content,
                match.start()
            )

            add_finding(
                findings,
                severity,
                message,
                line_number
            )

            recommendations.append(
                recommendation
            )


# =========================================================
# GET LINE NUMBER
# =========================================================

def get_line_number(
    content,
    position
):

    return (
        content.count(
            "\n",
            0,
            position
        )
        + 1
    )


# =========================================================
# ADD FINDING
# =========================================================

def add_finding(
    findings,
    severity,
    message,
    line
):

    # Avoid exact duplicate finding
    # but allow same problem on different lines

    for finding in findings:

        if (
            finding.get("message") == message
            and
            finding.get("line") == line
        ):
            return

    findings.append({
        "severity": severity,
        "message": message,
        "line": line
    })


# =========================================================
# BUILD SECURITY RESULT
# =========================================================

def build_result(
    findings,
    recommendations
):

    recommendations = list(
        dict.fromkeys(
            recommendations
        )
    )

    # =====================================================
    # NO SECURITY FINDINGS
    # =====================================================

    if not findings:

        return {
            "success": True,
            "file_type": "Security Scan",
            "status": "Passed",
            "severity": "None",
            "warnings": 0,
            "errors": 0,
            "findings": [],
            "recommendations": [],
            "timestamp": current_timestamp(),
            "message":
                "No security issues detected."
        }

    # =====================================================
    # SEVERITY ORDER
    # =====================================================

    severity_order = {
        "Low": 1,
        "Medium": 2,
        "High": 3,
        "Critical": 4
    }

    highest_finding = max(
        findings,
        key=lambda finding:
            severity_order.get(
                finding.get(
                    "severity",
                    ""
                ),
                0
            )
    )

    highest_severity = (
        highest_finding.get(
            "severity",
            "Unknown"
        )
    )

    # =====================================================
    # COUNT WARNINGS / ERRORS
    # =====================================================

    warning_count = 0
    error_count = 0

    for finding in findings:

        severity = finding.get(
            "severity"
        )

        if severity in [
            "Low",
            "Medium"
        ]:

            warning_count += 1

        elif severity in [
            "High",
            "Critical"
        ]:

            error_count += 1

    # =====================================================
    # SECURITY STATUS
    # =====================================================

    security_success = (
        error_count == 0
    )

    if security_success:

        status = "Passed"

        message = (
            "Security analysis passed with "
            f"{warning_count} warning(s)."
        )

    else:

        status = "Failed"

        message = (
            "Security analysis detected "
            f"{error_count} high-risk issue(s) "
            f"and {warning_count} warning(s)."
        )

    # =====================================================
    # RETURN
    # =====================================================

    return {
        "success": security_success,
        "file_type": "Security Scan",
        "status": status,
        "severity": highest_severity,
        "warnings": warning_count,
        "errors": error_count,
        "findings": findings,
        "recommendations": recommendations,
        "timestamp": current_timestamp(),
        "message": message
    }


# =========================================================
# TIMESTAMP
# =========================================================

def current_timestamp():

    return datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )