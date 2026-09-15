# =========================================================
# PIPELINEGUARD
# GENERIC YAML VALIDATOR
# =========================================================

from datetime import datetime

import yaml


# =========================================================
# CREATE STANDARD RESULT
# =========================================================

def create_result(
    success,
    file_type,
    status,
    warnings,
    errors,
    message,
    issues=None,
    recommendations=None
):

    return {

        "success":
            success,

        "file_type":
            file_type,

        "status":
            status,

        "warnings":
            warnings,

        "errors":
            errors,

        "timestamp":
            datetime.now().strftime(
                "%d-%m-%Y %H:%M:%S"
            ),

        "message":
            message,

        "issues":
            issues or [],

        "recommendations":
            recommendations or []

    }


# =========================================================
# MAIN YAML VALIDATOR
# =========================================================

def validate_yaml(file_path):

    try:

        # -------------------------------------------------
        # READ FILE
        # -------------------------------------------------

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            content = file.read()


        # -------------------------------------------------
        # EMPTY FILE CHECK
        # -------------------------------------------------

        if not content.strip():

            return create_result(

                False,

                "YAML",

                "Failed",

                0,

                1,

                "Empty YAML file.",

                [
                    "The YAML file does not contain any configuration."
                ],

                [
                    "Add valid YAML configuration before validation."
                ]

            )


        # -------------------------------------------------
        # PARSE YAML
        # -------------------------------------------------

        data = yaml.safe_load(
            content
        )


        # -------------------------------------------------
        # EMPTY YAML
        # -------------------------------------------------

        if data is None:

            return create_result(

                False,

                "YAML",

                "Failed",

                0,

                1,

                "Empty YAML configuration.",

                [
                    "The YAML document does not contain configuration data."
                ],

                [
                    "Add valid YAML configuration."
                ]

            )


        # -------------------------------------------------
        # VALIDATE ROOT STRUCTURE
        # -------------------------------------------------

        if not isinstance(
            data,
            (dict, list)
        ):

            return create_result(

                False,

                "YAML",

                "Failed",

                0,

                1,

                "Invalid YAML configuration structure.",

                [
                    "The YAML root should normally contain a mapping or list."
                ],

                [
                    "Use key-value mappings or YAML lists for configuration."
                ]

            )


        # -------------------------------------------------
        # DICTIONARY YAML
        # -------------------------------------------------

        if isinstance(
            data,
            dict
        ):

            return validate_mapping(
                data
            )


        # -------------------------------------------------
        # LIST YAML
        # -------------------------------------------------

        if isinstance(
            data,
            list
        ):

            return validate_list(
                data
            )


        # -------------------------------------------------
        # FALLBACK
        # -------------------------------------------------

        return create_result(

            True,

            "YAML",

            "Passed",

            0,

            0,

            "Valid YAML configuration.",

            [],

            []

        )


    # =====================================================
    # YAML SYNTAX ERROR
    # =====================================================

    except yaml.YAMLError as error:

        issue_message = (
            get_yaml_error_message(
                error
            )
        )


        return create_result(

            False,

            "YAML",

            "Failed",

            0,

            1,

            "YAML syntax error detected.",

            [
                issue_message
            ],

            [
                "Check YAML indentation.",
                "Check for missing colons.",
                "Check list formatting.",
                "Check quotes and brackets."
            ]

        )


    # =====================================================
    # FILE ERROR
    # =====================================================

    except OSError as error:

        return create_result(

            False,

            "YAML",

            "Failed",

            0,

            1,

            "Unable to read YAML file.",

            [
                str(error)
            ],

            [
                "Verify that the YAML file exists and is readable."
            ]

        )


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as error:

        return create_result(

            False,

            "YAML",

            "Failed",

            0,

            1,

            "Unable to validate YAML file.",

            [
                str(error)
            ],

            [
                "Verify that the file contains valid YAML."
            ]

        )


# =========================================================
# VALIDATE YAML MAPPING
# =========================================================

def validate_mapping(data):

    warnings = 0

    issues = []

    recommendations = []


    # -----------------------------------------------------
    # EMPTY MAPPING
    # -----------------------------------------------------

    if len(data) == 0:

        warnings += 1

        issues.append(
            "The YAML document contains an empty mapping."
        )

        recommendations.append(
            "Add configuration values to the YAML document."
        )


    # -----------------------------------------------------
    # CHECK NULL VALUES
    # -----------------------------------------------------

    null_keys = []


    for key, value in data.items():

        if value is None:

            null_keys.append(
                str(key)
            )


    if null_keys:

        warnings += len(
            null_keys
        )


        for key in null_keys:

            issues.append(

                f"Configuration key '{key}' has no value."

            )


        recommendations.append(

            "Review configuration keys that contain null values."

        )


    # -----------------------------------------------------
    # RESULT WITH WARNINGS
    # -----------------------------------------------------

    if warnings > 0:

        return create_result(

            True,

            "YAML",

            "Passed",

            warnings,

            0,

            (
                "Valid YAML configuration "
                f"with {warnings} warning(s)."
            ),

            issues,

            remove_duplicates(
                recommendations
            )

        )


    # -----------------------------------------------------
    # SUCCESS
    # -----------------------------------------------------

    return create_result(

        True,

        "YAML",

        "Passed",

        0,

        0,

        "Valid YAML configuration.",

        [],

        []

    )


# =========================================================
# VALIDATE YAML LIST
# =========================================================

def validate_list(data):

    # -----------------------------------------------------
    # EMPTY LIST
    # -----------------------------------------------------

    if len(data) == 0:

        return create_result(

            True,

            "YAML",

            "Passed",

            1,

            0,

            "Valid YAML configuration with 1 warning.",

            [
                "The YAML document contains an empty list."
            ],

            [
                "Add configuration items if the list should not be empty."
            ]

        )


    # -----------------------------------------------------
    # VALID LIST
    # -----------------------------------------------------

    return create_result(

        True,

        "YAML",

        "Passed",

        0,

        0,

        "Valid YAML configuration.",

        [],

        []

    )


# =========================================================
# YAML ERROR MESSAGE WITH LINE NUMBER
# =========================================================

def get_yaml_error_message(
    error
):

    problem = getattr(
            error,
            "problem",
            None
        )


    problem_mark = getattr(
            error,
            "problem_mark",
            None
        )


    if problem_mark is not None:

        line = (
            problem_mark.line
            +
            1
        )

        column = (
            problem_mark.column
            +
            1
        )


        if problem:

            return (

                f"{problem} "
                f"at line {line}, "
                f"column {column}."

            )


        return (

            "YAML syntax error "
            f"at line {line}, "
            f"column {column}."

        )


    return str(
        error
    )


# =========================================================
# REMOVE DUPLICATES
# =========================================================

def remove_duplicates(
    items
):

    result = []


    for item in items:

        if item not in result:

            result.append(
                item
            )


    return result