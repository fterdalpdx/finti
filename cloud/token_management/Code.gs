/*
 * Handle GET requests to this app
 */
function doGet(event) {
  if (event.parameter.log_index) {
    var output = HtmlService.createHtmlOutput();
    var log_entry = getLogEntry(event.parameter.log_index);
    output.append(log_entry);
    return output;    
  } else {
    var token = obtainToken();
    var template = HtmlService.createTemplateFromFile('token');
    template.data = token;
    return template.evaluate()
    .setSandboxMode(HtmlService.SandboxMode.IFRAME);
  }
}

/*
 * Handle POST requests to this app
 */
function doPost(eventInfo) {
  Logger.log(eventInfo);
  var token;
  
  if ("token" in eventInfo.parameter) {
    Logger.log("found token");
    token = resetToken();
  } else {
    Logger.log("did not find token");
    token = deleteToken();
  }
  var template = HtmlService.createTemplateFromFile('token');
  template.data = token;
  return template.evaluate().setSandboxMode(HtmlService.SandboxMode.IFRAME);
}

/**
 * Fetch an existing token for a user, generate one otherwise
 */
function getLogEntry(){
  return "incididunt ut labore et dolore";
}

/**
 * Fetch an existing token for a user, generate one otherwise
 */
function obtainToken(){
  var user = Session.getActiveUser().toString();
  var token = fetch_token(user);
  if (token == "") {
    token = "you do not currently possess a token";
  } else {
    token = "you have an existing token";
  }
  return token;
}

function bin2Hex(s) {
  var hex = '', h;
  for (var i = 0, l = s.length; i < l; ++i) {
    h = (s[i] < 0 ? (0xFF + s[i] + 1) : s[i]).toString(16)
    if (h.length < 2) {
      h = "0" + h;
    }
    hex += h;
  }
  return hex;
}

/**
 * Creates a hash of the user token for storage
 */

function hash(token) {
  var digest = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, token, Utilities.Charset.US_ASCII);
  return(bin2Hex(digest));
}

/**
 * Delete the active users PSU Web Services token
 */
function deleteToken() {
  var user = Session.getActiveUser().toString();
  Logger.log("deleteToken(): active user: " + user);
  var token = fetch_token(user);
  if (token == "") {
    return("you do not currently possess a token");
  } else {
    remove_token(user);
    return("token invalidated");
  }
}

/**
 * Reset the active users PSU Web Services token
 */
function resetToken() {
  var user = Session.getActiveUser().toString();
  var new_token = generate_token();
  
  Logger.log("resetToken(): active user: " + user + ", new token: " + new_token);
  store_token(user, new_token);
  return(new_token);
}

/**
 * Fetch a users token from storage
 */
function fetch_token(user) {
  var ss_id = PropertiesService.getScriptProperties().getProperty("spreadsheet_id");
  var ss = SpreadsheetApp.openById(ss_id);
  var sheet = ss.getSheets()[0];
  var column = 1;
  var last_row = sheet.getLastRow();
  if (last_row == 0) {
    return "";
  }
  var column_values = sheet.getRange(1, column, sheet.getLastRow()).getValues();
  var search_result = column_values.findIndex(user);
  var token = "";
  
  Logger.log("fetch_token(): searching for user: " + user);
  if (search_result == -1) {
    Logger.log("fetch_token(): did not find user: " + user);
  } else {
    Logger.log("fetch_token(): found user: " + user);
    var cell = sheet.getRange("B" + search_result);
    token = cell.getValue();
    Logger.log("fetch_token(): token for user: " + token); 
  }
  return token;
}

Array.prototype.findIndex = function(search){
  if(search == "") return false;

  for (var i=0; i<this.length; i++) {
    if (this[i] == search) {
      Logger.log("findIndex(): found: " + search);
      return i + 1;
    }
  }

  return -1;
} 

/**
 * Store a users token into storage
 */
function store_token(user, token) {
  Logger.log("store_token(): storing token for user: " + user);
 
  var ss_id = PropertiesService.getScriptProperties().getProperty("spreadsheet_id");
  var ss = SpreadsheetApp.openById(ss_id);
  var sheet = ss.getSheets()[0];
  var change_log = ss.getSheets()[1];

  var now = Utilities.formatDate(new Date(), "GMT", "yyyy-MM-dd'T'HH:mm:ss'Z'");
  // The initial case with no stored data
  var last_row = sheet.getLastRow();
  if (last_row == 0) {
    sheet.appendRow([user, hash(token), now]);
    change_log.appendRow([user, hash(token), now, "add"]);
    notify_observers(change_log.getLastRow());
    return;
  }
  
  var users = sheet.getRange(1, 1, sheet.getLastRow(),1).getValues();
  
  var user_index = users.findIndex(user);
  
  Logger.log("store_token(): searching for user: " + user);
  if (user_index == -1) {
    Logger.log("store_token(): did not find user: " + user + ", appending new user and token");
    sheet.appendRow([user, hash(token), now]);
    change_log.appendRow([user, hash(token), now, "add"]);
    notify_observers(change_log.getLastRow());
  } else {
    Logger.log("store_token(): found user: " + user);
    var cell = sheet.getRange("B" + user_index + ":C" + user_index);
    cell.setValues([[hash(token), now]]);
    Logger.log("store_token(): setting token for user: " + token); 
    change_log.appendRow([user, hash(token), now, "update"]);
    notify_observers(change_log.getLastRow());
  }
}

/**
 * Notify observers of a user token changes event 
 */

function notify_observers(log_index) {
  var ws_url = PropertiesService.getScriptProperties().getProperty("ws_url");
  var params = {
    "validateHttpsCertificates": false
  };
  var response = UrlFetchApp.fetch(ws_url + "/erp/gen/1.0/tokens/" + log_index, params);
}

/**
 * Remove a user and their token from storage
 */

function remove_token(user) {
  //var user = Session.getActiveUser().toString();
  Logger.log("remove_token(): storing token for user: " + user);

  var ss_id = PropertiesService.getScriptProperties().getProperty("spreadsheet_id");
  var ss = SpreadsheetApp.openById(ss_id);
  var sheet = ss.getSheets()[0];
  var change_log = ss.getSheets()[1];  
  var users = sheet.getRange(1, 1, sheet.getLastRow(),1).getValues();
  var now = Utilities.formatDate(new Date(), "GMT", "yyyy-MM-dd'T'HH:mm:ss'Z'");
  
  var user_index = users.findIndex(user);
  
  Logger.log("remove_token(): searching for user: " + user);
  if (user_index == -1) {
    Logger.log("remove_token(): did not find user: " + user);
  } else {
    Logger.log("remove_token(): found user: " + user);
    var cell = sheet.getRange("B" + user_index);
    token = cell.getValue();
    sheet.deleteRow(user_index);
    Logger.log("store_token(): deleted token for user: " + user); 
    change_log.appendRow([user, token, now, "delete"]);
    notify_observers(change_log.getLastRow());
  }
  if (user_index == -1) return false; else return true;
}

/**
 * Generate a Simple HTTP auth header for the FetchURL request
 */
function genFetchURLparams(verb) {
  var user = Session.getActiveUser().toString();
  var user_token = PropertiesService.getScriptProperties().getProperty(user);
  var headers = {
    "Authorization": "Basic " + Utilities.base64Encode(user_token + ':')
  };
  
  var params = {
    "method": verb,
    "headers": headers,
    "validateHttpsCertificates": false
  };
}


/**
 * Pull-in files in include in the current context
 */
function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename)
  .setSandboxMode(HtmlService.SandboxMode.IFRAME)
  .getContent();
}

/**
 * Generate a random token for a useri
 */
function generate_token() {
  function s4() {
    return Math.floor((1 + Math.random()) * 0x10000)
               .toString(16)
               .substring(1);
  }
  var token = s4() + s4() + '-' + s4() + '-' + s4() + '-' +
           s4() + '-' + s4() + s4() + s4();
  
  Logger.log("token: " + token );
  return token;
}


/**
 * Get the URL for the Google Apps Script running as a WebApp.
 */

function getScriptUrl() {
 var url = ScriptApp.getService().getUrl();
 return url;
}

function getId() {
  Logger.log("id: " + SpreadsheetApp.getActive().getId());
}

/**
 * Run the unit-test suite
 */

function unit_test() {
  test_store_token();
  test_remove_token();
  test_non_existing_user();
  test_remove_non_user();
  test_hash();
}

function test_non_existing_user(){
  var user = "esmerelda_weatherwax@pdx.edu";
  
  token = fetch_token(user);
  assert_true(token == "", "verify non-existant users are handled correctly");
}

function test_remove_non_user(){
  var user = "esmerelda_weatherwax@pdx.edu";
  
  status = remove_token(user);
  assert_true(status == false, "verify removing a non-users is handled correctly");
}

function test_remove_token(){
  var new_token = generate_token();
  var user = "nacmacfeegle@pdx.edu";
  
  var token = fetch_token(user);
  if (token != "") {
    remove_token(user);
  }
  
  store_token(user, new_token);
  remove_token(user);
  
  token = fetch_token(user);
  assert_true( token == "", 'verify tokens are removed correctly');
}

function test_hash(){
  var token = "1ca6f057-5439-e23a-5974-e066f04e578f";
  var hash_val = hash(token);
  var expected_hash_val = "q0ftofCSISHKiIDlcJW7M9ef0SDc5S5z6a01TJzhj3M=";
  
  assert_true(hash_val == expected_hash_val, "verify that the hash method is consistant");
}

function test_store_token(){
  var new_token = generate_token();
  var user = "nacmacfeegle@pdx.edu";
  
  var token = fetch_token(user);
  if (token != "") {
    remove_token(user);
  }
  
  store_token(user, new_token);
  token = fetch_token(user);
  assert_true( token == new_token, 'verify tokens are stored correctly');
  remove_token(user);
}

function assert_true(cond, msg) {
  if (cond) {
    Logger.log('===============  OK: ' + msg);
  } else {
    Logger.log('============= ERROR: ' + msg);
  }
}
    
