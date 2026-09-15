import os
import re
import yaml


# =========================================================
# PIPELINE TYPE DETECTOR
# =========================================================

def detect_pipeline_type(file_path, original_filename=""):

    filename = original_filename.lower().strip()

    # =====================================================
    # 1. STRONG EXTENSION / FILENAME DETECTION
    # =====================================================

    if (
        filename == "jenkinsfile"
        or filename.endswith(".groovy")
    ):
        return "jenkins"

    if filename.endswith(".tf"):
        return "terraform"

    # =====================================================
    # READ CONTENT
    # =====================================================

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as file:

            content = file.read()

    except Exception:
        return "yaml"

    if not content.strip():
        return "yaml"

    content_lower = content.lower()

    # =====================================================
    # 2. JENKINS CONTENT
    # =====================================================

    if (
        re.search(
            r"\bpipeline\s*\{",
            content,
            re.IGNORECASE
        )
        and
        re.search(
            r"\bstages\s*\{",
            content,
            re.IGNORECASE
        )
    ):
        return "jenkins"

    # =====================================================
    # 3. TERRAFORM CONTENT
    # =====================================================

    terraform_patterns = [
        r'\bterraform\s*\{',
        r'\bprovider\s+"[^"]+"\s*\{',
        r'\bresource\s+"[^"]+"\s+"[^"]+"\s*\{',
        r'\bvariable\s+"[^"]+"\s*\{'
    ]

    terraform_score = 0

    for pattern in terraform_patterns:

        if re.search(
            pattern,
            content,
            re.IGNORECASE
        ):
            terraform_score += 1

    if terraform_score >= 2:
        return "terraform"

    # =====================================================
    # 4. YAML PARSING
    # =====================================================

    try:

        documents = list(
            yaml.safe_load_all(content)
        )

    except yaml.YAMLError:

        # Invalid YAML still needs a validator.
        # Use filename hints where possible.

        if "docker" in filename:
            return "docker"

        if (
            "kubernetes" in filename
            or "k8s" in filename
        ):
            return "kubernetes"

        if "gitlab" in filename:
            return "gitlab"

        if (
            "github" in filename
            or "workflow" in filename
            or "actions" in filename
        ):
            return "github"

        return "yaml"

    documents = [
        document
        for document in documents
        if document is not None
    ]

    if not documents:
        return "yaml"

    # =====================================================
    # 5. KUBERNETES
    #
    # Kubernetes manifests normally contain:
    # apiVersion + kind + metadata
    # =====================================================

    for data in documents:

        if not isinstance(data, dict):
            continue

        if (
            "apiVersion" in data
            and
            "kind" in data
        ):
            return "kubernetes"

    # Use first document for CI / Compose detection

    data = documents[0]

    if not isinstance(data, dict):
        return "yaml"

    # =====================================================
    # 6. GITHUB ACTIONS
    #
    # Typical:
    # name:
    # on:
    # jobs:
    # =====================================================

    jobs = data.get("jobs")

    # PyYAML YAML 1.1 may convert "on" to True.
    github_trigger = data.get("on")

    if github_trigger is None and True in data:
        github_trigger = data.get(True)

    if (
        isinstance(jobs, dict)
        and
        github_trigger is not None
    ):

        github_score = 0

        for job in jobs.values():

            if not isinstance(job, dict):
                continue

            if "runs-on" in job:
                github_score += 2

            if "steps" in job:
                github_score += 1

        if github_score > 0:
            return "github"

    # =====================================================
    # 7. DOCKER COMPOSE
    #
    # Compose normally has:
    # services:
    #   web:
    #     image/build:
    # =====================================================

    services = data.get("services")

    if isinstance(services, dict):

        docker_score = 0

        for service in services.values():

            if not isinstance(service, dict):
                continue

            if "image" in service:
                docker_score += 1

            if "build" in service:
                docker_score += 1

            if "ports" in service:
                docker_score += 1

            if "volumes" in service:
                docker_score += 1

            if "environment" in service:
                docker_score += 1

        if docker_score > 0:
            return "docker"

        # Filename can strengthen detection of an incomplete
        # Docker Compose file.

        if (
            "docker" in filename
            or "compose" in filename
        ):
            return "docker"

    # =====================================================
    # 8. GITLAB CI
    # =====================================================

    gitlab_score = 0

    if "stages" in data:
        gitlab_score += 2

    if "workflow" in data:
        gitlab_score += 1

    if "before_script" in data:
        gitlab_score += 1

    if "after_script" in data:
        gitlab_score += 1

    if "default" in data:
        gitlab_score += 1

    reserved_keys = {
        "stages",
        "variables",
        "workflow",
        "default",
        "include",
        "image",
        "services",
        "before_script",
        "after_script",
        "cache"
    }

    for key, value in data.items():

        if key in reserved_keys:
            continue

        if str(key).startswith("."):
            continue

        if isinstance(value, dict):

            if "script" in value:
                gitlab_score += 2

            if "stage" in value:
                gitlab_score += 1

    if gitlab_score >= 2:
        return "gitlab"

    # =====================================================
    # 9. FILENAME FALLBACKS
    # =====================================================

    if (
        "docker-compose" in filename
        or filename in [
            "compose.yml",
            "compose.yaml"
        ]
    ):
        return "docker"

    if (
        "kubernetes" in filename
        or "k8s" in filename
    ):
        return "kubernetes"

    if "gitlab" in filename:
        return "gitlab"

    if (
        "github" in filename
        or "workflow" in filename
        or "actions" in filename
    ):
        return "github"

    # =====================================================
    # 10. GENERIC YAML
    # =====================================================

    return "yaml"