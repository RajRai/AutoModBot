function getElementsStartsWithId( id ) {
    let children = document.body.getElementsByTagName('*');
    let elements = [], child;
    for (var i = 0, length = children.length; i < length; i++) {
        child = children[i];
        if (child.id.substr(0, id.length) == id)
            elements.push(child);
    }
    return elements;
}

function dump_settings(){
    let i;
    let jsonArr = [];
    let automod = {
        blacklist: {},
        mentions: {},
        repeat: {},
        spam: {}
    };

    let checkbox = document.getElementById('profanity_enabled');
    automod.blacklist.enabled = checkbox.checked;
    checkbox = document.getElementById('spam_enabled');
    automod.spam.enabled = checkbox.checked;
    checkbox = document.getElementById('repeat_enabled');
    automod.repeat.enabled = checkbox.checked;
    checkbox = document.getElementById('mention_enabled');
    automod.mentions.enabled = checkbox.checked;

    let table = document.getElementById('profanity_settings');
    for(i = 1; i < table.rows.length; i++){
        let row = table.rows[i];
        let col = row.cells;
        let jsonObj = {
            enabled : col[1].firstChild.checked,
            content : col[2].firstChild.value,
            exact : col[3].firstChild.checked,
            threshold : parseFloat(col[4].firstChild.value),
            timeout : col[5].firstChild.value
        }
        jsonArr.push(jsonObj);
    }
    automod.blacklist.rules = jsonArr;
    automod.blacklist.enabled = true;
    jsonArr = [];

    table = document.getElementById('spam_settings');
    for(i=1; i < table.rows.length; i++){
        let row = table.rows[i];
        let col = row.cells;
        let jsonObj = {
            enabled : col[1].firstChild.checked,
            cutoff : col[2].firstChild.value,
            limit : parseInt(col[3].firstChild.value),
            timeout : col[4].firstChild.value
        }
        jsonArr.push(jsonObj);
    }
    automod.spam.enabled = true;
    automod.spam.rules = jsonArr;
    jsonArr = [];

    table = document.getElementById('repeat_settings');
    for(i=1; i < table.rows.length; i++){
        let row = table.rows[i];
        let col = row.cells;
        let jsonObj = {
            enabled : col[1].firstChild.checked,
            cutoff : col[2].firstChild.value,
            limit : parseInt(col[3].firstChild.value),
            threshold: parseFloat(col[4].firstChild.value),
            timeout : col[5].firstChild.value
        }
        jsonArr.push(jsonObj);
    }
    automod.repeat.enabled = true;
    automod.repeat.rules = jsonArr;
    jsonArr = [];

    table = document.getElementById('mention_settings');
    for(i=1; i < table.rows.length; i++){
        let row = table.rows[i];
        let col = row.cells;
        let jsonObj = {
            enabled : col[1].firstChild.checked,
            content : col[2].firstChild.value.split("\n"),
            limit : parseInt(col[3].firstChild.value),
            cutoff: col[4].firstChild.value,
            timeout : col[5].firstChild.value
        }
        jsonArr.push(jsonObj);
    }
    automod.mentions.rules = jsonArr;
    automod.mentions.enabled = true;
    jsonArr = [];

    let tables = document.getElementById('timeout_config_div').getElementsByTagName('TABLE');
    for (i=0; i < tables.length; i++){
        table = tables[i];
        let name = document.getElementById('name_' + table.id);
        let jsonArr2 = [];
        for(let j = 1; j < table.rows.length; j++){
            let row = table.rows[j];
            let col = row.cells;
            let jsonObj = {
                enabled : col[1].firstChild.checked,
                offenseCount : col[2].firstChild.value,
                cutoff : col[3].firstChild.value,
                timeout : col[4].firstChild.value
            }
            jsonArr2.push(jsonObj);
        }
        let jsonObj2 = {
            name : name.value,
            steps : jsonArr2
        }
        jsonArr.push(jsonObj2);
    }
    automod.timeout = jsonArr;
    jsonArr = [];

    let helper = {}
    checkbox = document.getElementById('helper_enabled');
    helper.enabled = checkbox.checked;
    table = document.getElementById('helper_settings');
    for(i = 1; i < table.rows.length; i++){
        let row = table.rows[i];
        let col = row.cells;
        let jsonObj = {
            enabled : col[1].firstChild.checked,
            search : col[2].firstChild.value,
            exact : col[3].firstChild.checked,
            threshold : parseFloat(col[4].firstChild.value),
            reply : col[5].firstChild.value
        }
        jsonArr.push(jsonObj);
    }
    helper.rules = jsonArr
    jsonArr = [];

    let logging = {}
    logging.logging_channel = document.getElementById('logging_channel_input').value;
    checkbox = document.getElementById('log_bans');
    logging.bans = checkbox.checked;
    checkbox = document.getElementById('log_timeouts');
    logging.timeouts = checkbox.checked;
    checkbox = document.getElementById('log_deletes');
    logging.deletes = checkbox.checked;
    checkbox = document.getElementById('log_help_replies');
    logging.help_replies = checkbox.checked;
    checkbox = document.getElementById('log_settings_changes');
    logging.settings_changes = checkbox.checked;

    automod.saved_messages = parseInt(document.getElementById('message_count_input').value);
    automod.enabled = document.getElementById('automod_enabled').checked;

    var settings = {
        automod: automod,
        helper: helper,
        logging: logging
    };

    settings.manager_role = document.getElementById('manager_role_input').value.split("\n");
    settings.prefix = document.getElementById('prefix_input').value;
    settings.enabled = document.getElementById('bot_enabled').checked;

    let result = document.getElementById('result_label');

    // Creating a XHR object
    let xhr = new XMLHttpRequest();
    let url = window.location.protocol + "//" + window.location.host + window.location.pathname;

    // open a connection
    xhr.open("POST", url, true);

    // Set the request header i.e. which type of content you are sending
    xhr.setRequestHeader("Content-Type", "application/json");

    // Create a state change callback
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {

            // Print received data from server
            result.innerHTML = this.responseText;

        }
    };

    // Converting JSON data to string
    const data = JSON.stringify(settings);

    // Sending data with the request
    xhr.send(data);

    // Refresh
    location.reload();
}

function load_settings(json){
    try {
        var table = document.getElementById('profanity_settings')
        let checkbox = document.getElementById('profanity_enabled');
        checkbox.checked = json.automod.blacklist.enabled;

        for (var i = 0; i < json.automod.blacklist.rules.length; i++) {
            if (i > 0) addRowProfanity('profanity_settings');
            var rule = json.automod.blacklist.rules[i];
            var row = table.rows[i + 1];
            var col = row.cells;
            col[1].firstChild.checked = rule.enabled;
            col[2].firstChild.value = rule.content;
            col[3].firstChild.checked = rule.exact;
            col[4].firstChild.value = rule.threshold;
            col[5].firstChild.value = rule.timeout
        }
    } catch (e) {}

    try {
        table = document.getElementById('spam_settings');
        let checkbox = document.getElementById('spam_enabled');
        checkbox.checked = json.automod.spam.enabled;
        for (i = 0; i < json.automod.spam.rules.length; i++) {
            if (i > 0) addRowSpam('spam_settings');
            rule = json.automod.spam.rules[i];
            row = table.rows[i + 1];
            col = row.cells;
            col[1].firstChild.checked = rule.enabled;
            col[2].firstChild.value = rule.cutoff;
            col[3].firstChild.value = rule.limit;
            col[4].firstChild.value = rule.timeout;
        }
    } catch (e) {}

    try {
        table = document.getElementById('repeat_settings');
        let checkbox = document.getElementById('repeat_enabled');
        checkbox.checked = json.automod.repeat.enabled;
        for (i = 0; i < json.automod.repeat.rules.length; i++) {
            if (i > 0) addRowRepeat('repeat_settings');
            rule = json.automod.repeat.rules[i];
            row = table.rows[i + 1];
            col = row.cells;
            col[1].firstChild.checked = rule.enabled;
            col[2].firstChild.value = rule.cutoff;
            col[3].firstChild.value = rule.limit;
            col[4].firstChild.value = rule.threshold;
            col[5].firstChild.value = rule.timeout;
        }
    } catch (e) {}

    try {
        table = document.getElementById('mention_settings');
        let checkbox = document.getElementById('mention_enabled');
        checkbox.checked = json.automod.mentions.enabled;
        for (i = 0; i < json.automod.mentions.rules.length; i++) {
            if (i > 0) addRowMentions('repeat_settings');
            rule = json.automod.mentions.rules[i];
            row = table.rows[i + 1];
            col = row.cells;
            col[1].firstChild.checked = rule.checked;
            col[2].firstChild.value = rule.content.join("\n");
            col[3].firstChild.value = rule.limit;
            col[4].firstChild.value = rule.cutoff;
            col[5].firstChild.value = rule.timeout;
        }
    } catch (e) {}

    try {
        for (i = 0; i < json.automod.timeout.length; i++) {
            let config = json.automod.timeout[i];
            addConfigTable();
            let tables = getElementsStartsWithId('timeout_config_table_');
            table = tables[i];
            for (let j = 0; j < config.steps.length; j++) {
                if (j > 0) addRowConfig(`timeout_config_table_${i}`)
                let tables = getElementsStartsWithId('timeout_config_table_');
                table = tables[i];
                let rule = config.steps[j];
                row = table.rows[j + 1];
                col = row.cells;
                col[1].firstChild.checked = rule.enabled;
                col[2].firstChild.value = rule.offenseCount;
                col[3].firstChild.value = rule.cutoff;
                col[4].firstChild.value = rule.timeout;
            }
        }
        for (i = 0; i < json.automod.timeout.length; i++) { // If this isn't done last, only the last name displays
            let config = json.automod.timeout[i];
            let name = document.getElementById('name_timeout_config_table_' + i);
            name.value = config.name;
        }
    } catch (e) {}

    try {
        document.getElementById('message_count_input').value = json.automod.saved_messages;
        document.getElementById('automod_enabled').checked = json.automod.enabled;
        document.getElementById('manager_role_input').value = json.manager_role.join("\n");
        document.getElementById('logging_channel_input').value = json.logging.logging_channel;
        document.getElementById('prefix_input').value = json.prefix;
        document.getElementById('bot_enabled').checked = json.enabled;
    } catch (e) {}

    try {
        document.getElementById('log_bans').checked = json.logging.bans;
        document.getElementById('log_deletes').checked = json.logging.deletes;
        document.getElementById('log_timeouts').checked = json.logging.timeouts;
        document.getElementById('log_help_replies').checked = json.logging.help_replies;
        document.getElementById('log_settings_changes').checked = json.logging.settings_changes;
    } catch (e) {}

    try {
        table = document.getElementById('helper_settings');
        let checkbox = document.getElementById('helper_enabled');
        checkbox.checked = json.helper.enabled;
        for (i = 0; i < json.helper.rules.length; i++) {
            if (i > 0) addRowHelper('repeat_settings');
            rule = json.helper.rules[i];
            row = table.rows[i + 1];
            col = row.cells;
            col[1].firstChild.checked = rule.enabled;
            col[2].firstChild.value = rule.search;
            col[3].firstChild.checked = rule.exact;
            col[4].firstChild.value = rule.threshold;
            col[5].firstChild.value = rule.reply;
        }
    } catch (e) {}

    return json;
}