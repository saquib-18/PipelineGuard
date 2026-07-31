from datetime import datetime


def validate_security(file_path):
    try:
        with open(file_path, "r") as file:
            content = file.read().lower()

        security_keywords = [
            "password",
            "secret",
            "apikey",
            "api_key",
            "token",
            "private_key",
            "access_key",
            "secret_key"
        ]

        found = []

        for keyword in security_keywords:
            if keyword in content:
                found.append(keyword)

        if len(found) == 0:
            return {
                "success": True,
                "file_type": "Security Scan",
                "status": "Passed",
                "warnings": 0,
                "errors": 0,
                "severity": "None",
                "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "message": "No security issues found."
            }

        return {
            "success": False,
            "file_type": "Security Scan",
            "status": "Failed",
            "warnings": len(found),
            "errors": len(found),
            "severity": "High",
            "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "message": "Sensitive keywords found: " + ", ".join(found)
        }

    except Exception as error:
        return {
            "success": False,
            "file_type": "Security Scan",
            "status": "Error",
            "warnings": 0,
            "errors": 1,
            "severity": "Unknown",
            "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "message": str(error)
        }