/* =========================================================
   PIPELINEGUARD v3.0
   MAIN FRONTEND CONTROLLER
========================================================= */


let selectedFile = null;

let currentResult = null;


/* =========================================================
   APPLICATION START
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        setupFileInput();

        setupDragAndDrop();

        setupTheme();

        loadDashboard();

        loadHistory();

    }
);


/* =========================================================
   ELEMENT HELPER
========================================================= */

function getElement(id) {

    return document.getElementById(id);

}


/* =========================================================
   SET TEXT SAFELY
========================================================= */

function setText(
    id,
    value
) {

    const element =
        getElement(id);

    if (!element) {
        return;
    }

    element.textContent =
        value;

}


/* =========================================================
   NUMBER HELPER
========================================================= */

function numberValue(value) {

    const number =
        Number(value);

    if (
        Number.isFinite(number)
    ) {

        return number;

    }

    return 0;

}


/* =========================================================
   ESCAPE HTML
========================================================= */

function escapeHTML(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "-";

    }

    return String(value)
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );

}


/* =========================================================
   FILE INPUT
========================================================= */

function setupFileInput() {

    const fileInput =
        getElement(
            "fileInput"
        );


    if (!fileInput) {

        console.error(
            "fileInput not found."
        );

        return;

    }


    fileInput.addEventListener(
        "change",
        function () {

            if (
                this.files &&
                this.files.length > 0
            ) {

                selectedFile =
                    this.files[0];

                displaySelectedFile(
                    selectedFile
                );

            }

        }
    );

}


/* =========================================================
   DISPLAY SELECTED FILE
========================================================= */

function displaySelectedFile(file) {

    if (!file) {
        return;
    }


    selectedFile =
        file;


    const fileName =
        getElement(
            "selectedFileName"
        );


    const fileSize =
        getElement(
            "selectedFileSize"
        );


    if (fileName) {

        fileName.textContent =
            file.name;

    }


    if (fileSize) {

        fileSize.textContent =
            formatFileSize(
                file.size
            );

    }

}


/* =========================================================
   FORMAT FILE SIZE
========================================================= */

function formatFileSize(bytes) {

    bytes =
        numberValue(bytes);


    if (bytes === 0) {

        return "0 B";

    }


    if (bytes < 1024) {

        return (
            bytes +
            " B"
        );

    }


    if (
        bytes <
        1024 * 1024
    ) {

        return (
            (
                bytes /
                1024
            ).toFixed(2)
            +
            " KB"
        );

    }


    return (
        (
            bytes /
            (
                1024 *
                1024
            )
        ).toFixed(2)
        +
        " MB"
    );

}


/* =========================================================
   DRAG AND DROP
========================================================= */

function setupDragAndDrop() {

    const dropZone =
        getElement(
            "dropZone"
        );


    const fileInput =
        getElement(
            "fileInput"
        );


    if (
        !dropZone ||
        !fileInput
    ) {

        return;

    }


    dropZone.addEventListener(
        "dragover",
        function (event) {

            event.preventDefault();

            dropZone.classList.add(
                "drag-active"
            );

        }
    );


    dropZone.addEventListener(
        "dragleave",
        function () {

            dropZone.classList.remove(
                "drag-active"
            );

        }
    );


    dropZone.addEventListener(
        "drop",
        function (event) {

            event.preventDefault();

            dropZone.classList.remove(
                "drag-active"
            );


            const files =
                event.dataTransfer.files;


            if (
                !files ||
                files.length === 0
            ) {

                return;

            }


            selectedFile =
                files[0];


            try {

                const transfer =
                    new DataTransfer();


                transfer.items.add(
                    selectedFile
                );


                fileInput.files =
                    transfer.files;

            }
            catch (error) {

                console.warn(
                    "Unable to assign dropped file.",
                    error
                );

            }


            displaySelectedFile(
                selectedFile
            );

        }
    );

}


/* =========================================================
   CHECK SUPPORTED FILE
========================================================= */

function isSupportedFile(file) {

    if (!file) {
        return false;
    }


    const name =
        String(
            file.name || ""
        ).toLowerCase();


    return (
        name.endsWith(".yml") ||
        name.endsWith(".yaml") ||
        name.endsWith(".tf") ||
        name.endsWith(".groovy") ||
        name === "jenkinsfile"
    );

}


/* =========================================================
   UPLOAD + VALIDATE
========================================================= */

async function uploadFile() {

    const fileInput =
        getElement(
            "fileInput"
        );


    let file =
        selectedFile;


    if (
        !file &&
        fileInput &&
        fileInput.files &&
        fileInput.files.length > 0
    ) {

        file =
            fileInput.files[0];

    }


    if (!file) {

        showNotification(
            "Please select a pipeline file first.",
            "error"
        );

        return;

    }


    if (
        !isSupportedFile(
            file
        )
    ) {

        showNotification(
            "Supported files: .yml, .yaml, .tf, .groovy and Jenkinsfile.",
            "error"
        );

        return;

    }


    if (
        file.size >
        5 * 1024 * 1024
    ) {

        showNotification(
            "Maximum file size is 5 MB.",
            "error"
        );

        return;

    }


    const formData =
        new FormData();


    formData.append(
        "file",
        file
    );


    showLoadingState();


    try {

        const response =
            await fetch(
                "/upload",
                {
                    method:
                        "POST",

                    body:
                        formData
                }
            );


        let data;


        try {

            data =
                await response.json();

        }
        catch (error) {

            throw new Error(
                "Server returned an invalid response."
            );

        }


        if (!response.ok) {

            throw new Error(
                data.message ||
                data.overall_message ||
                "Validation request failed."
            );

        }


        currentResult =
            data;


        displayValidationReport(
            data,
            file
        );


        /*
         * Refresh the backend-driven dashboard
         * and history after every validation.
         */

        await Promise.all([
            loadDashboard(),
            loadHistory()
        ]);


        if (
            data.overall_success === true
        ) {

            if (
                numberValue(
                    data.total_warnings
                ) > 0
            ) {

                showNotification(
                    "Validation completed with warnings.",
                    "warning"
                );

            }
            else {

                showNotification(
                    "Pipeline validation passed.",
                    "success"
                );

            }

        }
        else {

            showNotification(
                "Pipeline validation failed.",
                "error"
            );

        }

    }
    catch (error) {

        console.error(
            "PipelineGuard Error:",
            error
        );


        showValidationError(
            error.message
        );


        showNotification(
            error.message ||
            "Unable to connect to PipelineGuard server.",
            "error"
        );

    }

}


/* =========================================================
   LOADING STATE
========================================================= */

function showLoadingState() {

    const result =
        getElement(
            "result"
        );


    if (!result) {
        return;
    }


    result.innerHTML = `

        <div class="validation-loading">

            <div class="loading-spinner">
            </div>

            <h3>
                Analyzing Pipeline
            </h3>

            <p>
                Running syntax validation,
                security analysis and
                configuration checks.
            </p>

            <div class="scan-steps">

                <span>
                    ✓ Reading configuration
                </span>

                <span>
                    ✓ Detecting pipeline type
                </span>

                <span>
                    ◌ Running validator
                </span>

                <span>
                    ◌ Security scanning
                </span>

                <span>
                    ◌ Generating report
                </span>

            </div>

        </div>

    `;

}


/* =========================================================
   VALIDATION ERROR
========================================================= */

function showValidationError(message) {

    const result =
        getElement(
            "result"
        );


    if (!result) {
        return;
    }


    result.innerHTML = `

        <div class="error-state">

            <div class="state-icon">
                ⚠️
            </div>

            <h3>
                Validation Error
            </h3>

            <p>
                ${escapeHTML(message)}
            </p>

        </div>

    `;

}


/* =========================================================
   DISPLAY VALIDATION REPORT
========================================================= */

function displayValidationReport(
    data,
    file
) {

    const result =
        getElement(
            "result"
        );


    if (!result) {
        return;
    }


    const overallStatus =
        data.overall_status ||
        data.status ||
        (
            data.overall_success === true
                ? "Passed"
                : "Failed"
        );


    const pipelineType =
        formatPipelineType(
            data.detected_type ||
            data.file_type ||
            data.pipeline_type ||
            "Unknown"
        );


    const filename =
        (
            data.filename ||
            (
                file
                    ? file.name
                    : "Unknown file"
            )
        );


    const errors =
        numberValue(
            data.total_errors
        );


    const warnings =
        numberValue(
            data.total_warnings
        );


    const securityStatus =
        data.security_status ||
        "Unknown";


    const severity =
        data.security_severity ||
        "None";


    const passed =
        String(
            overallStatus
        ).toLowerCase()
        ===
        "passed";


    const statusClass =
        passed
            ? "status-passed"
            : "status-failed";


    result.innerHTML = `

        <div class="validation-result">

            <div class="result-header ${statusClass}">

                <div>

                    <span class="result-label">
                        Overall Result
                    </span>

                    <h3>
                        ${escapeHTML(
                            overallStatus
                        )}
                    </h3>

                    <p>
                        ${
                            passed
                                ? "Pipeline validation and security analysis passed."
                                : "Pipeline validation or security analysis detected problems."
                        }
                    </p>

                </div>

                <div class="result-icon">
                    ${
                        passed
                            ? "✓"
                            : "!"
                    }
                </div>

            </div>


            <div class="report-section">

                <h3>
                    Validation Summary
                </h3>


                <div class="summary-grid">

                    <div class="summary-item">

                        <span>
                            File
                        </span>

                        <strong>
                            ${escapeHTML(
                                filename
                            )}
                        </strong>

                    </div>


                    <div class="summary-item">

                        <span>
                            Pipeline Type
                        </span>

                        <strong>
                            ${escapeHTML(
                                pipelineType
                            )}
                        </strong>

                    </div>


                    <div class="summary-item">

                        <span>
                            Errors
                        </span>

                        <strong>
                            ${errors}
                        </strong>

                    </div>


                    <div class="summary-item">

                        <span>
                            Warnings
                        </span>

                        <strong>
                            ${warnings}
                        </strong>

                    </div>


                    <div class="summary-item">

                        <span>
                            Security
                        </span>

                        <strong>
                            ${escapeHTML(
                                securityStatus
                            )}
                        </strong>

                    </div>


                    <div class="summary-item">

                        <span>
                            Severity
                        </span>

                        <strong>
                            ${escapeHTML(
                                severity
                            )}
                        </strong>

                    </div>

                </div>

            </div>


            ${buildPipelineValidationSection(data)}


            ${buildValidationIssuesSection(data)}


            ${buildValidationRecommendationsSection(data)}


            ${buildSecurityAnalysisSection(data)}


            ${buildSecurityFindingsSection(data)}


            ${buildSecurityRecommendationsSection(data)}


            ${
                data.pdf_file
                    ? `
                        <div class="report-actions">

                            <button
                                type="button"
                                class="primary-btn"
                                onclick="downloadPDF(
                                    '${escapeJS(
                                        data.pdf_file
                                    )}'
                                )"
                            >
                                📄 Download PDF Report
                            </button>

                        </div>
                    `
                    : ""
            }

        </div>

    `;

}


/* =========================================================
   PIPELINE VALIDATION SECTION
========================================================= */

function buildPipelineValidationSection(data) {

    const validator =
        data.validator ||
        data.file_type ||
        "Pipeline";


    /*
     * Backend app.py returns the main pipeline
     * validation status through data.status.
     *
     * Check pipeline_status and validation_status
     * first for history/older responses, then
     * check data.status for the current API response.
     */

    const status =
        data.pipeline_status ||
        data.validation_status ||
        data.status ||
        (
            data.pipeline_success === true
                ? "Passed"
                : data.pipeline_success === false
                    ? "Failed"
                    : "Unknown"
        );


    const errors =
        numberValue(
            data.pipeline_errors ??
            data.errors
        );


    const warnings =
        numberValue(
            data.pipeline_warnings ??
            data.warnings
        );


    const message =
        data.pipeline_message ||
        data.validation_message ||
        data.result ||
        data.message ||
        "Pipeline validation completed.";


    const timestamp =
        data.timestamp ||
        "-";


    return `

        <div class="report-section">

            <h3>
                Pipeline Validation
            </h3>


            <div class="report-table">

                <div class="report-row">

                    <span>
                        Validator
                    </span>

                    <strong>
                        ${escapeHTML(
                            formatPipelineType(
                                validator
                            )
                        )}
                    </strong>

                </div>


                <div class="report-row">

                    <span>
                        Status
                    </span>

                    <strong>
                        ${escapeHTML(
                            status
                        )}
                    </strong>

                </div>


                <div class="report-row">

                    <span>
                        Errors
                    </span>

                    <strong>
                        ${errors}
                    </strong>

                </div>


                <div class="report-row">

                    <span>
                        Warnings
                    </span>

                    <strong>
                        ${warnings}
                    </strong>

                </div>


                <div class="report-row">

                    <span>
                        Result
                    </span>

                    <strong>
                        ${escapeHTML(
                            message
                        )}
                    </strong>

                </div>


                <div class="report-row">

                    <span>
                        Timestamp
                    </span>

                    <strong>
                        ${escapeHTML(
                            timestamp
                        )}
                    </strong>

                </div>

            </div>

        </div>

    `;

}


/* =========================================================
   VALIDATION ISSUES
========================================================= */

function buildValidationIssuesSection(data) {

    const issues =
        Array.isArray(
            data.issues
        )
            ? data.issues
            : [];


    if (
        issues.length === 0
    ) {

        return `

            <div class="report-section">

                <h3>
                    Validation Issues
                </h3>

                <div class="success-message">
                    ✓ No validation issues detected.
                </div>

            </div>

        `;

    }


    const items =
        issues.map(
            function (
                issue,
                index
            ) {

                let message =
                    issue;

                let line =
                    null;


                if (
                    typeof issue === "object" &&
                    issue !== null
                ) {

                    message =
                        issue.message ||
                        issue.description ||
                        JSON.stringify(
                            issue
                        );

                    line =
                        issue.line ??
                        null;

                }


                return `

                    <div class="issue-item">

                        <strong>
                            Issue ${index + 1}
                        </strong>

                        <p>
                            ${escapeHTML(
                                message
                            )}
                        </p>

                        <span>
                            Line:
                            ${
                                line !== null
                                    ? escapeHTML(line)
                                    : "-"
                            }
                        </span>

                    </div>

                `;

            }
        )
        .join("");


    return `

        <div class="report-section">

            <h3>
                Validation Issues
            </h3>

            <div class="issues-list">
                ${items}
            </div>

        </div>

    `;

}


/* =========================================================
   VALIDATION RECOMMENDATIONS
========================================================= */

function buildValidationRecommendationsSection(data) {

    const recommendations =
        Array.isArray(
            data.recommendations
        )
            ? data.recommendations
            : [];


    if (
        recommendations.length === 0
    ) {

        return `

            <div class="report-section">

                <h3>
                    Validation Recommendations
                </h3>

                <div class="success-message">
                    ✓ No recommendations required.
                </div>

            </div>

        `;

    }


    return `

        <div class="report-section">

            <h3>
                Validation Recommendations
            </h3>

            <div class="recommendations-list">

                ${
                    recommendations.map(
                        function (
                            item
                        ) {

                            return `

                                <div class="recommendation-item">

                                    → ${escapeHTML(
                                        item
                                    )}

                                </div>

                            `;

                        }
                    ).join("")
                }

            </div>

        </div>

    `;

}


/* =========================================================
   SECURITY ANALYSIS
========================================================= */

function buildSecurityAnalysisSection(data) {

    const status =
        data.security_status ||
        "Unknown";


    const severity =
        data.security_severity ||
        "None";


    const errors =
        numberValue(
            data.security_errors
        );


    const warnings =
        numberValue(
            data.security_warnings
        );


    const result =
        data.security_message ||
        (
            errors === 0 &&
            warnings === 0
                ? "No security issues detected."
                : "Security analysis detected issues."
        );


    return `

        <div class="report-section">

            <h3>
                Security Analysis
            </h3>


            <div class="report-table">

                <div class="report-row">

                    <span>
                        Status
                    </span>

                    <strong>
                        ${escapeHTML(
                            status
                        )}
                    </strong>

                </div>


                <div class="report-row">

                    <span>
                        Severity
                    </span>

                    <strong>
                        ${escapeHTML(
                            severity
                        )}
                    </strong>

                </div>


                <div class="report-row">

                    <span>
                        Security Errors
                    </span>

                    <strong>
                        ${errors}
                    </strong>

                </div>


                <div class="report-row">

                    <span>
                        Security Warnings
                    </span>

                    <strong>
                        ${warnings}
                    </strong>

                </div>


                <div class="report-row">

                    <span>
                        Result
                    </span>

                    <strong>
                        ${escapeHTML(
                            result
                        )}
                    </strong>

                </div>

            </div>

        </div>

    `;

}


/* =========================================================
   SECURITY FINDINGS
========================================================= */

function buildSecurityFindingsSection(data) {

    const findings =
        Array.isArray(
            data.security_findings
        )
            ? data.security_findings
            : [];


    if (
        findings.length === 0
    ) {

        return `

            <div class="report-section">

                <h3>
                    Security Findings
                </h3>

                <div class="success-message">
                    ✓ No security findings detected.
                </div>

            </div>

        `;

    }


    const items =
        findings.map(
            function (
                finding,
                index
            ) {

                let message =
                    "Security issue detected.";

                let severity =
                    "Unknown";

                let line =
                    null;


                if (
                    typeof finding === "object" &&
                    finding !== null
                ) {

                    message =
                        finding.message ||
                        finding.description ||
                        message;

                    severity =
                        finding.severity ||
                        severity;

                    line =
                        finding.line ??
                        null;

                }
                else {

                    message =
                        String(
                            finding
                        );

                }


                return `

                    <div class="security-finding">

                        <div class="finding-header">

                            <strong>
                                Security Finding
                                ${index + 1}
                            </strong>

                            <span class="
                                severity-badge
                                ${getSeverityClass(
                                    severity
                                )}
                            ">

                                ${escapeHTML(
                                    String(
                                        severity
                                    ).toUpperCase()
                                )}

                            </span>

                        </div>


                        <div class="finding-message">

                            ${escapeHTML(
                                message
                            )}

                        </div>


                        <div class="finding-meta">

                            Line:
                            ${
                                line !== null &&
                                line !== "" &&
                                line !== "-"
                                    ? escapeHTML(line)
                                    : "-"
                            }

                        </div>

                    </div>

                `;

            }
        )
        .join("");


    return `

        <div class="report-section">

            <h3>
                Security Findings
            </h3>


            <div class="security-findings-list">

                ${items}

            </div>

        </div>

    `;

}


/* =========================================================
   SECURITY RECOMMENDATIONS
========================================================= */

function buildSecurityRecommendationsSection(data) {

    const recommendations =
        Array.isArray(
            data.security_recommendations
        )
            ? data.security_recommendations
            : [];


    if (
        recommendations.length === 0
    ) {

        return "";

    }


    return `

        <div class="report-section">

            <h3>
                Security Recommendations
            </h3>


            <div class="recommendations-list">

                ${
                    recommendations.map(
                        function (
                            recommendation
                        ) {

                            return `

                                <div class="recommendation-item">

                                    → ${escapeHTML(
                                        recommendation
                                    )}

                                </div>

                            `;

                        }
                    ).join("")
                }

            </div>

        </div>

    `;

}


/* =========================================================
   SEVERITY CLASS
========================================================= */

function getSeverityClass(
    severity
) {

    const value =
        String(
            severity ||
            "none"
        ).toLowerCase();


    if (
        value === "critical"
    ) {

        return "severity-critical";

    }


    if (
        value === "high"
    ) {

        return "severity-high";

    }


    if (
        value === "medium"
    ) {

        return "severity-medium";

    }


    if (
        value === "low"
    ) {

        return "severity-low";

    }


    return "severity-none";

}


/* =========================================================
   FORMAT PIPELINE TYPE
========================================================= */

function formatPipelineType(type) {

    const value =
        String(
            type ||
            "Unknown"
        )
        .trim()
        .toLowerCase();


    if (
        value.includes("github")
    ) {

        return "GitHub Actions";

    }


    if (
        value.includes("gitlab")
    ) {

        return "GitLab CI";

    }


    if (
        value.includes("jenkins")
    ) {

        return "Jenkins Pipeline";

    }


    if (
        value.includes("docker")
    ) {

        return "Docker Compose";

    }


    if (
        value.includes("kubernetes") ||
        value.includes("k8s")
    ) {

        return "Kubernetes";

    }


    if (
        value.includes("terraform")
    ) {

        return "Terraform";

    }


    if (
        value === "yaml" ||
        value === "yml" ||
        value.includes("yaml")
    ) {

        return "YAML";

    }


    if (
        !value ||
        value === "unknown"
    ) {

        return "Unknown";

    }


    return type;

}


/* =========================================================
   GET RAW PIPELINE TYPE
========================================================= */

function getPipelineType(record) {

    if (
        !record ||
        typeof record !== "object"
    ) {

        return "";

    }


    return (
        record.file_type ||
        record.pipeline_type ||
        record.pipelineType ||
        record.detected_type ||
        record.detectedType ||
        record.validator ||
        ""
    );

}


/* =========================================================
   LOAD DASHBOARD
========================================================= */

async function loadDashboard() {

    try {

        const response =
            await fetch(
                "/statistics",
                {
                    method:
                        "GET",

                    cache:
                        "no-store"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Unable to load dashboard statistics."
            );

        }


        const data =
            await response.json();


        if (
            !data ||
            typeof data !== "object"
        ) {

            throw new Error(
                "Invalid statistics response."
            );

        }


        const statistics =
            data.statistics ||
            data;


        setText(
            "totalFiles",
            numberValue(
                statistics.total_validations
            )
        );


        setText(
            "passedFiles",
            numberValue(
                statistics.passed
            )
        );


        setText(
            "failedFiles",
            numberValue(
                statistics.failed
            )
        );


        setText(
            "securityIssues",
            numberValue(
                statistics.security_failed
            )
        );


        setText(
            "totalErrors",
            numberValue(
                statistics.total_errors
            )
        );


        setText(
            "totalWarnings",
            numberValue(
                statistics.total_warnings
            )
        );

    }
    catch (error) {

        console.error(
            "Dashboard error:",
            error
        );

    }

}


/* =========================================================
   LOAD HISTORY
========================================================= */

async function loadHistory() {

    const tableBody =
        getElement(
            "historyTableBody"
        );


    if (tableBody) {

        tableBody.innerHTML = `

            <tr>

                <td
                    colspan="8"
                    class="history-empty-cell"
                >
                    Loading validation history...
                </td>

            </tr>

        `;

    }


    try {

        const response =
            await fetch(
                "/history",
                {
                    method:
                        "GET",

                    cache:
                        "no-store"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Unable to load validation history."
            );

        }


        const responseData =
            await response.json();


        let history;


        if (
            Array.isArray(
                responseData
            )
        ) {

            history =
                responseData;

        }
        else if (
            responseData &&
            Array.isArray(
                responseData.history
            )
        ) {

            history =
                responseData.history;

        }
        else {

            history = [];

        }


        renderHistory(
            history
        );


        updatePipelineBreakdown(
            history
        );

    }
    catch (error) {

        console.error(
            "History error:",
            error
        );


        if (tableBody) {

            tableBody.innerHTML = `

                <tr>

                    <td
                        colspan="8"
                        class="history-empty-cell"
                    >
                        Unable to load validation history.
                    </td>

                </tr>

            `;

        }


        updatePipelineBreakdown(
            []
        );

    }

}


/* =========================================================
   RENDER HISTORY
========================================================= */

function renderHistory(
    history
) {

    const tableBody =
        getElement(
            "historyTableBody"
        );


    if (!tableBody) {

        return;

    }


    if (
        !Array.isArray(history) ||
        history.length === 0
    ) {

        tableBody.innerHTML = `

            <tr>

                <td
                    colspan="8"
                    class="history-empty-cell"
                >
                    No validation history yet.
                </td>

            </tr>

        `;

        return;

    }


    tableBody.innerHTML =
        history.map(
            function (
                entry,
                index
            ) {

                const status =
                    entry.overall_status ||
                    entry.status ||
                    "Unknown";


                const passed =
                    String(
                        status
                    )
                    .toLowerCase()
                    ===
                    "passed";


                const pipeline =
                    formatPipelineType(
                        getPipelineType(
                            entry
                        )
                    );


                const errors =
                    numberValue(
                        entry.total_errors ??
                        entry.errors
                    );


                const warnings =
                    numberValue(
                        entry.total_warnings ??
                        entry.warnings
                    );


                const securityStatus =
                    entry.security_status ||
                    "None";


                const severity =
                    entry.security_severity ||
                    entry.severity ||
                    "None";


                const timestamp =
                    entry.timestamp ||
                    "-";


                const pdfFile =
                    entry.pdf_file ||
                    entry.pdf_filename ||
                    "";


                return `

                    <tr>


                        <td>
                            ${escapeHTML(
                                entry.filename ||
                                "Unknown file"
                            )}
                        </td>


                        <td>
                            ${escapeHTML(
                                pipeline
                            )}
                        </td>


                        <td>

                            <span class="
                                history-status
                                ${
                                    passed
                                        ? "history-pass"
                                        : "history-fail"
                                }
                            ">

                                ${
                                    passed
                                        ? "✓ Passed"
                                        : "✕ Failed"
                                }

                            </span>

                        </td>


                        <td>

                            <span class="
                                history-count
                                history-error-count
                            ">
                                ${errors}
                            </span>

                        </td>


                        <td>

                            <span class="
                                history-count
                                history-warning-count
                            ">
                                ${warnings}
                            </span>

                        </td>


                        <td>

                            <span class="
                                severity-badge
                                ${getSeverityClass(
                                    severity
                                )}
                            ">

                                ${escapeHTML(
                                    String(
                                        severity
                                    ).toUpperCase()
                                )}

                            </span>

                        </td>


                        <td>
                            ${escapeHTML(
                                timestamp
                            )}
                        </td>


                        <td>

                            <div class="
                                history-row-actions
                            ">


                                <button
                                    type="button"
                                    class="
                                        history-action-btn
                                        history-view-btn
                                    "
                                    onclick="
                                        viewHistoryRecord(
                                            ${index}
                                        )
                                    "
                                    title="View report"
                                >
                                    👁
                                </button>


                                ${
                                    pdfFile
                                        ? `
                                            <button
                                                type="button"
                                                class="
                                                    history-action-btn
                                                "
                                                onclick="
                                                    downloadPDF(
                                                        '${escapeJS(
                                                            pdfFile
                                                        )}'
                                                    )
                                                "
                                                title="Download PDF"
                                            >
                                                📄
                                            </button>
                                        `
                                        : ""
                                }


                                <button
                                    type="button"
                                    class="
                                        history-action-btn
                                        history-delete-btn
                                    "
                                    onclick="
                                        deleteHistoryRecord(
                                            ${index}
                                        )
                                    "
                                    title="Delete record"
                                >
                                    🗑
                                </button>


                            </div>

                        </td>


                    </tr>

                `;

            }
        )
        .join("");

}


/* =========================================================
   PIPELINE TYPE BREAKDOWN
========================================================= */

function updatePipelineBreakdown(
    history
) {

    const counts = {

        github:
            0,

        gitlab:
            0,

        jenkins:
            0,

        docker:
            0,

        kubernetes:
            0,

        terraform:
            0,

        yaml:
            0,

        other:
            0

    };


    if (
        Array.isArray(history)
    ) {

        history.forEach(
            function (record) {

                const type =
                    getPipelineType(
                        record
                    )
                    .toLowerCase();


                if (
                    type.includes("github")
                ) {

                    counts.github++;

                }
                else if (
                    type.includes("gitlab")
                ) {

                    counts.gitlab++;

                }
                else if (
                    type.includes("jenkins")
                ) {

                    counts.jenkins++;

                }
                else if (
                    type.includes("docker")
                ) {

                    counts.docker++;

                }
                else if (
                    type.includes("kubernetes") ||
                    type.includes("k8s")
                ) {

                    counts.kubernetes++;

                }
                else if (
                    type.includes("terraform")
                ) {

                    counts.terraform++;

                }
                else if (
                    type === "yaml" ||
                    type === "yml" ||
                    type.includes("yaml")
                ) {

                    counts.yaml++;

                }
                else {

                    counts.other++;

                }

            }
        );

    }


    setText(
        "githubCount",
        counts.github
    );


    setText(
        "gitlabCount",
        counts.gitlab
    );


    setText(
        "jenkinsCount",
        counts.jenkins
    );


    setText(
        "dockerCount",
        counts.docker
    );


    setText(
        "kubernetesCount",
        counts.kubernetes
    );


    setText(
        "terraformCount",
        counts.terraform
    );


    setText(
        "yamlCount",
        counts.yaml
    );


    setText(
        "otherCount",
        counts.other
    );

}


/* =========================================================
   VIEW HISTORY RECORD
========================================================= */

async function viewHistoryRecord(
    index
) {

    try {

        const response =
            await fetch(
                "/history/"
                +
                encodeURIComponent(
                    index
                ),
                {
                    method:
                        "GET",

                    cache:
                        "no-store"
                }
            );


        let data;


        try {

            data =
                await response.json();

        }
        catch (error) {

            throw new Error(
                "Server returned an invalid response."
            );

        }


        if (!response.ok) {

            throw new Error(
                data.message ||
                "Unable to load previous report."
            );

        }


        let record =
            null;


        if (
            data &&
            data.record &&
            typeof data.record === "object"
        ) {

            record =
                data.record;

        }
        else if (
            data &&
            typeof data === "object" &&
            (
                data.filename ||
                data.overall_status ||
                data.status
            )
        ) {

            record =
                data;

        }


        if (!record) {

            throw new Error(
                "History report data is unavailable."
            );

        }


        currentResult =
            record;


        displayValidationReport(
            record,
            null
        );


        scrollToValidationReport();


        showNotification(
            "Previous validation report loaded.",
            "success"
        );

    }
    catch (error) {

        console.error(
            "View history error:",
            error
        );


        showNotification(
            error.message ||
            "Unable to load previous report.",
            "error"
        );

    }

}


/* =========================================================
   SCROLL TO REPORT
========================================================= */

function scrollToValidationReport() {

    const result =
        getElement(
            "result"
        );


    if (!result) {
        return;
    }


    const reportCard =
        result.closest(
            ".card"
        );


    if (reportCard) {

        reportCard.scrollIntoView({
            behavior:
                "smooth",

            block:
                "start"
        });

    }
    else {

        result.scrollIntoView({
            behavior:
                "smooth",

            block:
                "start"
        });

    }

}


/* =========================================================
   DELETE HISTORY RECORD
========================================================= */

async function deleteHistoryRecord(
    index
) {

    const confirmed =
        confirm(
            "Delete this validation history record?"
        );


    if (!confirmed) {
        return;
    }


    try {

        const response =
            await fetch(
                "/history/"
                +
                encodeURIComponent(
                    index
                ),
                {
                    method:
                        "DELETE"
                }
            );


        let data;


        try {

            data =
                await response.json();

        }
        catch (error) {

            throw new Error(
                "Server returned an invalid response."
            );

        }


        if (!response.ok) {

            throw new Error(
                data.message ||
                "Unable to delete history record."
            );

        }


        showNotification(
            "History record deleted.",
            "success"
        );


        await Promise.all([
            loadHistory(),
            loadDashboard()
        ]);

    }
    catch (error) {

        console.error(
            "Delete history error:",
            error
        );


        showNotification(
            error.message ||
            "Unable to delete history record.",
            "error"
        );

    }

}


/* =========================================================
   CLEAR ALL HISTORY
========================================================= */

async function clearHistory() {

    const confirmed =
        confirm(
            "Are you sure you want to clear all validation history?"
        );


    if (!confirmed) {
        return;
    }


    try {

        const response =
            await fetch(
                "/history",
                {
                    method:
                        "DELETE"
                }
            );


        let data;


        try {

            data =
                await response.json();

        }
        catch (error) {

            throw new Error(
                "Server returned an invalid response."
            );

        }


        if (!response.ok) {

            throw new Error(
                data.message ||
                "Unable to clear history."
            );

        }


        showNotification(
            "Validation history cleared successfully.",
            "success"
        );


        await Promise.all([
            loadHistory(),
            loadDashboard()
        ]);

    }
    catch (error) {

        console.error(
            "Clear history error:",
            error
        );


        showNotification(
            error.message ||
            "Unable to clear validation history.",
            "error"
        );

    }

}


/* =========================================================
   DOWNLOAD PDF
========================================================= */

function downloadPDF(
    filename
) {

    if (!filename) {

        showNotification(
            "PDF report is not available.",
            "error"
        );

        return;

    }


    window.location.href =
        "/download/"
        +
        encodeURIComponent(
            filename
        );

}


/* =========================================================
   ESCAPE JAVASCRIPT STRING
========================================================= */

function escapeJS(value) {

    return String(
        value || ""
    )
    .replaceAll(
        "\\",
        "\\\\"
    )
    .replaceAll(
        "'",
        "\\'"
    )
    .replaceAll(
        "\n",
        "\\n"
    )
    .replaceAll(
        "\r",
        "\\r"
    );

}


/* =========================================================
   THEME
========================================================= */

function setupTheme() {

    const savedTheme =
        localStorage.getItem(
            "pipelineguardTheme"
        );


    if (
        savedTheme === "light"
    ) {

        document.body.classList.remove(
            "dark-mode"
        );

    }
    else {

        document.body.classList.add(
            "dark-mode"
        );

    }


    updateThemeButton();

}


/* =========================================================
   TOGGLE THEME
========================================================= */

function toggleTheme() {

    document.body.classList.toggle(
        "dark-mode"
    );


    const isDark =
        document.body.classList.contains(
            "dark-mode"
        );


    localStorage.setItem(
        "pipelineguardTheme",
        isDark
            ? "dark"
            : "light"
    );


    updateThemeButton();

}


/* =========================================================
   THEME BUTTON
========================================================= */

function updateThemeButton() {

    const button =
        getElement(
            "themeToggle"
        );


    if (!button) {
        return;
    }


    const isDark =
        document.body.classList.contains(
            "dark-mode"
        );


    button.textContent =
        isDark
            ? "☀️"
            : "🌙";


    button.title =
        isDark
            ? "Switch to light mode"
            : "Switch to dark mode";

}


/* =========================================================
   NOTIFICATIONS
========================================================= */

function showNotification(
    message,
    type
) {

    const container =
        getElement(
            "notificationContainer"
        );


    if (!container) {
        return;
    }


    const notification =
        document.createElement(
            "div"
        );


    notification.className =
        "notification "
        +
        (
            type ||
            "info"
        );


    notification.textContent =
        message;


    container.appendChild(
        notification
    );


    setTimeout(
        function () {

            notification.classList.add(
                "show"
            );

        },
        10
    );


    setTimeout(
        function () {

            notification.classList.remove(
                "show"
            );


            setTimeout(
                function () {

                    notification.remove();

                },
                300
            );

        },
        3500
    );

}