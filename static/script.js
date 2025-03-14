document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("collect_data").addEventListener("click", collectData);
    document.getElementById("align_button").addEventListener("click", alignSentences);
});

function collectData() {
    const englishUrl = document.getElementById("english_url").value;
    const hindiUrl = document.getElementById("hindi_url").value;

    fetch("/collect_data", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `english_url=${encodeURIComponent(englishUrl)}&hindi_url=${encodeURIComponent(hindiUrl)}`
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("english_sentences").value = data.english_sentences.filter(Boolean).join("\n");
        document.getElementById("hindi_sentences").value = data.hindi_sentences.filter(Boolean).join("\n");
    })
    .catch(error => console.error("Error:", error));
}

function alignSentences() {
    const englishSentences = document.getElementById("english_sentences").value.split("\n").map(s => s.trim()).filter(Boolean);
    const hindiSentences = document.getElementById("hindi_sentences").value.split("\n").map(s => s.trim());

    fetch("/align_sentences", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ english_sentences: englishSentences, hindi_sentences: hindiSentences })
    })
    .then(response => response.json())
    .then(data => {
        let tableBody = document.getElementById("alignedTable");
        tableBody.innerHTML = ""; // Clear previous content

        data.aligned_sentences.forEach((row, index) => {
            let tr = document.createElement("tr");
            tr.innerHTML = `<td>${index + 1}</td><td>${row[0]}</td><td>${row[1]}</td>`;
            tableBody.appendChild(tr);
        });
    })
    .catch(error => console.error("Error aligning sentences:", error));
}
