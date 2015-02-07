
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
  var response = UrlFetchApp.fetch(url + "/org/v1/buildings/" + building_identifier, params);
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
  var response = UrlFetchApp.fetch(url + "/org/v1/buildings/" + building_identifier + "/history", params);
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
  var response = UrlFetchApp.fetch(url + "/org/v1/buildings", params);
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
  var defaulted_data = defaultify(data);
  return defaulted_data;
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
    "city": "Portland",
    "state_code": "OR",
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

/*
 * Add reasonable defaults for required data when not specified
 */
function defaultify(building){
  if (building["street_address"] != null) {
    // Yea, we have a start
    if (building["city"] == null || building["city"] == "") {
      building["city"] = "Portland";
    }
    if (building["state_code"] == null || building["state_code"] == "") {
      building["state_code"] = "OR";
    }
    var street_addr = 
        building["street_address"] + ", "
        + building["city"] + " " + building["state_code"];

    Logger.log("defaultify(): geolocating address: " + street_addr);
    var location = pdxGeolocate(street_addr);
    
    if (building["centroid_lat"] == null || isNaN(parseFloat(building["centroid_lat"]))) {
      building["centroid_lat"] = location[0];
    }
  
    if (building["centroid_long"] == null || isNaN(parseFloat(building["centroid_long"]))) {
      building["centroid_long"] = location[1];
    }
  
    if (building["rlis_lat"] == null || isNaN(parseFloat(building["rlis_lat"]))) {
      building["rlis_lat"] = location[0];
    }
  
    if (building["rlis_long"] == null || isNaN(parseFloat(building["rlis_long"]))) {
      building["rlis_long"] = location[1];
    }
  
    if (building["geolocate_lat"] == null || isNaN(parseFloat(building["geolocate_lat"]))) {
      building["geolocate_lat"] = location[0];
    }
  
    Logger.log("defaultify(): building[geolocate_long]: " + building["geolocate_long"]);
    if (building["geolocate_long"] == null || isNaN(parseFloat(building["geolocate_long"]))) {
      building["geolocate_long"] = location[1];
      Logger.log("defaultify(): setting geolocate_long");
    }
  }
  return building;
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
  var url = ws_url + "/org/v1/buildings";
  var options = {
    "method": "post", 
    "contentType": "application/json", 
    "payload": payload, 
    "headers": {
      "Accept-Encoding": "*",
      "Authorization": "Basic " + Utilities.base64Encode(user_token + ':')
    },
    "validateHttpsCertificates": false
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
  var url = ws_url + "/org/v1/buildings";
  Logger.log('url:' + url);
  var options = { 
    "method": "put", 
    "contentType": "application/json", 
    "payload": payload, 
    "headers": {
      "Accept-Encoding": "*",
      "Authorization": "Basic " + Utilities.base64Encode(user_token + ':')
    }, 
    "muteHttpExceptions": true,
    "validateHttpsCertificates": false
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
 * Geolocate a building around Portland
 */

function pdxGeolocate(address){
  response = Maps.newGeocoder().setBounds(44.1419049,-120.5380992, 45.977013, -116.945570).geocode(address)
  var result = response.results[0];
  Logger.log("pdxGeolocate() geolocated: " + address);
  return [result.geometry.location.lat, result.geometry.location.lng];
}

/**
 * Remove an existing building
*/

function deleteBuilding(form) {

  Logger.log("deleteBuilding");
  var ws_url = PropertiesService.getScriptProperties().getProperty("ws_url");
  var url = ws_url + "/org/v1/buildings/" + form.id;
  Logger.log('url:' + url);
  var options = {
    "method": "delete",
    "validateHttpsCertificates": false
  };
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
    "headers": headers,
    "validateHttpsCertificates": false
  };
  return params;
}

/**
 * Run the unit-test suite
 */
function unittest(){
  testpdxGeolocate();
  testdefaultify();
}

/**
 * Test pdxGeolocate
 */
function testpdxGeolocate(){
  var address = "2000 SW 5TH AVE";
  var location = pdxGeolocate(address);
  Logger.log("lat: " + location[0] + ", long: " + location[1]);
  assert_true( location[0] == 45.50849270000001 && location[1] == -122.6830174, "verify the geolocated address is reasonable");
}

/**
 * Test defaultify
 */ 
function testdefaultify(){
  var bld = makeEmptyBuilding();
  bld["street_address"] = "2000 SW 5TH AVE";
  var better_bld = defaultify(bld);
  assert_true(better_bld["centroid_long"] == -122.6830174, "verify default values are added");
  assert_true(better_bld["geolocate_lat"] == 45.50849270000001, "verify default values are added");
}


/**
 * Report and check unit-test results
 */
function assert_true(cond, msg) {
  if (cond) {
    Logger.log('===============  OK: ' + msg);
  } else {
    Logger.log('============= ERROR: ' + msg);
  }
}


