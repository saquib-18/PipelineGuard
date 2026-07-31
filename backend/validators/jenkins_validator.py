from datetime import datetime


def validate_jenkins(file_path):
    try:
        with open(file_path, "r") as file:
            content = file.read().lower()

        required_keywords = [
            "pipeline",
            "agent",
            "stages",
            "steps"
        ]

        missing = []

        for keyword in required_keywords:
            if keyword not in content:
                missing.append(keyword)

        if len(missing) == 0:
            return {
                "success": True,
                "file_type": "Jenkins Pipeline",
                "status": "Passed",
                "warnings": 0,
                "errors": 0,
                "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "message": "Valid Jenkins Pipeline."
            }

        return {
            "success": False,
            "file_type": "Jenkins Pipeline",
            "status": "Failed",
            "warnings": 0,
            "errors": len(missing),
            "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "message": "Missing: " + ", ".join(missing)
        }

    except Exception as error:
        return {
            "success": False,
            "file_type": "Jenkins Pipeline",
            "status": "Error",
            "warnings": 0,
            "errors": 1,
            "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "message": str(error)
        }