function addRowProfanity(tableID) {
    var table = document.getElementById(tableID);
    var rowCount = table.rows.length;
    var row = table.insertRow(rowCount);
    //Column 1
    var cell1 = row.insertCell(0);
    var element1 = document.createElement("input");
    element1.type = "button";
    var btnName = "button" + (rowCount + 1);
    element1.name = btnName;
    element1.setAttribute('value', 'Delete'); // or element1.value = "button";
    element1.onclick = function () { removeRow(btnName, tableID); }
    cell1.appendChild(element1);
    //Column 2
    var cell2 = row.insertCell(1);
    var element2 = document.createElement("input");
    element2.type = "checkbox";
    element2.id = "enabled-checkbox-" + rowCount + '-' + tableID;
    cell2.appendChild(element2);
    //Column 3
    var cell3 = row.insertCell(2);
    var element3 = document.createElement("input");
    element3.type = "text";
    cell3.appendChild(element3);
    var cell4 = row.insertCell(3);
    var element4 = document.createElement("input");
    element4.type = "checkbox";
    element4.id = "exact-checkbox-" + rowCount + tableID;
    cell4.appendChild(element4);
    var label = document.createElement("label");
    label.htmlFor = "exact-checkbox-" + rowCount + '-' + tableID;
    cell4.appendChild(label);
    var cell5 = row.insertCell(4);
    var element5 = document.createElement("input");
    element5.type = "text";
    cell5.appendChild(element5);
    var cell6 = row.insertCell(5);
    var element6 = document.createElement("input");
    element6.type = "text";
    cell6.appendChild(element6);
}

function addRowRepeat(tableID) {
    var table = document.getElementById(tableID);
    var rowCount = table.rows.length;
    var row = table.insertRow(rowCount);
    //Column 1
    var cell1 = row.insertCell(0);
    var element1 = document.createElement("input");
    element1.type = "button";
    var btnName = "button" + (rowCount + 1);
    element1.name = btnName;
    element1.setAttribute('value', 'Delete'); // or element1.value = "button";
    element1.onclick = function () { removeRow(btnName, tableID); }
    cell1.appendChild(element1);
    //Column 2
    var cell2 = row.insertCell(1);
    var element2 = document.createElement("input");
    element2.type = "checkbox";
    element2.id = "enabled-checkbox-" + rowCount + '-' + tableID;
    cell2.appendChild(element2);
    //Column 3
    var cell3 = row.insertCell(2);
    var element3 = document.createElement("input");
    element3.type = "text";
    cell3.appendChild(element3);
    var cell4 = row.insertCell(3);
    var element4 = document.createElement("input");
    element4.type = "text";
    cell4.appendChild(element4);
    var cell5 = row.insertCell(4);
    var element5 = document.createElement("input");
    element5.type = "text";
    cell5.appendChild(element5);
    var cell6 = row.insertCell(5);
    var element6 = document.createElement("input");
    element6.type = "text";
    cell6.appendChild(element6);
}

function addRowSpam(tableID) {
    var table = document.getElementById(tableID);
    var rowCount = table.rows.length;
    var row = table.insertRow(rowCount);
    //Column 1
    var cell1 = row.insertCell(0);
    var element1 = document.createElement("input");
    element1.type = "button";
    var btnName = "button" + (rowCount + 1);
    element1.name = btnName;
    element1.setAttribute('value', 'Delete'); // or element1.value = "button";
    element1.onclick = function () { removeRow(btnName, tableID); }
    cell1.appendChild(element1);
    //Column 2
    var cell2 = row.insertCell(1);
    var element2 = document.createElement("input");
    element2.type = "checkbox";
    element2.id = "enabled-checkbox-" + rowCount + '-' + tableID;
    cell2.appendChild(element2);
    //Column 3
    var cell3 = row.insertCell(2);
    var element3 = document.createElement("input");
    element3.type = "text";
    cell3.appendChild(element3);
    var cell4 = row.insertCell(3);
    var element4 = document.createElement("input");
    element4.type = "text";
    cell4.appendChild(element4);
    var cell5 = row.insertCell(4);
    var element5 = document.createElement("input");
    element5.type = "text";
    cell5.appendChild(element5);
}

function addRowMentions(tableID) {
    var table = document.getElementById(tableID);
    var rowCount = table.rows.length;
    var row = table.insertRow(rowCount);
    //Column 1
    var cell1 = row.insertCell(0);
    var element1 = document.createElement("input");
    element1.type = "button";
    var btnName = "button" + (rowCount + 1);
    element1.name = btnName;
    element1.setAttribute('value', 'Delete'); // or element1.value = "button";
    element1.onclick = function () { removeRow(btnName, tableID); }
    cell1.appendChild(element1);
    //Column 2
    var cell2 = row.insertCell(1);
    var element2 = document.createElement("input");
    element2.type = "checkbox";
    element2.id = "enabled-checkbox-" + rowCount + '-' + tableID;
    cell2.appendChild(element2);
    //Column 3
    var cell3 = row.insertCell(2);
    var element3 = document.createElement("textarea");
    element3.cols = "25";
    element3.rows = "3";
    cell3.appendChild(element3);
    var cell4 = row.insertCell(3);
    var element4 = document.createElement("input");
    element4.type = "text";
    cell4.appendChild(element4);
    var cell5 = row.insertCell(4);
    var element5 = document.createElement("input");
    element5.type = "text";
    cell5.appendChild(element5);
    var cell6 = row.insertCell(5);
    var element6 = document.createElement("input");
    element6.type = "text";
    cell6.appendChild(element6);
}

function addRowConfig(tableID) {
    var table = document.getElementById(tableID);
    var rowCount = table.rows.length;
    var row = table.insertRow(rowCount);
    //Column 1
    var cell1 = row.insertCell(0);
    var element1 = document.createElement("input");
    element1.type = "button";
    var btnName = "button" + (rowCount + 1);
    element1.name = btnName;
    element1.setAttribute('value', 'Delete'); // or element1.value = "button";
    element1.onclick = function () { removeRow(btnName, tableID); }
    cell1.appendChild(element1);
    //Column 2
    var cell2 = row.insertCell(1);
    var element2 = document.createElement("input");
    element2.type = "checkbox";
    element2.id = "enabled-checkbox-" + rowCount + '-' + tableID;
    cell2.appendChild(element2);
    //Column 3
    var cell3 = row.insertCell(2);
    var element3 = document.createElement("input");
    element3.type = "text";
    cell3.appendChild(element3);
    var cell4 = row.insertCell(3);
    var element4 = document.createElement("input");
    element4.type = "text";
    cell4.appendChild(element4);
    var cell5 = row.insertCell(4);
    var element5 = document.createElement("input");
    element5.type = "text";
    cell5.appendChild(element5);
}

function addRowHelper(tableID) {
    var table = document.getElementById(tableID);
    var rowCount = table.rows.length;
    var row = table.insertRow(rowCount);
    //Column 1
    var cell1 = row.insertCell(0);
    var element1 = document.createElement("input");
    element1.type = "button";
    var btnName = "button" + (rowCount + 1);
    element1.name = btnName;
    element1.setAttribute('value', 'Delete'); // or element1.value = "button";
    element1.onclick = function () { removeRow(btnName, tableID); }
    cell1.appendChild(element1);
    //Column 2
    var cell2 = row.insertCell(1);
    var element2 = document.createElement("input");
    element2.type = "checkbox";
    element2.id = "enabled-checkbox-" + rowCount + '-' + tableID;
    cell2.appendChild(element2);
    //Column 3
    var element3 = document.createElement("textarea");
    element3.cols = "25";
    element3.rows = "3";
    cell3.appendChild(element3);
    var cell4 = row.insertCell(3);
    var element4 = document.createElement("input");
    element4.type = "checkbox";
    element4.id = "exact-checkbox-" + rowCount + tableID;
    cell4.appendChild(element4);
    var label = document.createElement("label");
    label.htmlFor = "exact-checkbox-" + rowCount + '-' + tableID;
    cell4.appendChild(label);
    var cell5 = row.insertCell(4);
    var element5 = document.createElement("input");
    element5.type = "text";
    cell5.appendChild(element5);
    var cell6 = row.insertCell(5);
    var element6 = document.createElement("textarea");
    element3.cols = "25";
    element3.rows = "3";
    cell6.appendChild(element6);
}

function removeRow(btnName, tableID) {
    try {
        var table = document.getElementById(tableID);
        var rowCount = table.rows.length;
        var deleted = false;
        for (var i = 0; i < rowCount; i++) {
            var row = table.rows[i];
            var rowObj = row.cells[0].childNodes[0];
            try {
                if (rowObj.name == btnName) {
                    table.deleteRow(i);
                    rowCount--;
                    deleted = true;
                    continue;
                }
            } catch (e) {}
            if (deleted)
                row.cells[1].innerHTML = i-1;
        }
    }
    catch (e) {
        alert(e);
    }
}

function addConfigTable() {
    let area = document.getElementById("timeout_config_div");
    let numberOfChildren = area.getElementsByTagName('table').length
    let HTML =
        `<document>\n` +
        `<div id="timeout_config_div_${numberOfChildren}"><p>\n` +
        `    <label for="config_name_${numberOfChildren}">Configuration Name:</label>` +
        `    <INPUT type="text" id="name_timeout_config_table_${numberOfChildren}" name="config_name_${numberOfChildren}"/>\n` +
        `    <TABLE id="timeout_config_table_${numberOfChildren}" width="350px" border="1">\n` +
        '        <TR>\n' +
        '            <TH></TH>\n' +
        '            <TH>Enabled?</TH>\n' +
        '            <TH>Offense count for tier</TH>\n' +
        '            <TH>Time period for offense count (i.e 1d, 1w. Month+ does not work)</TH>\n' +
        '            <TH>Timeout duration (i.e 30m, 1h, etc)</TH>\n' +
        '        </TR>\n' +
        '        <TR>\n' +
        '            <TD><input type="button" name="button1" value="Delete" onclick="removeRow(\'button1\')"/></TD>\n' +
        `            <TD><input name="enabled-checkbox[]" id="enabled-checkbox-0-timeout_config_${numberOfChildren}" value="exact" type="checkbox" checked="checked"/></TD>\n` +
        `            <TD><input type="text" value="" name="offenses"/></TD>\n` +
        `            <TD><input type="text" value="" name="period"/></TD>\n` +
        `            <TD><input type="text" value="" name="duration"/></TD>\n` +
        '        </TR>\n' +
        '    </TABLE>\n' +
        `    <INPUT type="button" value="Add Row" onclick="addRowConfig(\'timeout_config_table_${numberOfChildren}\')"/>\n` +
        `    <INPUT type="button" value="Delete Configuration" onclick="deleteConfigTable(\'timeout_config_div_${numberOfChildren}\')"/>` +
        '</p><br></div>\n' +
        `</document>`
    let doc = new DOMParser().parseFromString(HTML, "text/html");
    area.appendChild(doc.getElementById(`timeout_config_div_${numberOfChildren}`));
}

function deleteConfigTable(divID){
    let elem = document.getElementById(divID);
    return elem.parentNode.removeChild(elem);
}