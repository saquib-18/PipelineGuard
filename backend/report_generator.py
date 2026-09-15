from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import mm

import os
from datetime import datetime
from xml.sax.saxutils import escape


# =========================================================
# PIPELINEGUARD PDF REPORT GENERATOR
# =========================================================

def generate_pdf(report_data, filename):

    # =====================================================
    # REPORT DIRECTORY
    # =====================================================

    report_folder = "reports"

    os.makedirs(
        report_folder,
        exist_ok=True
    )

    pdf_path = os.path.join(
        report_folder,
        filename
    )

    # =====================================================
    # DOCUMENT
    # =====================================================

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="PipelineGuard Validation Report",
        author="PipelineGuard"
    )

    # =====================================================
    # STYLES
    # =====================================================

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "PipelineGuardTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=27,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1D4ED8"),
        spaceAfter=5
    )

    subtitle_style = ParagraphStyle(
        "PipelineGuardSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=20
    )

    section_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=8,
        spaceAfter=9
    )

    normal_style = ParagraphStyle(
        "ReportNormal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )

    small_style = ParagraphStyle(
        "SmallText",
        parent=normal_style,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748B")
    )

    success_style = ParagraphStyle(
        "SuccessText",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#15803D")
    )

    failure_style = ParagraphStyle(
        "FailureText",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#B91C1C")
    )

    # =====================================================
    # ELEMENTS
    # =====================================================

    elements = []

    # =====================================================
    # HEADER
    # =====================================================

    elements.append(
        Paragraph(
            "PipelineGuard",
            title_style
        )
    )

    elements.append(
        Paragraph(
            "Pipeline-as-Code Linter &amp; Validator",
            subtitle_style
        )
    )

    # =====================================================
    # OVERALL RESULT
    # =====================================================

    overall_success = report_data.get(
        "overall_success",
        report_data.get("success", False)
    )

    overall_status = report_data.get(
        "overall_status",
        "Passed" if overall_success else "Failed"
    )

    overall_message = report_data.get(
        "overall_message",
        report_data.get(
            "message",
            "-"
        )
    )

    if overall_success:

        status_table = Table(
            [
                [
                    Paragraph(
                        "<b>OVERALL RESULT</b>",
                        small_style
                    )
                ],
                [
                    Paragraph(
                        "PASSED",
                        success_style
                    )
                ],
                [
                    Paragraph(
                        safe_text(overall_message),
                        normal_style
                    )
                ]
            ],
            colWidths=[170 * mm]
        )

        status_background = colors.HexColor(
            "#DCFCE7"
        )

        status_border = colors.HexColor(
            "#16A34A"
        )

    else:

        status_table = Table(
            [
                [
                    Paragraph(
                        "<b>OVERALL RESULT</b>",
                        small_style
                    )
                ],
                [
                    Paragraph(
                        "FAILED",
                        failure_style
                    )
                ],
                [
                    Paragraph(
                        safe_text(overall_message),
                        normal_style
                    )
                ]
            ],
            colWidths=[170 * mm]
        )

        status_background = colors.HexColor(
            "#FEE2E2"
        )

        status_border = colors.HexColor(
            "#DC2626"
        )

    status_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    status_background
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    1,
                    status_border
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    12
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    12
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                )
            ]
        )
    )

    elements.append(
        status_table
    )

    elements.append(
        Spacer(1, 16)
    )

    # =====================================================
    # VALIDATION SUMMARY
    # =====================================================

    elements.append(
        Paragraph(
            "Validation Summary",
            section_style
        )
    )

    filename_value = report_data.get(
        "filename",
        "-"
    )

    file_type = report_data.get(
        "file_type",
        "-"
    )

    detected_type = report_data.get(
        "detected_type",
        "-"
    )

    pipeline_errors = to_int(
        report_data.get(
            "errors",
            0
        )
    )

    pipeline_warnings = to_int(
        report_data.get(
            "warnings",
            0
        )
    )

    security_errors = to_int(
        report_data.get(
            "security_errors",
            0
        )
    )

    security_warnings = to_int(
        report_data.get(
            "security_warnings",
            0
        )
    )

    total_errors = to_int(
        report_data.get(
            "total_errors",
            pipeline_errors + security_errors
        )
    )

    total_warnings = to_int(
        report_data.get(
            "total_warnings",
            pipeline_warnings + security_warnings
        )
    )

    summary_data = [
        [
            "File",
            safe_text(filename_value)
        ],
        [
            "Pipeline Type",
            safe_text(file_type)
        ],
        [
            "Detected Type",
            display_detected_type(
                detected_type
            )
        ],
        [
            "Pipeline Errors",
            str(pipeline_errors)
        ],
        [
            "Pipeline Warnings",
            str(pipeline_warnings)
        ],
        [
            "Security Errors",
            str(security_errors)
        ],
        [
            "Security Warnings",
            str(security_warnings)
        ],
        [
            "Total Errors",
            str(total_errors)
        ],
        [
            "Total Warnings",
            str(total_warnings)
        ]
    ]

    elements.append(
        create_info_table(
            summary_data,
            normal_style
        )
    )

    elements.append(
        Spacer(1, 14)
    )

    # =====================================================
    # PIPELINE VALIDATION
    # =====================================================

    elements.append(
        Paragraph(
            "Pipeline Validation",
            section_style
        )
    )

    pipeline_data = [
        [
            "Validator",
            safe_text(
                report_data.get(
                    "file_type",
                    "-"
                )
            )
        ],
        [
            "Status",
            safe_text(
                report_data.get(
                    "status",
                    "-"
                )
            )
        ],
        [
            "Errors",
            str(pipeline_errors)
        ],
        [
            "Warnings",
            str(pipeline_warnings)
        ],
        [
            "Result",
            safe_text(
                report_data.get(
                    "message",
                    "-"
                )
            )
        ],
        [
            "Timestamp",
            safe_text(
                report_data.get(
                    "timestamp",
                    "-"
                )
            )
        ]
    ]

    elements.append(
        create_info_table(
            pipeline_data,
            normal_style
        )
    )

    elements.append(
        Spacer(1, 14)
    )

    # =====================================================
    # VALIDATION ISSUES
    # =====================================================

    issues = normalize_items(
        report_data.get(
            "issues",
            []
        )
    )

    elements.append(
        Paragraph(
            "Validation Issues",
            section_style
        )
    )

    if issues:

        for index, issue in enumerate(
            issues,
            start=1
        ):

            if isinstance(
                issue,
                dict
            ):

                message = issue.get(
                    "message",
                    issue.get(
                        "issue",
                        str(issue)
                    )
                )

                line = issue.get(
                    "line"
                )

            else:

                message = str(
                    issue
                )

                line = None

            issue_text = (
                f"<b>{index}.</b> "
                f"{safe_text(message)}"
            )

            if line not in [
                None,
                "",
                "-"
            ]:

                issue_text += (
                    f"<br/><font color='#64748B'>"
                    f"Line: {safe_text(line)}"
                    f"</font>"
                )

            elements.append(
                create_message_box(
                    issue_text,
                    normal_style,
                    "#FEE2E2",
                    "#DC2626"
                )
            )

            elements.append(
                Spacer(1, 6)
            )

    else:

        elements.append(
            create_message_box(
                "No pipeline validation issues detected.",
                normal_style,
                "#DCFCE7",
                "#16A34A"
            )
        )

    elements.append(
        Spacer(1, 12)
    )

    # =====================================================
    # PIPELINE RECOMMENDATIONS
    # =====================================================

    recommendations = normalize_items(
        report_data.get(
            "recommendations",
            []
        )
    )

    elements.append(
        Paragraph(
            "Validation Recommendations",
            section_style
        )
    )

    if recommendations:

        for index, recommendation in enumerate(
            recommendations,
            start=1
        ):

            if isinstance(
                recommendation,
                dict
            ):

                recommendation_text = (
                    recommendation.get(
                        "message",
                        recommendation.get(
                            "recommendation",
                            str(recommendation)
                        )
                    )
                )

            else:

                recommendation_text = str(
                    recommendation
                )

            elements.append(
                create_message_box(
                    (
                        f"<b>{index}.</b> "
                        f"{safe_text(recommendation_text)}"
                    ),
                    normal_style,
                    "#DBEAFE",
                    "#2563EB"
                )
            )

            elements.append(
                Spacer(1, 6)
            )

    else:

        elements.append(
            create_message_box(
                "No additional pipeline recommendations.",
                normal_style,
                "#F1F5F9",
                "#94A3B8"
            )
        )

    elements.append(
        Spacer(1, 14)
    )

    # =====================================================
    # SECURITY ANALYSIS
    # =====================================================

    elements.append(
        Paragraph(
            "Security Analysis",
            section_style
        )
    )

    security_data = [
        [
            "Status",
            safe_text(
                report_data.get(
                    "security_status",
                    "-"
                )
            )
        ],
        [
            "Severity",
            safe_text(
                report_data.get(
                    "security_severity",
                    "-"
                )
            )
        ],
        [
            "Security Errors",
            str(security_errors)
        ],
        [
            "Security Warnings",
            str(security_warnings)
        ],
        [
            "Result",
            safe_text(
                report_data.get(
                    "security_message",
                    "-"
                )
            )
        ]
    ]

    elements.append(
        create_info_table(
            security_data,
            normal_style
        )
    )

    elements.append(
        Spacer(1, 14)
    )

    # =====================================================
    # SECURITY FINDINGS
    # =====================================================

    security_findings = normalize_items(
        report_data.get(
            "security_findings",
            []
        )
    )

    elements.append(
        Paragraph(
            "Security Findings",
            section_style
        )
    )

    if security_findings:

        for index, finding in enumerate(
            security_findings,
            start=1
        ):

            if isinstance(
                finding,
                dict
            ):

                severity = finding.get(
                    "severity",
                    "Unknown"
                )

                message = finding.get(
                    "message",
                    "-"
                )

                line = finding.get(
                    "line"
                )

            else:

                severity = "Unknown"
                message = str(finding)
                line = None

            background, border = (
                severity_colors(
                    severity
                )
            )

            finding_text = (
                f"<b>{index}. "
                f"{safe_text(severity)} Severity</b>"
                f"<br/>"
                f"{safe_text(message)}"
            )

            if line not in [
                None,
                "",
                "-"
            ]:

                finding_text += (
                    "<br/>"
                    "<font color='#64748B'>"
                    f"Line: {safe_text(line)}"
                    "</font>"
                )

            elements.append(
                create_message_box(
                    finding_text,
                    normal_style,
                    background,
                    border
                )
            )

            elements.append(
                Spacer(1, 7)
            )

    else:

        elements.append(
            create_message_box(
                "No security findings detected.",
                normal_style,
                "#DCFCE7",
                "#16A34A"
            )
        )

    elements.append(
        Spacer(1, 12)
    )

    # =====================================================
    # SECURITY RECOMMENDATIONS
    # =====================================================

    security_recommendations = normalize_items(
        report_data.get(
            "security_recommendations",
            []
        )
    )

    elements.append(
        Paragraph(
            "Security Recommendations",
            section_style
        )
    )

    if security_recommendations:

        for index, recommendation in enumerate(
            security_recommendations,
            start=1
        ):

            if isinstance(
                recommendation,
                dict
            ):

                recommendation_text = (
                    recommendation.get(
                        "message",
                        recommendation.get(
                            "recommendation",
                            str(recommendation)
                        )
                    )
                )

            else:

                recommendation_text = (
                    str(recommendation)
                )

            elements.append(
                create_message_box(
                    (
                        f"<b>{index}.</b> "
                        f"{safe_text(recommendation_text)}"
                    ),
                    normal_style,
                    "#FEF3C7",
                    "#D97706"
                )
            )

            elements.append(
                Spacer(1, 6)
            )

    else:

        elements.append(
            create_message_box(
                "No security recommendations required.",
                normal_style,
                "#DCFCE7",
                "#16A34A"
            )
        )

    elements.append(
        Spacer(1, 18)
    )

    # =====================================================
    # FINAL REPORT SUMMARY
    # =====================================================

    elements.append(
        Paragraph(
            "Final Report Summary",
            section_style
        )
    )

    final_summary = [
        [
            "Overall Status",
            safe_text(
                overall_status
            )
        ],
        [
            "Pipeline Status",
            safe_text(
                report_data.get(
                    "status",
                    "-"
                )
            )
        ],
        [
            "Security Status",
            safe_text(
                report_data.get(
                    "security_status",
                    "-"
                )
            )
        ],
        [
            "Highest Security Severity",
            safe_text(
                report_data.get(
                    "security_severity",
                    "-"
                )
            )
        ],
        [
            "Total Errors",
            str(total_errors)
        ],
        [
            "Total Warnings",
            str(total_warnings)
        ],
        [
            "Report Generated",
            datetime.now().strftime(
                "%d-%m-%Y %H:%M:%S"
            )
        ]
    ]

    elements.append(
        create_info_table(
            final_summary,
            normal_style
        )
    )

    elements.append(
        Spacer(1, 20)
    )

    # =====================================================
    # FOOTER TEXT
    # =====================================================

    elements.append(
        Paragraph(
            (
                "Generated by <b>PipelineGuard v3.0</b>"
                "<br/>"
                "Pipeline-as-Code Linter, Validator "
                "&amp; Security Analyzer"
            ),
            ParagraphStyle(
                "FooterText",
                parent=small_style,
                alignment=TA_CENTER
            )
        )
    )

    # =====================================================
    # BUILD PDF
    # =====================================================

    doc.build(
        elements,
        onFirstPage=draw_page_footer,
        onLaterPages=draw_page_footer
    )

    return pdf_path


# =========================================================
# INFORMATION TABLE
# =========================================================

def create_info_table(
    rows,
    style
):

    table_data = [
        [
            Paragraph(
                "<b>Field</b>",
                style
            ),
            Paragraph(
                "<b>Value</b>",
                style
            )
        ]
    ]

    for field, value in rows:

        table_data.append(
            [
                Paragraph(
                    safe_text(field),
                    style
                ),
                Paragraph(
                    safe_text(value),
                    style
                )
            ]
        )

    table = Table(
        table_data,
        colWidths=[
            52 * mm,
            118 * mm
        ],
        repeatRows=1
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1E3A8A")
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "BACKGROUND",
                    (0, 1),
                    (0, -1),
                    colors.HexColor("#F1F5F9")
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#CBD5E1")
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )
            ]
        )
    )

    return table


# =========================================================
# MESSAGE BOX
# =========================================================

def create_message_box(
    text,
    style,
    background,
    border
):

    table = Table(
        [
            [
                Paragraph(
                    text,
                    style
                )
            ]
        ],
        colWidths=[
            170 * mm
        ]
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor(
                        background
                    )
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    colors.HexColor(
                        border
                    )
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                )
            ]
        )
    )

    return table


# =========================================================
# SECURITY SEVERITY COLORS
# =========================================================

def severity_colors(
    severity
):

    severity = str(
        severity
    ).lower()

    if severity == "critical":

        return (
            "#FEE2E2",
            "#991B1B"
        )

    if severity == "high":

        return (
            "#FEE2E2",
            "#DC2626"
        )

    if severity == "medium":

        return (
            "#FEF3C7",
            "#D97706"
        )

    if severity == "low":

        return (
            "#DBEAFE",
            "#2563EB"
        )

    return (
        "#F1F5F9",
        "#94A3B8"
    )


# =========================================================
# DISPLAY DETECTED TYPE
# =========================================================

def display_detected_type(
    detected_type
):

    detected_type = str(
        detected_type
    ).lower()

    mapping = {
        "github": "GitHub Actions",
        "gitlab": "GitLab CI",
        "docker": "Docker Compose",
        "kubernetes": "Kubernetes",
        "jenkins": "Jenkins Pipeline",
        "terraform": "Terraform",
        "yaml": "YAML"
    }

    return mapping.get(
        detected_type,
        detected_type
    )


# =========================================================
# NORMALIZE LIST VALUES
# =========================================================

def normalize_items(
    value
):

    if value is None:
        return []

    if isinstance(
        value,
        list
    ):
        return value

    if isinstance(
        value,
        tuple
    ):
        return list(value)

    if isinstance(
        value,
        str
    ):

        if not value.strip():
            return []

        return [
            value
        ]

    return [
        value
    ]


# =========================================================
# SAFE TEXT FOR REPORTLAB
# =========================================================

def safe_text(
    value
):

    if value is None:
        return "-"

    return escape(
        str(value)
    )


# =========================================================
# SAFE INTEGER
# =========================================================

def to_int(
    value
):

    try:
        return int(value)

    except (
        TypeError,
        ValueError
    ):
        return 0


# =========================================================
# PAGE FOOTER
# =========================================================

def draw_page_footer(
    canvas,
    doc
):

    canvas.saveState()

    page_width, page_height = A4

    # Footer line

    canvas.setStrokeColor(
        colors.HexColor("#CBD5E1")
    )

    canvas.setLineWidth(
        0.5
    )

    canvas.line(
        18 * mm,
        12 * mm,
        page_width - 18 * mm,
        12 * mm
    )

    # Left footer

    canvas.setFont(
        "Helvetica",
        7
    )

    canvas.setFillColor(
        colors.HexColor("#64748B")
    )

    canvas.drawString(
        18 * mm,
        7 * mm,
        "PipelineGuard v3.0"
    )

    # Right page number

    page_text = (
        f"Page {doc.page}"
    )

    canvas.drawRightString(
        page_width - 18 * mm,
        7 * mm,
        page_text
    )

    canvas.restoreState()