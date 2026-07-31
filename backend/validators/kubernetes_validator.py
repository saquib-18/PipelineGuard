from datetime import datetime
import yaml


def validate_kubernetes(file_path):
    try:
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)

        if data is None:
            return {
                "success": False,
                "file_type": "Kubernetes",
                "status": "Failed",
                "warnings": 0,
                "errors": 1,
                "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "message": "Empty Kubernetes manifest."
            }

        missing = []

        if "apiVersion" not in data:
            missing.append("apiVersion")

        if "kind" not in data:
            missing.append("kind")

        if "metadata" not in data:
            missing.append("metadata")

        if missing:
            return {
                "success": False,
                "file_type": "Kubernetes",
                "status": "Failed",
                "warnings": 0,
                "errors": len(missing),
                "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "message": "Missing: " + ", ".join(missing)
            }

        return {
            "success": True,
            "file_type": "Kubernetes",
            "status": "Passed",
            "warnings": 0,
            "errors": 0,
            "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "message": "Valid Kubernetes manifest."
        }

    except yaml.YAMLError as error:
        return {
            "success": False,
            "file_type": "Kubernetes",
            "status": "Failed",
            "warnings": 0,
            "errors": 1,
            "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "message": str(error)
        }

    except Exception as error:
        return {
            "success": False,
            "file_type": "Kubernetes",
            "status": "Error",
            "warnings": 0,
            "errors": 1,
            "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "message": str(error)
        }