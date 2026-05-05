function appendMessage(text, sender) {
    const chatBox = document.getElementById("chat-box");
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message");
    msgDiv.classList.add(sender === "user" ? "user-message" : "bot-message");
    msgDiv.innerText = text;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return msgDiv;
}

function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

async function sendMessage() {
    const inputField = document.getElementById("user-input");
    const msg = inputField.value.trim();
    
    if (msg === "") return;
    
    appendMessage(msg, "user");
    inputField.value = "";
    
    const chatBox = document.getElementById("chat-box");
    const loadingDiv = document.createElement("div");
    loadingDiv.classList.add("message", "bot-message", "loading-indicator");
    loadingDiv.id = "loading-spinner";
    loadingDiv.innerHTML = `<div class="spinner"></div> Đang xử lý...`;
    chatBox.appendChild(loadingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    const startTime = performance.now();

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: msg,
                session_id: "demo_session1" // Hardcode session id giả định
            })
        });
        
        if (!response.ok) {
            throw new Error("Lỗi kết nối từ server");
        }
        
        const data = await response.json();
        const endTime = performance.now();
        const execTime = ((endTime - startTime) / 1000).toFixed(2);
        
        const loadingElement = document.getElementById("loading-spinner");
        if (loadingElement) loadingElement.remove();
        
        if (data.reply) {
            // Kiểm tra xem data.reply có phải là object có answer_text không
            const replyObj = data.reply;
            if (typeof replyObj === 'object' && replyObj !== null && replyObj.answer_text) {
                let botMsg = appendMessage(replyObj.answer_text, "bot");
                let timeDiv = document.createElement("div");
                timeDiv.className = "exec-time";
                timeDiv.innerText = `Thời gian phản hồi: ${execTime}s`;
                botMsg.appendChild(timeDiv);
                
                // Hiển thị context JSON structure nếu replyObj type là TABLE hoặc MIXED
                if (replyObj.answer_type === "TABLE" || replyObj.answer_type === "MIXED") {
                    const tableContainer = document.createElement("div");
                    tableContainer.classList.add("bot-message-table");
                    
                    if (replyObj.table_html) {
                        tableContainer.innerHTML = replyObj.table_html;
                    } else if (replyObj.table_json) {
                        tableContainer.appendChild(renderTableFromJson(replyObj.table_json, replyObj.highlight_cells || []));
                    } else {
                        // Fallback
                        tableContainer.style.background = "#f0f0f0";
                        tableContainer.style.padding = "10px";
                        tableContainer.style.marginTop = "5px";
                        tableContainer.style.borderRadius = "8px";
                        tableContainer.style.fontSize = "0.9em";
                        
                        let tableMeta = "<strong>Data Structure:</strong><br/>";
                        if (replyObj.table_id) {
                            tableMeta += `Table ID: ${replyObj.table_id}<br/>`;
                        }
                        if (replyObj.highlight_cells && replyObj.highlight_cells.length > 0) {
                            tableMeta += `Highlighted Cells: ${replyObj.highlight_cells.join(", ")}<br/>`;
                        }
                        if (replyObj.source_spans && replyObj.source_spans.length > 0) {
                            tableMeta += `Source Spans: ${replyObj.source_spans.join(", ")}<br/>`;
                        }
                        tableContainer.innerHTML = tableMeta;
                    }

                    const chatBox = document.getElementById("chat-box");
                    chatBox.appendChild(tableContainer);
                    chatBox.scrollTop = chatBox.scrollHeight;
                }
            } else {
                let botMsg = appendMessage(data.reply, "bot");
                let timeDiv = document.createElement("div");
                timeDiv.className = "exec-time";
                timeDiv.innerText = `Thời gian phản hồi: ${execTime}s`;
                botMsg.appendChild(timeDiv);
            }
        } else if (data.error) {
            appendMessage("Lỗi xử lý: " + data.error, "bot");
        }
    } catch (err) {
        const loadingElement = document.getElementById("loading-spinner");
        if (loadingElement) loadingElement.remove();

        appendMessage("Không thể kết nối đến máy chủ. Xin vui lòng thử lại.", "bot");
        console.error(err);
    }
}

function renderTableFromJson(tableJson, highlightCells) {
    const table = document.createElement("table");
    table.classList.add("huit-table");
    
    if (tableJson.headers && tableJson.headers.length > 0) {
        const thead = document.createElement("thead");
        const tr = document.createElement("tr");
        tableJson.headers.forEach(headerText => {
            const th = document.createElement("th");
            th.innerText = headerText;
            tr.appendChild(th);
        });
        thead.appendChild(tr);
        table.appendChild(thead);
    }
    
    if (tableJson.rows && tableJson.rows.length > 0) {
        const tbody = document.createElement("tbody");
        tableJson.rows.forEach((row, rowIndex) => {
            const tr = document.createElement("tr");
            row.forEach((cellText, colIndex) => {
                const td = document.createElement("td");
                td.innerText = cellText;
                
                // Construct cell ID format to match highlights
                // This depends on how the backend generates IDs, e.g., table_1_cell_0_0
                // For simplicity, we just check if the text matches or if we can pass the exact IDs.
                // Since our parsed_tables has id="table_x_cell_y_z", we can't easily guess the table ID here unless passed.
                // But if highlightCells is an array of IDs, it works best with HTML.
                // For JSON, we will just apply to all if we can't match, or assume highlightCells might contain exact text or coordinates.
                // Assuming highlightCells might contain "row_X_col_Y" or similar for json.
                if (highlightCells.includes(`r${rowIndex}c${colIndex}`)) {
                    td.classList.add("highlight-cell");
                }
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);
    }
    
    return table;
}
