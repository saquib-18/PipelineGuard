from datetime import datetime
import yaml


def validate_yaml(file_path):
    try:
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)

        if data is None:
            return {
                "success": False,
                "file_type": "YAML",
                "status": "Failed",
                "warnings": 0,
                "errors": 1,
                "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "message": "Empty YAML file."
            }

        if "jobs" in data:
            return {
                "success": True,
                "file_type": "GitHub Actions",
                "status": "Passed",
                "warnings": 0,
                "errors": 0,
                "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "message": "Valid GitHub Actions pipeline."
            }

        if "stages" in data:
            return {
                "success": True,
                "file_type": "GitLab CI",
                "status": "Passed",
                "warnings": 0,
                "errors": 0,
                "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "message": "Valid GitLab CI pipeline."
            }

        return {
            "success": True,
            "file_type": "YAML",
            "status": "Passed",
            "warnings": 0,
            "errors": 0,
            "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "message": "Valid YAML file."
        }

    except yaml.YAMLError as error:
        return {
            "success": False,
            "file_type": "YAML",
            "status": "Failed",
            "warnings": 0,
            "errors": 1,
            "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "message": str(error)
        }

    except Exception as error:
        return {
            "success": False,
            "file_type": "YAML",
            "status": "Error",
            "warnings": 0,
            "errors": 1,
            "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "message": str(error)
        }