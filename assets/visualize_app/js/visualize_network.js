// =============================
// PRINTING DEVICE DETAILS TABLE
// =============================

// ====================
// READING OF JSON FILE
// ====================
function readTextFile(file, callback) {
    var rawFile = new XMLHttpRequest();
    rawFile.overrideMimeType("application/json");
    rawFile.open("GET", file, true);
    rawFile.onreadystatechange = function () {
        if (rawFile.readyState === 4 && rawFile.status === "200") {
            callback(rawFile.responseText);
        }
    }
    rawFile.send(null);
}

// ####################################
// # using input parameters returns
// # HTML table with these inputs
// ####################################
function tableFromUnusedInterfaces(key, data) {
    text = "<table class=\"infobox2\">";
    text += "<thead><th><u><h4>LOCAL INT.</h4></u></th><th><u><h4>DESCRIPTION</h4></u></th><th><u><h4>Bandwith</h4></u></th>";
    text += "</thead>";

    for (var neighbor in data[key]) {
        text += "<tr>";

        console.log("local_intf:" + data[key][neighbor]['local_intf']);
        text += "<td>" + data[key][neighbor]['local_intf'] + "</td>";
        console.log("description:" + data[key][neighbor]['description']);
        text += "<td>" + data[key][neighbor]['description'] + "</td>";
        console.log("actual_bandwith:" + data[key][neighbor]['actual_bandwith']);
        text += "<td>" + data[key][neighbor]['actual_bandwith'] + "</td>";

        text += "</tr>";
    }

    text += "</table>";

    return text;
}

// ####################################
// # using input parameters returns
// # HTML table with these inputs
// ####################################
function tableFromNeighbor(key, data) {
    text = "<table class=\"infobox\">";
    text += "<thead><th><u><h4>LOCAL INT.</h4></u></th><th><u><h4>NEIGHBOR</h4></u></th><th><u><h4>NEIGHBOR'S INT</h4></u></th>";
    text += "</thead>";

    for (var neighbor in data[key]) {
        text += "<tr>";

        console.log("local_intf:" + data[key][neighbor]['local_intf']);
        text += "<td>" + data[key][neighbor]['local_intf'] + "</td>";
        console.log("neighbor_intf:" + data[key][neighbor]['neighbor_intf']);
        text += "<td>" + data[key][neighbor]['neighbor'] + "</td>";
        console.log("neighbor:" + data[key][neighbor]['neighbor']);
        text += "<td>" + data[key][neighbor]['neighbor_intf'] + "</td>";

        text += "</tr>";
    }

    text += "</table>";

    return text;
}

// ####################################
// # replaces content of specified DIV
// ####################################
function printToDivWithID(id, text) {
    div = document.getElementById(id);
    div.innerHTML = text;
}

// ########
// # MAIN #
// ########
width = window.innerWidth || document.documentElement.clientWidth;
height = window.innerHeight || document.documentElement.clientHeight;

var svg = d3.select("svg");

d3.select("svg").attr("height", height * 0.9)
d3.select("svg").attr("width", width * 0.785)

var color = d3.scaleOrdinal(d3.schemeCategory20);

var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function (d) {
        return d.id;
    }).distance(100).strength(0.001))
    .force("charge", d3.forceManyBody().strength(-200).distanceMax(500).distanceMin(50))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("center", d3.forceCenter((width * 0.8) / 2, height / 2))
    .force("collision", d3.forceCollide().radius(35));

// ######################################
// # Read graph.json and draw SVG graph #
// ######################################
d3.json(graph_data_path, function (error, graph) {
    if (error) throw error;


    var link = svg.append("g")
        .selectAll("line")
        .data(graph.links)
        .enter().append("line")
        .attr("stroke", "#547cf5")
        .attr("stroke-width", function (d) {
            return Math.sqrt(parseInt(d.value) / 2);
        });


    var node = svg.append("g")
        .attr("class", "nodes")
        .attr("id", "nodes")
        .selectAll("a")
        .data(graph.nodes).enter()
        .append("a")
        .attr("xlink:href", function (d){
            return "?device_id=" + d.object_id
        })


    node.on("click", function (d) {
        document.getElementById('device_post').value = d.object_id
        return document.getElementById('form-id').submit()
    })


    node.call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    node.append("image")
        .attr("xlink:href", function (d) {
            return (image_path + d.group + ".png");
        })
        .attr("width", 64)
        .attr("height", 64)
        .attr("x", -16)
        .attr("y", -25)
        .attr("fill", function (d) {
            return color(d.group);
        });

    node.append("text")
        .attr("font-size", "1.2em")
        .attr("fill", "#ba54f5")
        .attr("dx", 12)
        .attr("dy", ".35em")
        .attr("x", -125)
        .attr("y", -12)
        .text(function (d) {
            return d.id
        });


    node.append("title")
        .text(function (d) {
            return d.id;
        });

    simulation
        .nodes(graph.nodes)
        .on("tick", ticked);

    simulation.force("link")
        .links(graph.links);

    function ticked() {
        link
            .attr("x1", function (d) {
                return d.source.x;
            })
            .attr("y1", function (d) {
                return d.source.y;
            })
            .attr("x2", function (d) {
                return d.target.x;
            })
            .attr("y2", function (d) {
                return d.target.y;
            });

        node
            .attr("transform", function (d) {
                return "translate(" + d.x + "," + d.y + ")"
            });
    }
});

function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}

function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}
