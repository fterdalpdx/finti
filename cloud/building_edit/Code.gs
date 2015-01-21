
/**
 * Get the URL for the Google Apps Script running as a WebApp.
 */

function getScriptUrl() {
 var url = ScriptApp.getService().getUrl();
 return url;
}


/**
 * Handle page loading and routing
 */

function doGet(e) {
  Logger.log( Utilities.jsonStringify(e));
  if (!e.parameter.building) {
      return HtmlService
          .createTemplateFromFile("buildings")
          .evaluate();
  } else {
      var t = HtmlService.createTemplateFromFile("building");
      t.data = e.parameter.building;
      return t.evaluate();
  }
}


/**
 * Include file (stylesheet/javascript) in HTML
 */
function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename)
      .setSandboxMode(HtmlService.SandboxMode.IFRAME)
      .getContent();
}


/**
 * Fetch an individual building
 */

function getBuilding(building_identifier) {
  Logger.log("getBuilding: fetching building: " + building_identifier );
  var url = PropertiesService.getScriptProperties().getProperty("ws_url");
  var params = genFetchURLparams('GET');
  var response = UrlFetchApp.fetch(url + "/erp/gen/1.0/buildings/" + building_identifier, params);
  var json = response.getContentText();
  var building = JSON.parse(json);
  Logger.log("getBuilding: " + json );
  return building;
}


/**
 * Fetch an individual building history
 */

function getBuildingHistory(building_identifier) {
  Logger.log("getBuildingHistory: fetching building history: " + building_identifier );
  var params = genFetchURLparams('GET');
  var url = PropertiesService.getScriptProperties().getProperty("ws_url");
  var response = UrlFetchApp.fetch(url + "/erp/gen/1.0/buildings/" + building_identifier + "/history", params);
  var json = response.getContentText();
  Logger.log("getBuildingHistory: " + json );
  return json.replace(/'/g,"&quot;");
}


/**
 * Fetch the list of all PSU buildings
 */

function getBuildings() {
  var params = genFetchURLparams('GET');
  var url = PropertiesService.getScriptProperties().getProperty("ws_url");
  var response = UrlFetchApp.fetch(url + "/erp/gen/1.0/buildings", params);
  var json = response.getContentText();
  var buildings = JSON.parse(json);
  return buildings;
}


/**
 * Create a building descriptor
*/

function makeBuilding(form) {
  var data = {
    "long_name": form.longname,
    "short_name": form.shortname,
    "building_code": form.code,
    "street_address": form.street,
    "city": form.city,
    "state_code": form.state,
    "zipcode": form.zip,
    "centroid_lat": parseFloat(form.centlat),
    "centroid_long": parseFloat(form.centlong),
    "rlis_lat": parseFloat(form.rlislat),
    "rlis_long": parseFloat(form.rlislong),
    "geolocate_lat": parseFloat(form.geolat),
    "geolocate_long": parseFloat(form.geolong),
    "building_identifier": form.id,
    "from_date": form.fromdate,
    "to_date": form.todate
  };
  return data;
}

/**
 * Return an empty building descriptor
*/

function makeEmptyBuilding() {
  var data = {
    "long_name": "",
    "short_name": "",
    "building_code": "",
    "street_address": "",
    "city": "",
    "state_code": "",
    "zipcode": "",
    "centroid_lat": "",
    "centroid_long": "",
    "rlis_lat": "",
    "rlis_long": "",
    "geolocate_lat": "",
    "geolocate_long": "",
    "building_identifier": "",
    "from_date": "",
    "to_date": ""
  };
  return data;
}

/**
 * Notify interested users about building change
*/

function sendEmail(action, bldgid)
{
  var recip = "noreply@pdx.edu";
  var subj = "Building list has been modified";
  var mesg = bldgid + ' has been ' + action;
  MailApp.sendEmail(recip, subj, mesg);
}


/**
 * Create a new building
*/

function postBuilding(form) {

  Logger.log("postBuilding");
  var data = makeBuilding(form);

  payload = JSON.stringify(data);
  Logger.log('payload: ' + payload);

  var ws_url = PropertiesService.getScriptProperties().getProperty("ws_url");
  var url = ws_url + "/erp/gen/1.0/buildings";
  var options = {
    "method": "post", 
    "contentType": "application/json", 
    "payload": payload, 
    "headers": {
      "Accept-Encoding": "*",
      "Authorization": "Basic " + Utilities.base64Encode(user_token + ':')
    }
  };

  var response = UrlFetchApp.fetch(url, options);
  Logger.log('response after fetch');
  Logger.log(response);
  respdata = JSON.parse(response);
  Logger.log('parsed json: ' + respdata);
  bldgID = respdata["building_identifier"];
  Logger.log('id:' + bldgID);
  sendEmail('created', bldgID);
  return 'creation|' + bldgID + '|' + Logger.getLog();
}


/**
 * Update an existing building
 * Building identifier cannot be updated
*/

function putBuilding(form) {

  Logger.log("putBuilding");
  var data = makeBuilding(form);

  payload = JSON.stringify(data);
  Logger.log('payload: ' + payload);

  var user = Session.getActiveUser().toString();
  var user_token = PropertiesService.getScriptProperties().getProperty(user);
  var ws_url = PropertiesService.getScriptProperties().getProperty("ws_url");
  var url = ws_url + "/erp/gen/1.0/buildings";
  Logger.log('url:' + url);
  var options = { 
    "method": "put", 
    "contentType": "application/json", 
    "payload": payload, 
    "headers": {
      "Accept-Encoding": "*",
      "Authorization": "Basic " + Utilities.base64Encode(user_token + ':')
    }, 
    "muteHttpExceptions": true
  };
  
//  var request = UrlFetchApp.getRequest(url, options);
//  Logger.log('request');
//  Logger.log(request);
  var response = UrlFetchApp.fetch(url, options);
  Logger.log('response after fetch');
  Logger.log(response);
  respdata = JSON.parse(response);
  bldgID = respdata["building_identifier"];
  Logger.log('id:' + bldgID);
  sendEmail('updated', bldgID);
  
  return 'update|' + bldgID + '|' + Logger.getLog();
}


/**
 * Remove an existing building
*/

function deleteBuilding(form) {

  Logger.log("deleteBuilding");
  var ws_url = PropertiesService.getScriptProperties().getProperty("ws_url");
  var url = ws_url + "/erp/gen/1.0/buildings/" + form.id;
  Logger.log('url:' + url);
  var options = {"method": "delete"};
  var response = UrlFetchApp.fetch(url, options);
  Logger.log('response after fetch');
  Logger.log(response);
  sendEmail('deactivated', form.id);
  return 'deactivation|' + form.id + '|' + Logger.getLog();
}

/**
 * Generate a Simple HTTP auth header for the FetchURL request
 */
function genFetchURLparams(verb) {
  var user = Session.getActiveUser().toString();
  Logger.log('genFetchURLparams: user: ' + user);
  var user_token = PropertiesService.getScriptProperties().getProperty(user);
  var headers = {
    "Authorization": "Basic " + Utilities.base64Encode(user_token + ':')
  };
  
  var params = {
    "method": verb,
    "headers": headers
  };
  return params;
}

