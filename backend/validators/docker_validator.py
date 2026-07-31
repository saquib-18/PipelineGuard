from datetime import datetime
import yaml


def validate_docker(file_path):
    try:
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)

        if data is None:
            return {
                "success": False,
                "file_type": "Docker Compose",
                "status": "Failed",
                "warnings": 0,
                "errors": 1,
                "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "message": "Empty Docker Compose file."
            }

        if "services" not in data:
            return {
                "success": False,
                "file_type": "Docker Compose",
                "status": "Failed",
                "warnings": 0,
                "errors": 1,
                "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                "message": "Missing 'services' section."
            }

        return {
            "success": True,
            "file_type": "Docker Compose",
            "status": "Passed",
            "warnings": 0,
            "errors": 0,
            "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "message": "Valid Docker Compose file."
        }

    except yaml.YAMLError as error:
        return {
            "success": False,
            "file_type": "Docker Compose",
            "status": "Failed",
            "warnings": 0,
            "errors": 1,
            "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "message": str(error)
        }

    except Exception as error:
        return {
            "success": False,
            "file_type": "Docker Compose",
            "status": "Error",
            "warnings": 0,
            "errors": 1,
            "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "message": str(error)
        }