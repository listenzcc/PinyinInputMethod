console.log("Welcome to BCI input simulator");

let debug = true;

function get(id) {
    // Short version of getElementById
    let dom = document.getElementById(id);
    if (debug) {
        console.log("Got dom by id", id, dom);
    }
    return dom;
}

function clearAll(obj, name) {
    // Clear all the nodes named as [name] of [obj]
    obj.selectAll(name).data([]).exit().remove();
}

function onstartScript() {
    // Operations on startup
    console.log("Operating Onstart Script...");
    let inp = get("main-input");

    //----------------------------------------
    // Restore the char-panel
    // Clear it and fill it with a-z
    let panel = d3.select("#char-panel");
    clearAll(panel, "div");

    let atoz = [];
    for (let i = 97; i < 97 + 26; i++) {
        atoz.push(String.fromCharCode(i));
    }

    panel
        .append("div")
        .attr("class", "flex")
        .selectAll("p")
        .data(atoz)
        .enter()
        .append("p")
        .text((d) => d)
        .attr("class", "clickable")
        .on("click", function(e, d) {
            console.log(d);
            inp.value += d;
            newInput();
        });
}

function ravel(table) {
    // Parse json of pinYin table into list
    // Fetch the object in 'ciZus' option,
    // get the elements one by one,
    // and push them into a list
    let max = 100;

    let lst = [];
    for (let i in table) {
        for (let j = 0; j < table[i].length; j++) {
            lst.push(table[i][j]);
            max -= 1;
            if (max < 0) {
                return lst;
            }
        }
    }
    return lst;
}

function newInput() {
    // Operation on new input
    let inp = get("main-input");
    let out = get("main-output");
    let value = inp.value;
    let panel = d3.select("#dynamic-1-panel");

    d3.json("query/" + value).then(function(json) {
        clearAll(panel, "div");
        let lst = ravel(json.ciZus);

        panel
            .append("div")
            .attr("class", "flex")
            .selectAll("p")
            .data(lst)
            .enter()
            .append("p")
            .text((d) => d)
            .attr("class", "clickable")
            .on("click", function(e, d) {
                console.log(d);
                out.value += d;
                newSuggest(d);
            });
    });
}

function newSuggest(ciZu) {
    // Fetch suggestions based on ciZu
    let out = get("main-output");
    let panel = d3.select("#dynamic-2-panel");

    d3.json("guess/" + ciZu).then(function(json) {
        console.log(json);
        clearAll(panel, "div");
        let lst = ravel(json.suggests);

        panel
            .append("div")
            .attr("class", "flex")
            .selectAll("p")
            .data(lst)
            .enter()
            .append("p")
            .text((d) => d)
            .attr("class", "clickable")
            .on("click", function(e, d) {
                console.log(d);
                out.value += d;
            });
    });
}