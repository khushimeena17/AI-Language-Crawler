function alignSentences() {
    const englishSentences = document.getElementById("english_sentences").value.split("\n").map(s => s.trim()).filter(Boolean);
    const hindiSentences = document.getElementById("hindi_sentences").value.split("\n").map(s => s.trim()).filter(Boolean);

    fetch("/align", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ english_sentences: englishSentences, hindi_sentences: hindiSentences })
    })
    .then(response => response.json())
    .then(data => {
        let tableBody = document.getElementById("alignedTable");
        tableBody.innerHTML = ""; // Clear previous content

        data.aligned_data.forEach(row => {
            let tr = document.createElement("tr");
            tr.innerHTML = `<td>${row.serial}</td><td>${row.english}</td><td>${row.hindi}</td>`;
            tableBody.appendChild(tr);
        });
    })
    .catch(error => console.error("Error aligning sentences:", error));
}
