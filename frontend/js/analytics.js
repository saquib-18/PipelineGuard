/* =========================================================
   PIPELINEGUARD ANALYTICS
   analytics.js
   ========================================================= */


/* =========================================================
   GLOBAL DATA
========================================================= */

let validationChart = null;
let securityChart = null;
let findingsChart = null;

let analyticsHistory = [];



/* =========================================================
   PAGE INITIALIZATION
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    initializeAnalyticsTheme();

    setupAnalyticsButtons();

    refreshAnalytics();

});



/* =========================================================
   SETUP BUTTONS
========================================================= */

function setupAnalyticsButtons() {

    const refreshButtons = [
        "refreshAnalyticsBtn",
        "refreshAnalytics",
        "refreshActivityBtn",
        "refreshActivity"
    ];

    refreshButtons.forEach(function (id) {

        const button = document.getElementById(id);

        if (!button) {
            return;
        }

        button.addEventListener("click", function () {
            refreshAnalytics();
        });

    });


    const themeButton =
        document.getElementById("themeToggle");

    if (themeButton) {

        themeButton.addEventListener(
            "click",
            toggleAnalyticsTheme
        );

    }

}



/* =========================================================
   REFRESH EVERYTHING
========================================================= */

async function refreshAnalytics() {

    try {

        await loadAnalyticsStatistics();

        await loadAnalyticsHistory();

        updateAnalyticsCharts();

    } catch (error) {

        console.error(
            "Analytics refresh error:",
            error
        );

        showAnalyticsNotification(
            "Unable to load analytics data.",
            "error"
        );

    }

}



/* =========================================================
   LOAD STATISTICS
========================================================= */

async function loadAnalyticsStatistics() {

    try {

        const response = await fetch(
            "/statistics",
            {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                }
            }
        );


        if (!response.ok) {

            throw new Error(
                "Statistics request failed: " +
                response.status
            );

        }


        const data =
            await response.json();


        console.log(
            "Analytics statistics response:",
            data
        );


        /*
         * IMPORTANT
         *
         * Backend can return:
         *
         * {
         *     "statistics": {
         *         "total_validations": 3,
         *         "passed": 2,
         *         ...
         *     },
         *     "success": true
         * }
         *
         * OR a flat object.
         */


        let statistics = data;


        if (
            data &&
            typeof data.statistics === "object"
        ) {

            statistics =
                data.statistics;

        }


        updateStatisticsUI(
            statistics
        );


        return statistics;


    } catch (error) {

        console.error(
            "Statistics loading error:",
            error
        );


        /*
         * Keep dashboard usable.
         */

        updateStatisticsUI({

            total_validations: 0,

            passed: 0,

            failed: 0,

            security_passed: 0,

            security_failed: 0,

            total_errors: 0,

            total_warnings: 0

        });


        throw error;

    }

}



/* =========================================================
   UPDATE STATISTICS UI
========================================================= */

function updateStatisticsUI(data) {

    if (
        !data ||
        typeof data !== "object"
    ) {

        data = {};

    }


    const total =
        toNumber(
            firstValue(
                data.total_validations,
                data.totalValidations,
                data.total,
                0
            )
        );


    const passed =
        toNumber(
            firstValue(
                data.passed,
                data.successful,
                data.success,
                0
            )
        );


    const failed =
        toNumber(
            firstValue(
                data.failed,
                data.failures,
                0
            )
        );


    const securityPassed =
        toNumber(
            firstValue(
                data.security_passed,
                data.securityPassed,
                0
            )
        );


    const securityFailed =
        toNumber(
            firstValue(
                data.security_failed,
                data.securityFailed,
                0
            )
        );


    const totalErrors =
        toNumber(
            firstValue(
                data.total_errors,
                data.totalErrors,
                data.errors,
                0
            )
        );


    const totalWarnings =
        toNumber(
            firstValue(
                data.total_warnings,
                data.totalWarnings,
                data.warnings,
                0
            )
        );



    /* =====================================================
       PRIMARY STATISTICS
    ===================================================== */

    setText(
        "analyticsTotalValidations",
        total
    );


    setText(
        "analyticsTotalPassed",
        passed
    );


    setText(
        "analyticsTotalFailed",
        failed
    );


    setText(
        "analyticsTotalSecurityFailed",
        securityFailed
    );


    setText(
        "analyticsTotalErrors",
        totalErrors
    );


    setText(
        "analyticsTotalWarnings",
        totalWarnings
    );



    /* =====================================================
       RATES
    ===================================================== */

    const passRate =
        total > 0
            ? (passed / total) * 100
            : 0;


    const failureRate =
        total > 0
            ? (failed / total) * 100
            : 0;


    const securityTotal =
        securityPassed +
        securityFailed;


    const securityFailureRate =
        securityTotal > 0
            ? (securityFailed / securityTotal) * 100
            : 0;


    setText(
        "passRate",
        formatPercentage(passRate)
    );


    setText(
        "failureRate",
        formatPercentage(failureRate)
    );


    setText(
        "securityFailureRate",
        formatPercentage(securityFailureRate)
    );



    /* =====================================================
       VALIDATION PERFORMANCE
    ===================================================== */

    setText(
        "analyticsPassed",
        passed
    );


    setText(
        "analyticsFailed",
        failed
    );


    setText(
        "analyticsSecurityFailed",
        securityFailed
    );


    setProgress(
        "passedProgress",
        total > 0
            ? (passed / total) * 100
            : 0
    );


    setProgress(
        "failedProgress",
        total > 0
            ? (failed / total) * 100
            : 0
    );


    setProgress(
        "securityProgress",
        total > 0
            ? (securityFailed / total) * 100
            : 0
    );



    /* =====================================================
       CHART SUMMARY NUMBERS
    ===================================================== */

    setText(
        "chartPassedCount",
        passed
    );


    setText(
        "chartFailedCount",
        failed
    );


    setText(
        "chartSecurityPassed",
        securityPassed
    );


    setText(
        "chartSecurityFailed",
        securityFailed
    );


    setText(
        "chartErrorsCount",
        totalErrors
    );


    setText(
        "chartWarningsCount",
        totalWarnings
    );

}



/* =========================================================
   LOAD HISTORY
========================================================= */

async function loadAnalyticsHistory() {

    try {

        const response =
            await fetch(
                "/history",
                {
                    method: "GET",
                    headers: {
                        "Accept":
                            "application/json"
                    }
                }
            );


        if (!response.ok) {

            throw new Error(
                "History request failed: " +
                response.status
            );

        }


        const data =
            await response.json();


        console.log(
            "Analytics history response:",
            data
        );


        /*
         * Backend can return:
         *
         * [
         *     {...},
         *     {...}
         * ]
         *
         * OR:
         *
         * {
         *     "history": [...]
         * }
         *
         * OR:
         *
         * {
         *     "data": [...]
         * }
         */


        if (
            Array.isArray(data)
        ) {

            analyticsHistory =
                data;

        } else if (
            data &&
            Array.isArray(
                data.history
            )
        ) {

            analyticsHistory =
                data.history;

        } else if (
            data &&
            Array.isArray(
                data.data
            )
        ) {

            analyticsHistory =
                data.data;

        } else {

            analyticsHistory = [];

        }


        renderRecentActivity(
            analyticsHistory
        );


        updatePipelineBreakdown(
            analyticsHistory
        );


        updateAnalyticsCharts();


        return analyticsHistory;


    } catch (error) {

        console.error(
            "History loading error:",
            error
        );


        analyticsHistory = [];


        renderRecentActivity([]);

        updatePipelineBreakdown([]);

        throw error;

    }

}



/* =========================================================
   RENDER RECENT ACTIVITY
========================================================= */

function renderRecentActivity(history) {

    const tbody =
        document.getElementById(
            "recentActivityBody"
        );


    if (!tbody) {

        return;

    }


    tbody.innerHTML = "";


    if (
        !Array.isArray(history) ||
        history.length === 0
    ) {

        const row =
            document.createElement(
                "tr"
            );


        row.innerHTML = `
            <td
                colspan="8"
                class="history-empty-cell"
            >

                <div
                    class="analytics-empty"
                >

                    <span
                        class="analytics-empty-icon"
                    >
                        🕘
                    </span>

                    <strong>
                        No validation activity yet
                    </strong>

                    <br>

                    <span>
                        Validate a pipeline from
                        the main page to see activity here.
                    </span>

                </div>

            </td>
        `;


        tbody.appendChild(row);


        return;

    }


    /*
     * Latest 10 activities.
     */

    const recent =
        history.slice(0, 10);


    recent.forEach(
        function (record) {

            if (
                !record ||
                typeof record !== "object"
            ) {

                return;

            }


            const row =
                document.createElement(
                    "tr"
                );


            const fileName =
                getFileName(record);


            const pipelineType =
                getPipelineType(record);


            const status =
                getOverallStatus(record);


            const errors =
                getErrors(record);


            const warnings =
                getWarnings(record);


            const securityStatus =
                getSecurityStatus(record);


            const severity =
                getSeverity(record);


            const date =
                getDate(record);


            row.innerHTML = `

                <td>

                    <span
                        class="analytics-file-name"
                        title="${escapeHtml(fileName)}"
                    >
                        ${escapeHtml(fileName)}
                    </span>

                </td>


                <td>
                    ${escapeHtml(pipelineType)}
                </td>


                <td>
                    ${createStatusBadge(status)}
                </td>


                <td>

                    <span
                        class="analytics-number analytics-error-number"
                    >
                        ${errors}
                    </span>

                </td>


                <td>

                    <span
                        class="analytics-number analytics-warning-number"
                    >
                        ${warnings}
                    </span>

                </td>


                <td>
                    ${createSecurityBadge(
                        securityStatus
                    )}
                </td>


                <td>
                    ${createSeverityBadge(
                        severity
                    )}
                </td>


                <td>
                    ${escapeHtml(date)}
                </td>

            `;


            tbody.appendChild(row);

        }
    );

}



/* =========================================================
   PIPELINE TYPE BREAKDOWN
========================================================= */

function updatePipelineBreakdown(history) {

    const counts = {

        github: 0,

        gitlab: 0,

        jenkins: 0,

        docker: 0,

        kubernetes: 0,

        terraform: 0,

        yaml: 0,

        other: 0

    };


    if (
        Array.isArray(history)
    ) {

        history.forEach(
            function (record) {

                const type =
                    getPipelineType(record)
                        .toLowerCase();


                if (
                    type.includes("github")
                ) {

                    counts.github++;

                } else if (
                    type.includes("gitlab")
                ) {

                    counts.gitlab++;

                } else if (
                    type.includes("jenkins")
                ) {

                    counts.jenkins++;

                } else if (
                    type.includes("docker")
                ) {

                    counts.docker++;

                } else if (
                    type.includes("kubernetes") ||
                    type.includes("k8s")
                ) {

                    counts.kubernetes++;

                } else if (
                    type.includes("terraform")
                ) {

                    counts.terraform++;

                } else if (
                    type.includes("yaml") ||
                    type.includes("yml")
                ) {

                    counts.yaml++;

                } else {

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
   UPDATE ALL CHARTS
========================================================= */

function updateAnalyticsCharts() {

    const statistics =
        calculateHistoryStatistics();


    updateValidationChart(
        statistics
    );


    updateSecurityChart(
        statistics
    );


    updateFindingsChart(
        statistics
    );

}



/* =========================================================
   CALCULATE HISTORY STATISTICS
========================================================= */

function calculateHistoryStatistics() {

    const result = {

        passed: 0,

        failed: 0,

        securityPassed: 0,

        securityFailed: 0,

        errors: 0,

        warnings: 0

    };


    if (
        !Array.isArray(
            analyticsHistory
        )
    ) {

        return result;

    }


    analyticsHistory.forEach(
        function (record) {

            if (
                !record ||
                typeof record !== "object"
            ) {

                return;

            }


            const status =
                getOverallStatus(record)
                    .toLowerCase();


            if (
                status === "passed" ||
                status === "pass" ||
                status === "success"
            ) {

                result.passed++;

            } else {

                result.failed++;

            }


            const security =
                getSecurityStatus(record)
                    .toLowerCase();


            if (
                security === "passed" ||
                security === "pass" ||
                security === "secure" ||
                security === "success"
            ) {

                result.securityPassed++;

            } else if (
                security === "failed" ||
                security === "fail"
            ) {

                result.securityFailed++;

            }


            result.errors +=
                getErrors(record);


            result.warnings +=
                getWarnings(record);

        }
    );


    return result;

}



/* =========================================================
   VALIDATION CHART
========================================================= */

function updateValidationChart(
    statistics
) {

    const canvas =
        document.getElementById(
            "validationChart"
        );


    if (!canvas) {

        return;

    }


    if (
        typeof Chart === "undefined"
    ) {

        console.warn(
            "Chart.js is not loaded."
        );

        return;

    }


    if (validationChart) {

        validationChart.destroy();

    }


    validationChart =
        new Chart(
            canvas,
            {

                type: "doughnut",

                data: {

                    labels: [
                        "Passed",
                        "Failed"
                    ],

                    datasets: [

                        {

                            data: [

                                statistics.passed,

                                statistics.failed

                            ],

                            backgroundColor: [

                                "#22c55e",

                                "#ef4444"

                            ],

                            borderWidth: 0

                        }

                    ]

                },


                options: {

                    responsive: true,

                    maintainAspectRatio:
                        false,

                    cutout: "65%",

                    plugins: {

                        legend: {

                            position:
                                "bottom",

                            labels: {

                                padding: 18,

                                usePointStyle:
                                    true

                            }

                        }

                    }

                }

            }
        );

}



/* =========================================================
   SECURITY CHART
========================================================= */

function updateSecurityChart(
    statistics
) {

    const canvas =
        document.getElementById(
            "securityChart"
        );


    if (!canvas) {

        return;

    }


    if (
        typeof Chart === "undefined"
    ) {

        return;

    }


    if (securityChart) {

        securityChart.destroy();

    }


    securityChart =
        new Chart(
            canvas,
            {

                type: "doughnut",

                data: {

                    labels: [
                        "Security Passed",
                        "Security Failed"
                    ],

                    datasets: [

                        {

                            data: [

                                statistics.securityPassed,

                                statistics.securityFailed

                            ],

                            backgroundColor: [

                                "#22c55e",

                                "#f59e0b"

                            ],

                            borderWidth: 0

                        }

                    ]

                },


                options: {

                    responsive: true,

                    maintainAspectRatio:
                        false,

                    cutout: "65%",

                    plugins: {

                        legend: {

                            position:
                                "bottom",

                            labels: {

                                padding: 18,

                                usePointStyle:
                                    true

                            }

                        }

                    }

                }

            }
        );

}



/* =========================================================
   FINDINGS CHART
========================================================= */

function updateFindingsChart(
    statistics
) {

    const canvas =
        document.getElementById(
            "findingsChart"
        );


    if (!canvas) {

        return;

    }


    if (
        typeof Chart === "undefined"
    ) {

        return;

    }


    if (findingsChart) {

        findingsChart.destroy();

    }


    findingsChart =
        new Chart(
            canvas,
            {

                type: "bar",

                data: {

                    labels: [
                        "Errors",
                        "Warnings"
                    ],

                    datasets: [

                        {

                            label:
                                "Validation Findings",

                            data: [

                                statistics.errors,

                                statistics.warnings

                            ],

                            backgroundColor: [

                                "#ef4444",

                                "#f59e0b"

                            ],

                            borderRadius: 8,

                            borderSkipped: false

                        }

                    ]

                },


                options: {

                    responsive: true,

                    maintainAspectRatio:
                        false,

                    scales: {

                        y: {

                            beginAtZero: true,

                            ticks: {

                                precision: 0

                            }

                        }

                    },


                    plugins: {

                        legend: {

                            display: false

                        }

                    }

                }

            }
        );

}



/* =========================================================
   GET FILE NAME
========================================================= */

function getFileName(record) {

    return firstValue(

        record.file_name,

        record.filename,

        record.fileName,

        record.pdf_filename,

        record.pdfFileName,

        record.name,

        "Unknown file"

    );

}



/* =========================================================
   GET PIPELINE TYPE
========================================================= */

function getPipelineType(record) {

    return firstValue(

        record.pipeline_type,

        record.pipelineType,

        record.type,

        record.detected_type,

        record.detectedType,

        record.pipeline,

        record.file_type,

        record.fileType,

        "Unknown"

    );

}



/* =========================================================
   GET OVERALL STATUS
========================================================= */

function getOverallStatus(record) {

    return firstValue(

        record.overall_status,

        record.overallStatus,

        record.status,

        record.validation_status,

        record.validationStatus,

        "Unknown"

    );

}



/* =========================================================
   GET SECURITY STATUS
========================================================= */

function getSecurityStatus(record) {

    return firstValue(

        record.security_status,

        record.securityStatus,

        record.security_result,

        record.securityResult,

        record.security,

        "Unknown"

    );

}



/* =========================================================
   GET ERRORS
========================================================= */

function getErrors(record) {

    const value =
        firstValue(

            record.total_errors,

            record.totalErrors,

            record.errors_count,

            record.error_count,

            record.errorCount,

            record.errors,

            0

        );


    if (
        typeof value === "object" &&
        value !== null
    ) {

        /*
         * If errors is an array,
         * count the items.
         */

        if (
            Array.isArray(value)
        ) {

            return value.length;

        }


        /*
         * If errors is an object,
         * count its entries.
         */

        return Object.keys(value).length;

    }


    return toNumber(value);

}



/* =========================================================
   GET WARNINGS
========================================================= */

function getWarnings(record) {

    const value =
        firstValue(

            record.total_warnings,

            record.totalWarnings,

            record.warnings_count,

            record.warning_count,

            record.warningCount,

            record.warnings,

            0

        );


    if (
        typeof value === "object" &&
        value !== null
    ) {

        if (
            Array.isArray(value)
        ) {

            return value.length;

        }


        return Object.keys(value).length;

    }


    return toNumber(value);

}



/* =========================================================
   GET SEVERITY
========================================================= */

function getSeverity(record) {

    const direct =
        firstValue(

            record.severity,

            record.max_severity,

            record.maxSeverity,

            record.security_severity,

            record.securitySeverity

        );


    if (
        direct !== null &&
        direct !== undefined &&
        String(direct).trim() !== ""
    ) {

        return String(direct);

    }


    const errors =
        getErrors(record);


    if (
        errors > 0
    ) {

        return "High";

    }


    const warnings =
        getWarnings(record);


    if (
        warnings > 0
    ) {

        return "Medium";

    }


    return "None";

}



/* =========================================================
   GET DATE
========================================================= */

function getDate(record) {

    const value =
        firstValue(

            record.timestamp,

            record.date,

            record.datetime,

            record.created_at,

            record.createdAt,

            record.time,

            record.validation_time,

            record.validationTime,

            ""

        );


    if (!value) {

        return "Unknown";

    }


    try {

        const date =
            new Date(value);


        if (
            !Number.isNaN(
                date.getTime()
            )
        ) {

            return date.toLocaleString();

        }

    } catch (error) {

        console.warn(
            "Date formatting error:",
            error
        );

    }


    return String(value);

}



/* =========================================================
   CREATE STATUS BADGE
========================================================= */

function createStatusBadge(
    status
) {

    const normalized =
        String(status)
            .trim()
            .toLowerCase();


    if (
        normalized === "passed" ||
        normalized === "pass" ||
        normalized === "success"
    ) {

        return `
            <span
                class="analytics-status analytics-status-pass"
            >
                ✓ Passed
            </span>
        `;

    }


    if (
        normalized === "failed" ||
        normalized === "fail" ||
        normalized === "error"
    ) {

        return `
            <span
                class="analytics-status analytics-status-fail"
            >
                ✕ Failed
            </span>
        `;

    }


    return `
        <span
            class="analytics-status"
        >
            ${escapeHtml(status)}
        </span>
    `;

}



/* =========================================================
   CREATE SECURITY BADGE
========================================================= */

function createSecurityBadge(
    status
) {

    const normalized =
        String(status)
            .trim()
            .toLowerCase();


    if (
        normalized === "passed" ||
        normalized === "pass" ||
        normalized === "secure" ||
        normalized === "success"
    ) {

        return `
            <span
                class="analytics-security-pass"
            >
                ✓ Passed
            </span>
        `;

    }


    if (
        normalized === "failed" ||
        normalized === "fail"
    ) {

        return `
            <span
                class="analytics-security-fail"
            >
                ⚠ Failed
            </span>
        `;

    }


    return `
        <span>
            ${escapeHtml(status)}
        </span>
    `;

}



/* =========================================================
   CREATE SEVERITY BADGE
========================================================= */

function createSeverityBadge(
    severity
) {

    const normalized =
        String(severity)
            .trim()
            .toLowerCase();


    let className =
        "analytics-severity-none";


    if (
        normalized === "low"
    ) {

        className =
            "analytics-severity-low";

    } else if (
        normalized === "medium"
    ) {

        className =
            "analytics-severity-medium";

    } else if (
        normalized === "high"
    ) {

        className =
            "analytics-severity-high";

    } else if (
        normalized === "critical"
    ) {

        className =
            "analytics-severity-critical";

    }


    return `
        <span
            class="analytics-severity ${className}"
        >
            ${escapeHtml(severity)}
        </span>
    `;

}



/* =========================================================
   THEME
========================================================= */

function initializeAnalyticsTheme() {

    const savedTheme =
        localStorage.getItem(
            "pipelineguard-theme"
        );


    if (
        savedTheme === "dark"
    ) {

        document.body.classList.add(
            "dark-mode"
        );

        updateThemeIcon(true);

    } else {

        document.body.classList.remove(
            "dark-mode"
        );

        updateThemeIcon(false);

    }

}



/* =========================================================
   TOGGLE THEME
========================================================= */

function toggleAnalyticsTheme() {

    const darkMode =
        document.body.classList.toggle(
            "dark-mode"
        );


    localStorage.setItem(
        "pipelineguard-theme",
        darkMode
            ? "dark"
            : "light"
    );


    updateThemeIcon(
        darkMode
    );


    updateAnalyticsCharts();

}



/* =========================================================
   UPDATE THEME ICON
========================================================= */

function updateThemeIcon(
    isDark
) {

    const button =
        document.getElementById(
            "themeToggle"
        );


    if (!button) {

        return;

    }


    button.textContent =
        isDark
            ? "☀️"
            : "🌙";

}



/* =========================================================
   NOTIFICATION
========================================================= */

function showAnalyticsNotification(
    message,
    type = "info"
) {

    const container =
        document.getElementById(
            "notificationContainer"
        );


    if (!container) {

        console.log(
            message
        );

        return;

    }


    const notification =
        document.createElement(
            "div"
        );


    notification.className =
        "notification " +
        "notification-" +
        type;


    notification.textContent =
        message;


    container.appendChild(
        notification
    );


    setTimeout(
        function () {

            notification.remove();

        },
        3500
    );

}



/* =========================================================
   SET TEXT
========================================================= */

function setText(
    id,
    value
) {

    const element =
        document.getElementById(
            id
        );


    if (!element) {

        return;

    }


    element.textContent =
        value;

}



/* =========================================================
   SET PROGRESS
========================================================= */

function setProgress(
    id,
    percentage
) {

    const element =
        document.getElementById(
            id
        );


    if (!element) {

        return;

    }


    const safePercentage =
        Math.max(
            0,
            Math.min(
                100,
                Number(percentage) || 0
            )
        );


    element.style.width =
        safePercentage + "%";

}



/* =========================================================
   NUMBER CONVERSION
========================================================= */

function toNumber(value) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {

        return 0;

    }


    const number =
        Number(value);


    return Number.isFinite(number)
        ? number
        : 0;

}



/* =========================================================
   PERCENTAGE FORMAT
========================================================= */

function formatPercentage(
    value
) {

    const number =
        Number(value) || 0;


    return (
        Math.round(
            number * 10
        ) / 10
    ) + "%";

}



/* =========================================================
   FIRST VALID VALUE
========================================================= */

function firstValue(
    ...values
) {

    for (
        const value of values
    ) {

        if (
            value !== undefined &&
            value !== null &&
            value !== ""
        ) {

            return value;

        }

    }


    return "";

}



/* =========================================================
   ESCAPE HTML
========================================================= */

function escapeHtml(
    value
) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}