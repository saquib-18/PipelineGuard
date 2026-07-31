async function uploadFile() {

    const fileInput = document.getElementById("fileInput");
    const result = document.getElementById("result");

    if (fileInput.files.length === 0) {
        result.innerHTML = `
            <p style="color:red;">
                Please choose a file.
            </p>
        `;
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    result.innerHTML = "<h3>⏳ Validating...</h3>";

    try {

        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        const validationColor =
            data.status === "Passed"
                ? "green"
                : "red";

        const securityColor =
            data.security_status === "Passed"
                ? "green"
                : "red";

        let downloadButton = "";

        if (data.pdf_file) {

            downloadButton = `
            <br><br>

            <a href="/download/${data.pdf_file}">
                <button
                style="
                    background:#198754;
                    color:white;
                    border:none;
                    padding:12px 25px;
                    cursor:pointer;
                    border-radius:5px;
                    font-size:16px;
                ">
                    📄 Download PDF Report
                </button>
            </a>
            `;
        }

        result.innerHTML = `

<table
style="
width:100%;
border-collapse:collapse;
font-family:Arial;
">

<tr
style="
background:#0d6efd;
color:white;
">

<th colspan="2"
style="padding:12px;">
🚀 PipelineGuard Validation Report
</th>

</tr>

<tr>

<th align="left">
File Name
</th>

<td>
${fileInput.files[0].name}
</td>

</tr>

<tr>

<th align="left">
File Type
</th>

<td>
${data.file_type || "-"}
</td>

</tr>

<tr>

<th align="left">
Validation Status
</th>

<td
style="
color:${validationColor};
font-weight:bold;
">
${data.status || "-"}
</td>

</tr>

<tr>

<th align="left">
Warnings
</th>

<td>
${data.warnings ?? 0}
</td>

</tr>

<tr>

<th align="left">
Errors
</th>

<td>
${data.errors ?? 0}
</td>

</tr>

<tr>

<th align="left">
Timestamp
</th>

<td>
${data.timestamp || "-"}
</td>

</tr>

<tr>

<th align="left">
Validation Result
</th>

<td>
${data.message || "-"}
</td>

</tr>

<tr
style="
background:#f2f2f2;
">

<th colspan="2">
🔒 Security Scan
</th>

</tr>

<tr>

<th align="left">
Security Status
</th>

<td
style="
color:${securityColor};
font-weight:bold;
">
${data.security_status || "-"}
</td>

</tr>

<tr>

<th align="left">
Severity
</th>

<td>
${data.security_severity || "-"}
</td>

</tr>

<tr>

<th align="left">
Security Result
</th>

<td>
${data.security_message || "-"}
</td>

</tr>

</table>

${downloadButton}

`;

    }

    catch (error) {

        result.innerHTML = `
            <div
            style="
                background:#ffe6e6;
                border:1px solid red;
                padding:15px;
                border-radius:5px;
            ">

                <h3 style="color:red;">
                    ❌ Error
                </h3>

                <p>${error}</p>

            </div>
        `;

    }

}