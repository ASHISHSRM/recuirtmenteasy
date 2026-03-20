// API Configuration
const RAILWAY_BACKEND_URL = ""; // Update with your Railway public URL
let API_BASE;

if (RAILWAY_BACKEND_URL && RAILWAY_BACKEND_URL.trim() !== "") {
    API_BASE = RAILWAY_BACKEND_URL.trim();
} else if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
    API_BASE = "http://localhost:5000";
} else {
    API_BASE = window.location.origin;
}

console.log("API Base:", API_BASE);

let screeningResults = [];

// Event Listeners
document.getElementById("screen_btn").addEventListener("click", screenResumes);
document.getElementById("export_csv_btn").addEventListener("click", exportCSV);
document.getElementById("export_excel_btn").addEventListener("click", exportExcel);

// File count display
document.getElementById("resume_files").addEventListener("change", function() {
    const fileCount = this.files.length;
    const fileCountDiv = document.getElementById("file-count");
    if (fileCount > 0) {
        fileCountDiv.innerHTML = `<i class="fas fa-check-circle text-success"></i> <strong>${fileCount}</strong> file(s) selected`;
    } else {
        fileCountDiv.innerHTML = "";
    }
});

async function screenResumes() {
    const jdFile = document.getElementById("jd_file").files[0];
    const jdText = document.getElementById("jd_text").value.trim();
    const resumeFiles = document.getElementById("resume_files").files;

    if (!jdFile && !jdText) {
        showAlert("Please provide a job description (file or text)", "warning");
        return;
    }

    if (resumeFiles.length === 0) {
        showAlert("Please select at least one resume", "warning");
        return;
    }

    const formData = new FormData();
    
    if (jdFile) {
        formData.append("jd_file", jdFile);
    } else {
        // Create a temporary file from text
        const blob = new Blob([jdText], { type: "text/plain" });
        formData.append("jd_file", blob, "jd.txt");
    }

    for (let file of resumeFiles) {
        formData.append("resume_files", file);
    }

    try {
        document.getElementById("loading").style.display = "block";
        document.getElementById("results_section").style.display = "block";
        document.getElementById("results_table").innerHTML = "";

        const response = await fetch(`${API_BASE}/screen`, {
            method: "POST",
            body: formData,
            headers: {
                "Accept": "application/json"
            }
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            screeningResults = data.results;
            displayResults(data);
            document.getElementById("export_csv_btn").disabled = false;
            document.getElementById("export_excel_btn").disabled = false;
        } else {
            alert(`❌ Error: ${data.error}`);
        }
    } catch (error) {
        console.error("Error:", error);
        showAlert(`Failed to screen resumes: ${error.message}`, "danger");
    } finally {
        document.getElementById("loading").style.display = "none";
    }
}

function showAlert(message, type = "info") {
    const alertIcon = {
        "info": "fa-info-circle",
        "warning": "fa-exclamation-triangle",
        "danger": "fa-times-circle",
        "success": "fa-check-circle"
    };
    
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="fas ${alertIcon[type]}"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const resultsSection = document.getElementById("results_section");
    if (resultsSection && resultsSection.style.display !== "none") {
        resultsSection.insertAdjacentHTML("afterbegin", alertHtml);
    }
}

function displayResults(data) {
    // Summary section
    const strongHires = data.results.filter(r => r.recommendation.includes("Strong Hire")).length;
    const midHires = data.results.filter(r => r.recommendation.includes("Mid Hire")).length;
    const noHires = data.results.filter(r => r.recommendation.includes("No Hire")).length;
    
    const summaryHtml = `
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="summary-card">
                    <div class="summary-icon success">
                        <i class="fas fa-check-circle"></i>
                    </div>
                    <div class="summary-content">
                        <h6>Strong Hire</h6>
                        <p>${strongHires}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="summary-card">
                    <div class="summary-icon warning">
                        <i class="fas fa-exclamation-circle"></i>
                    </div>
                    <div class="summary-content">
                        <h6>Mid Hire</h6>
                        <p>${midHires}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="summary-card">
                    <div class="summary-icon danger">
                        <i class="fas fa-times-circle"></i>
                    </div>
                    <div class="summary-content">
                        <h6>No Hire</h6>
                        <p>${noHires}</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById("results_summary").innerHTML = summaryHtml;
    
    // Results table
    const tableHtml = `
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr>
                        <th style="width: 5%;">Rank</th>
                        <th style="width: 12%;">Candidate</th>
                        <th style="width: 8%;">TF-IDF</th>
                        <th style="width: 10%;">Skill %</th>
                        <th style="width: 8%;">Score</th>
                        <th style="width: 12%;">Hire Status</th>
                        <th style="width: 8%;">Skills</th>
                        <th style="width: 18%;">Strengths</th>
                        <th style="width: 19%;">Key Gaps</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.results.map((result, idx) => `
                        <tr>
                            <td><strong>#${idx + 1}</strong></td>
                            <td><strong>${result.candidate_name}</strong></td>
                            <td><span class="badge bg-info">${result.tfidf_score}</span></td>
                            <td><span class="badge bg-primary">${result.skill_match}%</span></td>
                            <td><span class="badge bg-secondary" style="font-size: 0.95em; padding: 0.5rem 0.8rem;">${result.combined_score.toFixed(1)}</span></td>
                            <td>${getRecommendationBadge(result.recommendation)}</td>
                            <td><small><strong>${result.matched_skills}/${result.total_required_skills}</strong></small></td>
                            <td><small>${result.strengths.length > 0 ? result.strengths.join(", ") : "—"}</small></td>
                            <td><small style="color: #fca5a5;"><strong>${result.gaps.length > 0 ? result.gaps.slice(0, 4).join(", ") : "✓ Complete match"}</strong></small></td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        </div>
        ${data.errors && data.errors.length > 0 ? `
            <div class="alert alert-warning mt-4">
                <strong><i class="fas fa-exclamation-triangle"></i> Processing Errors:</strong>
                <ul class="mb-0 mt-2">
                    ${data.errors.map(err => `<li>${err}</li>`).join("")}
                </ul>
            </div>
        ` : ""}
    `;
    
    document.getElementById("results_table").innerHTML = tableHtml;
}

function getRecommendationBadge(recommendation) {
    if (recommendation.includes("Strong Hire")) {
        return `<span class="badge bg-success"><i class="fas fa-check-circle"></i> Strong Hire</span>`;
    } else if (recommendation.includes("Mid Hire")) {
        return `<span class="badge bg-warning"><i class="fas fa-exclamation-circle"></i> Mid Hire</span>`;
    } else if (recommendation.includes("No Hire")) {
        return `<span class="badge bg-danger"><i class="fas fa-times-circle"></i> No Hire</span>`;
    } else {
        return `<span class="badge bg-secondary">Unknown</span>`;
    }
}

function exportCSV() {
    if (screeningResults.length === 0) {
        alert("No results to export");
        return;
    }

    const headers = ["Rank", "Candidate", "TF-IDF Score", "Skill Match %", "Combined Score", "Recommendation", "Matched Skills", "Strengths", "Gaps"];
    const rows = screeningResults.map((result, idx) => [
        idx + 1,
        result.candidate_name,
        result.tfidf_score,
        result.skill_match,
        result.combined_score.toFixed(1),
        result.recommendation,
        `${result.matched_skills}/${result.total_required_skills}`,
        result.strengths.join("; "),
        result.gaps.join("; ")
    ]);

    const csv = [headers, ...rows].map(row => row.map(cell => `"${cell}"`).join(",")).join("\n");
    
    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `resume-screening-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
}

function exportExcel() {
    if (screeningResults.length === 0) {
        alert("No results to export");
        return;
    }

    const ws_name = "Screening Results";
    const wb = XLSX.utils.book_new();
    
    const data = screeningResults.map((result, idx) => ({
        "Rank": idx + 1,
        "Candidate": result.candidate_name,
        "TF-IDF Score": result.tfidf_score,
        "Skill Match %": result.skill_match,
        "Combined Score": result.combined_score.toFixed(1),
        "Recommendation": result.recommendation,
        "Matched Skills": `${result.matched_skills}/${result.total_required_skills}`,
        "Strengths": result.strengths.join("; "),
        "Gaps": result.gaps.join("; ")
    }));

    const ws = XLSX.utils.json_to_sheet(data);
    XLSX.utils.book_append_sheet(wb, ws, ws_name);
    XLSX.writeFile(wb, `resume-screening-${new Date().toISOString().split('T')[0]}.xlsx`);
}
