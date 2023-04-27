document.getElementById("question-form").addEventListener("submit", function (event) {
    event.preventDefault();
    let question = document.getElementById("question").value;
    $.ajax({
        url: "/ask",
        method: "POST",
        data: { "question": question },
        success: function (response) {
            let answerDiv = document.createElement("div");
            answerDiv.innerHTML = response.template;
            let questionsContainer = document.getElementById("questions-container");
            questionsContainer.insertBefore(answerDiv, questionsContainer.firstChild);
            document.getElementById("question").value = "";
        }
    });
});

document.getElementById("clear-questions").addEventListener("click", function () {
    let questionsContainer = document.getElementById("questions-container");
    while (questionsContainer.firstChild) {
        questionsContainer.removeChild(questionsContainer.firstChild);
    }

    // Add the following lines to call the /clear endpoint
    fetch("/clear", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        }
    }).then(response => {
        if (response.ok) {
            console.log("Questions list cleared on the server side");
        } else {
            console.error("Failed to clear the questions list on the server side");
        }
    }).catch(error => {
        console.error("Error:", error);
    });
});