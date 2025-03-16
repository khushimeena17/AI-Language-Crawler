async function alignData() {
    let english_sentences = Array.from(document.getElementById('english_list').children).map(li => li.innerText);
    let hindi_sentences = Array.from(document.getElementById('hindi_list').children).map(li => li.innerText);

    if (english_sentences.length === 0 || hindi_sentences.length === 0) {
        alert("Please clean & collect data first!");
        return;
    }

    try {
        let response = await fetch('/align', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ english_sentences, hindi_sentences })
        });

        if (!response.ok) throw new Error(`Server error: ${response.status}`);

        let data = await response.json();

        // 🔹 Show aligned sentences in the list
        document.getElementById('aligned_list').innerHTML = data.aligned_data.map(
            pair => `<li><b>${pair.id}.</b> ${pair.english} - <i>${pair.hindi}</i></li>`
        ).join('');

        // 🔹 Create a downloadable CSV file
        createCSVDownload(data.aligned_data);
    } catch (error) {
        console.error("Error aligning sentences:", error);
        alert("Failed to align sentences. Check console for details.");
    }
}

function createCSVDownload(aligned_data) {
    let csvContent = "ID,English,Hindi\n";
    csvContent += aligned_data.map(row => `${row.id},"${row.english}","${row.hindi}"`).join("\n");

    let blob = new Blob([csvContent], { type: "text/csv" });
    let url = URL.createObjectURL(blob);

    let downloadLink = document.createElement("a");
    downloadLink.href = url;
    downloadLink.download = "aligned_sentences.csv";
    downloadLink.innerText = "📥 Download CSV";

    let csvContainer = document.getElementById("csvDownload");
    csvContainer.innerHTML = "";  // Clear previous download link
    csvContainer.appendChild(downloadLink);
}
