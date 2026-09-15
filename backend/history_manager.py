import json
import os
from copy import deepcopy


# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

HISTORY_FILE = os.path.join(
    BASE_DIR,
    "validation_history.json"
)

MAX_HISTORY = 50


# =========================================================
# SAFE INTEGER
# =========================================================

def safe_int(value):

    try:
        return int(value or 0)

    except (
        ValueError,
        TypeError
    ):
        return 0


# =========================================================
# LOAD HISTORY
# =========================================================

def load_history():

    if not os.path.exists(HISTORY_FILE):
        return []

    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (
        json.JSONDecodeError,
        OSError,
        TypeError
    ):

        return []


# =========================================================
# SAVE HISTORY
# =========================================================

def save_history(history):

    if not isinstance(history, list):
        history = []

    try:

        with open(
            HISTORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                history,
                file,
                indent=4,
                ensure_ascii=False
            )

        return True

    except OSError as error:

        print(
            "History save error:",
            error
        )

        return False


# =========================================================
# ADD HISTORY
# =========================================================

def add_history(report):

    if not isinstance(report, dict):
        return False

    history = load_history()

    # Store complete validation report
    history_record = deepcopy(report)

    history.insert(
        0,
        history_record
    )

    # Keep only latest records
    history = history[:MAX_HISTORY]

    return save_history(
        history
    )


# =========================================================
# GET ALL HISTORY
# =========================================================

def get_history():

    return load_history()


# =========================================================
# GET ONE HISTORY RECORD
# =========================================================

def get_history_item(index):

    history = load_history()

    try:

        index = int(index)

    except (
        ValueError,
        TypeError
    ):

        return None

    if (
        index < 0
        or
        index >= len(history)
    ):

        return None

    return history[index]


# =========================================================
# DELETE ONE HISTORY RECORD
# =========================================================

def delete_history_item(index):

    history = load_history()

    try:

        index = int(index)

    except (
        ValueError,
        TypeError
    ):

        return False

    if (
        index < 0
        or
        index >= len(history)
    ):

        return False

    history.pop(index)

    return save_history(
        history
    )


# =========================================================
# CLEAR HISTORY
# =========================================================

def clear_history():

    return save_history([])


# =========================================================
# GET HISTORY COUNT
# =========================================================

def get_history_count():

    history = load_history()

    return len(history)


# =========================================================
# NORMALIZE PIPELINE TYPE
# =========================================================

def normalize_pipeline_type(value):

    value = str(
        value or ""
    ).strip().lower()

    value = value.replace(
        "_",
        " "
    )

    value = value.replace(
        "-",
        " "
    )

    # -----------------------------------------------------
    # GITHUB
    # -----------------------------------------------------

    if "github" in value:
        return "github"

    # -----------------------------------------------------
    # GITLAB
    # -----------------------------------------------------

    if "gitlab" in value:
        return "gitlab"

    # -----------------------------------------------------
    # JENKINS
    # -----------------------------------------------------

    if "jenkins" in value:
        return "jenkins"

    # -----------------------------------------------------
    # DOCKER
    # -----------------------------------------------------

    if "docker" in value:
        return "docker"

    # -----------------------------------------------------
    # KUBERNETES
    # -----------------------------------------------------

    if (
        "kubernetes" in value
        or
        value == "k8s"
    ):
        return "kubernetes"

    # -----------------------------------------------------
    # TERRAFORM
    # -----------------------------------------------------

    if "terraform" in value:
        return "terraform"

    # -----------------------------------------------------
    # YAML
    # -----------------------------------------------------

    if (
        "yaml" in value
        or
        "yml" in value
    ):
        return "yaml"

    return "other"


# =========================================================
# CREATE RECENT ACTIVITY RECORD
# =========================================================

def create_recent_activity(record):

    status = str(
        record.get(
            "overall_status",
            record.get(
                "status",
                "Unknown"
            )
        )
    ).strip()

    return {

        "filename":
            record.get(
                "filename",
                "Unknown"
            ),

        "file_type":
            record.get(
                "file_type",
                record.get(
                    "detected_type",
                    "Unknown"
                )
            ),

        "status":
            status,

        "errors":
            safe_int(
                record.get(
                    "total_errors",
                    record.get(
                        "errors",
                        0
                    )
                )
            ),

        "warnings":
            safe_int(
                record.get(
                    "total_warnings",
                    record.get(
                        "warnings",
                        0
                    )
                )
            ),

        "severity":
            record.get(
                "security_severity",
                "None"
            ),

        "timestamp":
            record.get(
                "timestamp",
                "-"
            )
    }


# =========================================================
# GET STATISTICS
# =========================================================

def get_statistics():

    history = load_history()

    # =====================================================
    # MAIN STATISTICS
    # =====================================================

    statistics = {

        "total_validations": 0,

        "passed": 0,

        "failed": 0,

        "pass_rate": 0,

        "failure_rate": 0,

        "security_passed": 0,

        "security_failed": 0,

        "security_failure_rate": 0,

        "total_errors": 0,

        "total_warnings": 0,


        # =================================================
        # PIPELINE COUNTS
        # =================================================

        "pipeline_types": {

            "github": 0,

            "gitlab": 0,

            "jenkins": 0,

            "docker": 0,

            "kubernetes": 0,

            "terraform": 0,

            "yaml": 0,

            "other": 0
        },


        # =================================================
        # RECENT ACTIVITY
        # =================================================

        "recent_activity": []
    }


    # =====================================================
    # PROCESS HISTORY
    # =====================================================

    for record in history:

        if not isinstance(
            record,
            dict
        ):
            continue


        # =================================================
        # TOTAL VALIDATIONS
        # =================================================

        statistics[
            "total_validations"
        ] += 1


        # =================================================
        # OVERALL STATUS
        # =================================================

        status = str(

            record.get(
                "overall_status",
                record.get(
                    "status",
                    ""
                )
            )

        ).strip().lower()


        if status == "passed":

            statistics[
                "passed"
            ] += 1

        else:

            statistics[
                "failed"
            ] += 1


        # =================================================
        # SECURITY STATUS
        # =================================================

        security_status = str(

            record.get(
                "security_status",
                ""
            )

        ).strip().lower()


        if security_status == "passed":

            statistics[
                "security_passed"
            ] += 1


        elif security_status == "failed":

            statistics[
                "security_failed"
            ] += 1


        # =================================================
        # ERRORS
        # =================================================

        total_errors = safe_int(

            record.get(
                "total_errors",
                record.get(
                    "errors",
                    0
                )
            )

        )


        statistics[
            "total_errors"
        ] += total_errors


        # =================================================
        # WARNINGS
        # =================================================

        total_warnings = safe_int(

            record.get(
                "total_warnings",
                record.get(
                    "warnings",
                    0
                )
            )

        )


        statistics[
            "total_warnings"
        ] += total_warnings


        # =================================================
        # PIPELINE TYPE
        # =================================================

        pipeline_type = normalize_pipeline_type(

            record.get(
                "file_type",
                record.get(
                    "detected_type",
                    ""
                )
            )

        )


        statistics[
            "pipeline_types"
        ][pipeline_type] += 1


    # =====================================================
    # PASS / FAILURE RATE
    # =====================================================

    total = statistics[
        "total_validations"
    ]


    if total > 0:

        statistics[
            "pass_rate"
        ] = round(

            (
                statistics["passed"]
                /
                total
            )
            *
            100,

            1
        )


        statistics[
            "failure_rate"
        ] = round(

            (
                statistics["failed"]
                /
                total
            )
            *
            100,

            1
        )


    # =====================================================
    # SECURITY FAILURE RATE
    # =====================================================

    security_total = (

        statistics[
            "security_passed"
        ]

        +

        statistics[
            "security_failed"
        ]

    )


    if security_total > 0:

        statistics[
            "security_failure_rate"
        ] = round(

            (
                statistics[
                    "security_failed"
                ]
                /
                security_total
            )
            *
            100,

            1
        )


    # =====================================================
    # RECENT ACTIVITY
    # =====================================================
    #
    # History is already newest first because add_history()
    # inserts records at index 0.
    #
    # Show latest 5 validations.
    # =====================================================

    recent_records = history[:5]


    for record in recent_records:

        if not isinstance(
            record,
            dict
        ):
            continue

        statistics[
            "recent_activity"
        ].append(

            create_recent_activity(
                record
            )

        )


    # =====================================================
    # RETURN STATISTICS
    # =====================================================

    return statistics