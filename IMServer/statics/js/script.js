function weChat() {
    // Display weChat app
    d3.json("weChat/" + "display").then(function(json) {
        console.log(json);
    });
}

function sendMessage() {
    // Send message to weChat
    // message is read from Input-2
    let str = document.getElementById("Input-2").value;
    console.log(str);
    d3.json("send/" + str).then(function(json) {
        console.log(json);
    });
}

function onclickArea6() {
    // Hide Area-5 and Area-6
    document.getElementById("Area-5").style.display = "none";
    document.getElementById("Area-6").style.display = "none";
}

function inputByClick(c) {
    // Onclick callback func of controlling commands

    // Clear Input-1
    if (c == "C") {
        document.getElementById("Input-1").value = "";
    }

    // Clear Input-1 and Input-2
    if (c == "K") {
        document.getElementById("Input-1").value = "";
        document.getElementById("Input-2").value = "";
    }

    // Backspace on Input-1
    if (c == "B") {
        let value = document.getElementById("Input-2").value;
        let len = value.length;
        document.getElementById("Input-2").value = value.substring(0, len - 1);
    }

    // Append symbol to tail
    if (c == "，" || c == "。") {
        document.getElementById("Input-2").value += c;
    }

    // Set focus to Input-1 and perform select-all operation
    document.getElementById("Input-1").focus();
    document.getElementById("Input-1").select();
}

function clear(dom) {
    // Remove all children from the [dom]
    while (dom.childElementCount > 0) {
        dom.children[0].remove();
    }
}

function json2lst(json) {
    // Convert json into lst
    let max = 100;
    let lst = [];
    for (let i in json.candidates) {
        lst[lst.length] = [json.candidates[i], json.pinYin[i]];
        if (i > max) {
            break;
        }
    }
    return lst;
}

function query() {
    let inp2 = document.getElementById("Input-2");
    let value = document.getElementById("Input-1").value;
    console.log(value);

    while (value.startsWith(" ")) {
        value = value.substring(1);
    }

    while (value.endsWith(" ")) {
        value = value.substring(0, value.length - 1);
    }

    if (value.length == 0) {
        console.log("Empty value received, doing nothing.");
        return 1;
    }

    d3.json("query/" + value).then(function(json) {
        console.log(json);
        let lst = json2lst(json);
        if (lst.length == 0) {
            return;
        }
        clear(document.getElementById("Area-3"));

        d3.select("#Area-7").selectAll("div").data([0]).exit().remove();
        let div7 = d3.select("#Area-7").append("div").attr("class", "flex-display");

        d3.select("#Area-3")
            .selectAll("div")
            .data(lst)
            .enter()
            .append("div")
            .attr("class", "row-candidates flex-display")
            .selectAll("p")
            .data((d) => d[0])
            .enter()
            .append("p")
            .attr("class", "col-candidate")
            .html(function(d) {
                addWordToDiv(d, div7);
                return d;
            })
            .on("click", function(e, d) {
                // Onclick response of candidate ciZu in Chinese
                // Record the clicked ciZu into inp2.value
                inp2.value += d;
                inputByClick("");

                // Update the Area-4 for the contents containing the ciZu
                updateArea4(d);
            });
    });
}

function addWordToDiv(word, div) {
    let inp2 = document.getElementById("Input-2");
    let max = 50;
    if (div._groups[0][0].childElementCount > max) {
        return 1;
    }
    div
        .append("p")
        .attr("class", "col-candidate")
        .html(word)
        .on("click", function(e, d) {
            inp2.value += word;
            inputByClick("");
            updateArea4(word);
        });
}

function delHtmlTag(str) {
    // Remove all HTML tags in the str
    return str.replace(/<[^>]+>/g, "");
}

function updateArea4(str) {
    // Update Area-4
    // Query backend for contents containing [str]
    // update Area-4, suggestion area, with the found contents
    d3.json("guess/" + str).then(function(json) {
        // Clear Area-4
        clear(document.getElementById("Area-4"));

        // Prepare fetched json into list
        let max = 100;
        let lst = [];
        for (let i in json.sentence) {
            lst[lst.length] = json.sentence[i];
            if (i > max) {
                break;
            }
        }

        // Update Area-4
        d3.select("#Area-4")
            .selectAll("p")
            .data(lst)
            .enter()
            .append("p")
            .attr("class", "row-sentence")
            .html((d) => d)
            .on("click", function(e, d) {
                console.log(d);
                bigBoom(delHtmlTag(d));
            });
    });
}

function bigBoom(str) {
    let inp2 = document.getElementById("Input-2");
    // Perform big boom based on string
    // Area-5 will be updated based on the splitting of the [str]

    d3.json("split/" + str).then(function(json) {
        // Clear Area-5
        clear(document.getElementById("Area-5"));

        // Prepare fetched json into list
        console.log(json);
        let max = 100;
        let lst = [];
        for (let i in json) {
            lst[lst.length] = json[i];
            if (i > max) {
                break;
            }
        }

        d3.select("#Area-7").selectAll("div").data([0, 1]).exit().remove();
        let div7 = d3.select("#Area-7").append("div").attr("class", "flex-display");
        // Update Area-5
        d3.select("#Area-5")
            .append("div")
            .attr("class", "flex-display")
            .selectAll("p")
            .data(lst)
            .enter()
            .append("p")
            .attr("class", "col-candidate")
            .html(function(d) {
                addWordToDiv(d, div7);
                return d;
            })
            .on("click", function(e, d) {
                // Onclick response of candidate ciZu in Chinese
                // Record the clicked ciZu into inp2.value
                inp2.value += d;
                inputByClick("");
            });
    });

    // Display the Area-5 and Area-6
    document.getElementById("Area-5").style.display = "block";
    document.getElementById("Area-6").style.display = "block";
}