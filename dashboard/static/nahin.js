/* ============================================================
   Nahin AI — Dashboard client
   Live clock, safe command center, and optional greeting speech.
   ============================================================ */

(function () {
    "use strict";

    var form = document.getElementById("command-form");
    var input = document.getElementById("command-input");
    var outputPanel = document.getElementById("output-panel");
    var outputContent = document.getElementById("output-content");
    var outputEmpty = document.getElementById("output-empty");
    var runButton = document.getElementById("run-command");
    var csrfInput = form.querySelector('input[name="csrf_token"]');

    var timeoutId = null;
    var currentFetch = null;

    function toast(message, isError) {
        var el = document.createElement("div");
        el.className = "toast" + (isError ? " error" : "");
        el.textContent = message;
        document.body.appendChild(el);
        requestAnimationFrame(function () { el.classList.add("show"); });
        setTimeout(function () { el.classList.remove("show"); }, 2600);
        setTimeout(function () { el.remove(); }, 3000);
    }

    function showOutput(text, success) {
        outputContent.textContent = text;
        outputContent.classList.remove("hidden");
        outputEmpty.classList.add("hidden");
        outputContent.classList.remove("output-success", "output-error");
        outputContent.classList.add(success ? "output-success" : "output-error");
        outputPanel.scrollTop = outputPanel.scrollHeight;
    }

    function runCommand(command) {
        if (currentFetch) { currentFetch.abort(); }

        var trimmed = (command || "").trim();
        if (!trimmed) { return; }

        runButton.disabled = true;
        runButton.textContent = "Running...";

        currentFetch = fetch("/nahin/command", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                command: trimmed,
                csrf_token: csrfInput ? csrfInput.value : ""
            })
        });

        currentFetch
            .then(function (res) { return res.json().catch(function () { return {}; }); })
            .then(function (data) {
                var text = (data && data.output) ? data.output : "No output.";
                var success = data ? data.success !== false : false;
                showOutput(text, success);
                if (data && data.success === false) { toast("Command completed with an issue.", true); }
            })
            .catch(function (err) {
                if (err.name === "AbortError") { return; }
                showOutput("Could not reach the Nahin AI server. Is the dashboard running?", false);
                toast("Connection error.", true);
            })
            .finally(function () {
                currentFetch = null;
                runButton.disabled = false;
                runButton.textContent = "Run Command";
            });
    }

    if (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault();
            runCommand(input.value);
        });

        input.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
                e.preventDefault();
                runCommand(input.value);
            }
        });
    }

    var quickActions = document.getElementById("quick-actions");
    if (quickActions) {
        quickActions.addEventListener("click", function (e) {
            var btn = e.target.closest(".chip");
            if (!btn) { return; }
            var command = btn.getAttribute("data-command");
            if (input) { input.value = command; }
            runCommand(command);
        });
    }

    /* ---------- Live clock ---------- */
    function updateClock() {
        var now = new Date();
        var hours = now.getHours();
        var minutes = String(now.getMinutes()).padStart(2, "0");
        var seconds = String(now.getSeconds()).padStart(2, "0");
        var period = hours >= 12 ? "PM" : "AM";
        var display = String(((hours + 11) % 12) + 1) + ":" + minutes + ":" + seconds + " " + period;

        var timeEl = document.getElementById("clock-time");
        if (timeEl) { timeEl.textContent = display; }

        var dateEl = document.getElementById("clock-date");
        if (dateEl) {
            dateEl.textContent = now.toLocaleDateString(undefined, {
                weekday: "long", year: "numeric", month: "long", day: "numeric"
            });
        }
    }
    updateClock();
    setInterval(updateClock, 1000);

    /* ---------- Optional: Speak Greeting (TTS) ---------- */
    var speakButton = document.getElementById("speak-greeting");
    if (speakButton) {
        speakButton.addEventListener("click", function () {
            if (!("speechSynthesis" in window)) {
                toast("Speech synthesis is not supported in this browser.", true);
                return;
            }
            window.speechSynthesis.cancel();
            var greeting = document.getElementById("greeting-text");
            var greetingText = greeting ? greeting.textContent.trim() : "Good morning, Bappy";
            var message = new SpeechSynthesisUtterance(
                greetingText + ". Welcome back to Nahin AI. Your developer assistant is ready."
            );
            message.lang = "en-US";
            message.rate = 1;
            window.speechSynthesis.speak(message);
            toast("Speaking greeting...");
        });
    }
})();
