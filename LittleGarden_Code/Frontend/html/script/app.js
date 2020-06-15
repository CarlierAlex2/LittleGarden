const lanIP = `http://${window.location.hostname}:5000`;
const socket = io(`${lanIP}`);
const backend = lanIP + "/api/v1";

//#region ***  DOM references ***
let html_title;
let html_water, html_temp, html_light, html_humid;
let html_pump_button, html_pump_title;
let html_led_button, html_led_title;
let html_meting_list, html_period;

let html_settings, html_setting_title;
let html_setting_max, html_setting_min;
let html_setting_units;

let html_period_date_start, html_period_date_end;
let html_period_time_start, html_period_time_end;
let html_ip;

let selected_measuretype = 'water';
//#endregion


//#region ***  Callback-Visualisation - show___ ***
const showConsole = function(jsonObject) {
  console.log("SHOW in console")
  console.log(jsonObject);
};

const showMeasureLast = function(jsonObject) {
  console.log("SHOW last measurements")
  console.log(jsonObject);
  measurements = jsonObject.measurements;

  brightness = measurements.light;
  water = measurements.water;
  temperature = measurements.temp;
  humidity = measurements.humid;

  setMetingElement(html_light, brightness);
  setMetingElement(html_water, water);
  setMetingElement(html_temp, temperature);
  setMetingElement(html_humid, humidity);

  socket.emit("F2B_get_actuator", null);
};

const setMetingElement = function(html_element, measurement){
  measure_title = html_element.querySelector('.js-measure__title');
  measure_value = html_element.querySelector('.js-measure__value');
  unit = html_element.querySelector('.js-unit');
  comment = html_element.querySelector('.js-comment');

  value = measurement.value;
  value = Math.round(value * 10.0) / 10.0

  measure_value.innerHTML = value;
  unit.innerHTML = measurement.unit;
  if(comment)
  {
    comment.innerHTML = measurement.comment;
  }
};

const showMeasureFromPeriod = function(jsonObject) {
  console.log("SHOW measurements list")
  console.log(jsonObject);

  let htmlObject = '';
  measurements = jsonObject.measurements;
  showgraph(measurements)
  
  for (const group of measurements) {
    htmlObject += makeMeasureGroup(group)
  }

  html_meting_list.innerHTML = htmlObject;
};

const makeMeasureGroup = function(group){
  let htmlObject = '';
  //console.log(group);
  const day = group.day;
  const measurements = group.measurements;

  if (day != null)
  {
    console.log(day);
    htmlObject += `
    <section class="o-section-lg">
    <h2>${day}</h2>`;
  }

  if (measurements != null)
  {
    console.log(measurements);
    for (const meting of measurements) {
      htmlObject += makeMeasureElement(meting);
    }
  }

  if (day != null)
  {
    htmlObject += `
    </section>`;
  }

  return htmlObject;
};

const makeMeasureElement = function(meting){
  const timestamp = meting.timestamp;
  let value = meting.value;
  value = Math.round(value * 10.0) / 10.0
  const comment = meting.comment;
  const measureType = meting.measureType;
  const unit = meting.unit;
  const html_icon = makeIconElement(measureType);

  htmlObject = `
  <section class="o-section u-box-shadow u-rounded-sm u-background-white">
              <div class="o-content--relative o-content-padding-lg u-margin-negative-16">

                <div class="o-layout o-layout--justify-space-between o-layout--align-center">
                  <div class="u-1-of-2">
                    <div class="o-layout o-layout--gutter-sm o-layout--justify-start o-layout--align-center">
                    ${html_icon}
                      <p class="u-text--color-grey">${timestamp}</p>
                    </div>
                  </div>

                  <div class="u-1-of-2">
                    <div class="o-layout o-layout--gutter-sm o-layout--justify-start o-layout--align-center">
                      <div class="o-layout__item u-2-of-5"><p class="u-text--align-right">${value}</p></div>
                      <p class="o-layout__item u-1-of-4">${unit}</p>
                    </div>
                  </div>
                </div>
  `;

  if(comment.length > 1)
  {
    htmlObject += `                
    <div class="o-layout o-layout--justify-center o-layout--align-center">
    <p class="u-text-align-center">${comment}</p>
    </div>
    `;
  }
  
  htmlObject += `
  </div>
  </section>
  `;
  return htmlObject;
};

const makeIconElement = function(measureType){
  htmlObject ='';
  if(html_title)
  {
    if(measureType == "light")
    {
      htmlObject = `
      <h1 class="c-icon c-icon-xs c-icon--margin">
      <svg class="c-icon__symbol"
      id="Light_icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
        <title>Measure Icon</title>
        <path id="Path_120" data-name="Path 120" d="M0,0H24V24H0Z" fill="none"/>
        <path id="Path_121" data-name="Path 121" d="M20,15.31,23.31,12,20,8.69V4H15.31L12,.69,8.69,4H4V8.69L.69,12,4,15.31V20H8.69L12,23.31,15.31,20H20V15.31ZM12,18a6,6,0,1,1,6-6A6,6,0,0,1,12,18Z"/>
      </svg>
    </h1>
      `;
    }
    else if(measureType == "water")
    {
      htmlObject = `
      <h1 class="c-icon c-icon-xs c-icon--margin">
      <svg class="c-icon__symbol"
      id="Water_icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
        <path id="Path_124" data-name="Path 124" d="M24,0H0V24H24Z" fill="none"/>
        <path id="Path_125" data-name="Path 125" d="M17.66,7.93,12,2.27,6.34,7.93a8,8,0,1,0,11.32,0ZM12,19.59A6,6,0,0,1,7.76,9.35L12,5.1Z"/>
      </svg>
    </h1>
      `;
    }
    else if(measureType == "humid")
    {
      htmlObject = `
      <h1 class="c-icon c-icon-xs c-icon--margin">
      <svg class="c-icon__symbol"
      id="Moisture_icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
        <path id="Path_122" data-name="Path 122" d="M0,0H24V24H0Z" fill="none"/>
        <path id="Path_123" data-name="Path 123" d="M19.35,10.04a7.492,7.492,0,0,0-14-2A6,6,0,0,0,6,20H19a4.986,4.986,0,0,0,.35-9.96Z"/>
      </svg>
    </h1>
      `;
    }
    else if(measureType == "temp")
    {
      htmlObject = `
      <h1 class="c-icon c-icon-xs c-icon--margin">
      <svg class="c-icon__symbol"
      id="Temp_icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
        <path id="Path_134" data-name="Path 134" d="M0,0H24V24H0Z" fill="none"/>
        <g id="thermometer" transform="translate(2 -3)">
          <path id="Path_136" data-name="Path 136" d="M15,13V5A3,3,0,0,0,9,5v8a5,5,0,1,0,6,0M12,4a1,1,0,0,1,1,1V8H11V5A1,1,0,0,1,12,4Z" transform="translate(-2 3)" fill="#1a2615"/>
        </g>
      </svg>
    </h1>
      `;
    }
  }
  return htmlObject;
};

const showPeriod = function(jsonObject){
  dates = jsonObject.dates;
  console.log("SHOW period")
  console.log(dates);

  html_period_date_start.value = dates.dateStart;
  html_period_date_end.value = dates.dateEnd;

  html_period_time_start.value = dates.timeStart;
  html_period_time_end.value = dates.timeEnd;
};

const showSettings = function(jsonObject) {
  console.log("SHOW settings")
  console.log(jsonObject);
  settings = jsonObject.settings

  settingMax = settings.settingMax
  settingMin = settings.settingMin
  unit = settings.unit

  html_setting_max.value = settingMax;
  html_setting_min.value = settingMin;
  html_setting_units.unitMin.innerHTML = `Min ${unit}`
  html_setting_units.unitMax.innerHTML = `Max ${unit}`

  if(settings.measureType == "water" || settings.measureType == "humid")
  {
    html_setting_min.max = 100;
    html_setting_max.max = 100;
  }
  
  const html_setting_confirm  = document.querySelector('.js-setting-confirm-btn');
  html_setting_confirm.classList.remove("c-button-disabled");
};

const showIpAddress = function(jsonObject){
  console.log("SHOW ip addresses")
  console.log(jsonObject)
  ip_array = jsonObject.ip_array;
  let htmlObject = '';
  for(const ip of ip_array)
  {
    htmlObject += `<p class="u-text--word-wrap-break">${ip}</p>`;
  }
  html_ip.innerHTML = htmlObject;
};

const showgraph = function(measurements){
  console.log("SHOW graph")
  if (measurements.length > 0)
  {
    console.log(measurements);

    let converted_labels = [];
    let converted_data = [];
    let label = '';
    for(const group of measurements) {

      const group_list = group.measurements;
      for(const index in group_list) 
      {
        const measure = group_list[index];
        label = measure.label;
  
        converted_labels.push(label);
        converted_data.push(measure.value);
      }
    }
  
    converted_labels = converted_labels.reverse();
    converted_data = converted_data.reverse();
  
    let converted_labels_final = [];
    for(const index in converted_labels) 
    {
      label = converted_labels[index]
      converted_labels_final.push(label);
    }
  
    unit = measurements[0].measurements[0].unit;
    drawChart(converted_labels_final, converted_data, selected_measuretype, unit);
  }
  else
  {
    drawChart(null, null, selected_measuretype, "");
  }
};


const drawChart = function(converted_labels, converted_data, measureType, unit){
  const html_chart_container = document.querySelector('.js-chart-holder');
  height = 232;


  let htmlObject = `<canvas id="myChart" class="c-chart js-chart u-fill"></canvas>`;
  html_chart_container.innerHTML = htmlObject;


  let ctx = document.querySelector('.js-chart').getContext('2d');
  title_chart = `${html_title.innerHTML} in ${unit}`
  let config = {
      type: 'line', //specify what type of chart this is
      data:{
          labels: converted_labels,
          datasets:[
              {
                  label: title_chart, //label added at the top
                  backgroundColor: 'white',
                  borderColor: 'red',
                  data: converted_data, //data to bind to the chart
                  fill: false,
                  pointRadius: 0,
                  pointBorderColor: '#A1D98D',
                  pointBackgroundColor: '#E3FFD9',
                  borderColor: '#A1D98D',
                  backgroundColor: '#A1D98D',
                  pointStyle: 'triangle',
                  pointRotation: 180
              }
          ]
      },
      options: { //options to change style and behavior of the chart
        aspectRatio: 1.5,
        maintainAspectRatio: true,
          responsive: true,
          title: {
            display: false,
            text: title_chart
          },
          tooltips: {
              mode: 'index',
              intersect: true
          },
          nover: {
              mode: 'nearest',
              intersect: true
          },
          scales: {
              xAxes: [
                  {
                      display: true,
                      scaleLabel: {
                          display: false,
                          labelString: 'Timestamp'
                      },
                      ticks: {
                        autoSkip: true,
                        maxTicksLimit: 6
                    }
                  }
              ],
              yAxes: [
                  {
                      display: true,
                      scaleLabel: {
                          display: false,
                          labelString: `Measurement in ${unit}`
                      }
                  }
              ]
          }
      }
  };


  let myChart = new Chart(ctx, config);
};
//#endregion



//#region ***  Callback-No Visualisation - callback___  ***
const callBackError = function(jsonObject) {
  console.log(`ERROR: during processing of request ${jsonObject}`);
};

const callBackAddMeasurements = function(data) {
  if (data.count > 0) {
    console.log(data.status);
  }
};

const callBackChangeSetting = function(data) {
  console.log("UPDATE Settings");
  console.log(data);
};

const createMeasurement = function(){
  console.log('REQUEST CREATE new measurements')
  const url = `${backend}/measurements`;
  handleData(url, callBackAddMeasurements, callBackError, "POST", null);
};
//#endregion



//#region ***  Event Listeners - listenTo___ ***
const listenToChangeSettings = function(){
  console.log("LISTEN to setting change");
  if(html_setting_min)
  {
    html_setting_min.addEventListener('input', function(){
      settingValue = html_setting_min.value;
      jsonobject = {
        measureType: selected_measuretype,
        settingType: "min",
        value: settingValue
      };

      const url = `${backend}/settings/${selected_measuretype}`;
      handleData(url, callBackChangeSetting, callBackError, "PUT", JSON.stringify(jsonobject));
    });
  }

  if(html_setting_max)
  {
    html_setting_max.addEventListener('input', function(){
      settingValue = html_setting_max.value;
      jsonobject = {
        measureType: selected_measuretype,
        settingType: "max",
        value: settingValue
      };

      const url = `${backend}/settings/${selected_measuretype}`;
      handleData(url, callBackChangeSetting, callBackError, "PUT", JSON.stringify(jsonobject));
    });
  }
};

const listenToBack = function(){
  console.log("LISTEN to back button");
  const btn = document.querySelector(".js-back-btn");
  if(btn)
  {
    btn.addEventListener("click", function(){
      window.history.go(-1);
    })  
  }
};

const listenToNavigateDetail = function(){
  console.log("LISTEN to navigate to detail");
  const measurement_list = document.querySelectorAll(".js-measure");
  for (const parent of measurement_list){
    const btn = parent.querySelector(".js-detail-btn");
    if(btn)
    {
      btn.addEventListener("click", function(){
        measureType = this.getAttribute("data-measureType");
        link = `${window.location}/detail_page.html?measureType=${measureType}`;
        console.log(`Going to ${link}`);
        window.location = link;
      })  
    }
  }
};

const listenToAddButton = function(){
  console.log("LISTEN to UI");
  const metingBtn = document.querySelector(".js-measure-btn");
  if(metingBtn)
  {
    metingBtn.addEventListener("click", function(){
      createMeasurement();
    })  
  }
};

const listenToChangeType = function() {
  console.log("LISTEN to UI");
  const buttons = document.querySelectorAll(".js-type-btn");
  for (const btn of buttons){
    btn.addEventListener("click", function(){
      measureType = this.getAttribute("data-type");
      setSelectedType(measureType) 
    })  
  }
};

const listenToChangeDate = function() {
  if(html_period)
  {
    console.log("LISTEN to UI");
    html_period_date_start.addEventListener('input', getMeasurePeriod);
    html_period_date_end.addEventListener('input', getMeasurePeriod);
    html_period_time_start.addEventListener('input', getMeasurePeriod);
    html_period_time_end.addEventListener('input', getMeasurePeriod);
  };
};

const setSelectedType = function(measureType){
  selected_measuretype = measureType;
  console.log(`SET measurement type to ${measureType}`)
  if(html_meting_list)
  {
    getMeasurePeriod()
  }

  if(html_setting_max && html_setting_min)
  {
    getSettings()
  }
};

const listenToActuators = function(){
  if(html_pump_button)
  {
    console.log("LISTEN to water actuator");
    html_pump_button.addEventListener("click", function(){
      socket.emit("F2B_toggle_actuator", {"measureType": "water"})
    })  
  }

  if(html_led_button)
  {
    console.log("LISTEN to light actuator");
    html_led_button.addEventListener("click", function(){
      socket.emit("F2B_toggle_actuator", {"measureType": "light"})
    })  
  }
};

const listenToMainNavigation = function(){
  const html_nav  = document.querySelector('.js-nav');
  const html_nav_back  = document.querySelectorAll('.js-nav-back');
  const html_nav_btn  = document.querySelector('.js-nav-btn');

  if(html_nav && html_nav_back && html_nav_btn)
  {
    console.log("LISTEN to navigation events")
    html_nav_btn.addEventListener("click", function(){
      html_nav.classList.remove("c-ppopup-off");
      html_nav.classList.add("c-ppopup-on");
    })  

    for(const btn of html_nav_back)
    {
      btn.addEventListener("click", function(){
        html_nav.classList.add("c-ppopup-off");
        html_nav.classList.remove("c-ppopup-on");
      })  
  
    }
  }
}

const listenToSettingsButton_Popup = function(html_setting_btn){
  html_setting_btn.addEventListener("click", function(){
  getSettings();
  html_settings.classList.remove("c-ppopup-off");
  html_settings.classList.add("c-ppopup-on");
  })  
};

const listenToSettingsButton_Cancel = function(html_setting_cancel){
  html_setting_cancel.addEventListener("click", function(){
  html_settings.classList.remove("c-ppopup-on");
  html_settings.classList.add("c-ppopup-off");
  })  
};


const listenToSettingsButton_Confirm = function(html_setting_confirm){
  html_setting_confirm.addEventListener("click", function(){
    event.preventDefault();

    if(this.form.checkValidity())
    {
      this.disabled=false;
      html_setting_confirm.classList.remove("c-button-disabled");

      html_settings.classList.remove("c-ppopup-on");
      html_settings.classList.add("c-ppopup-off");
      settingValue_Min = html_setting_min.value;
      settingValue_Max = html_setting_max.value;

      jsonobject = {
        measureType: selected_measuretype,
        settingType: "min",
        value: settingValue_Min
      };
      let url = `${backend}/settings/${selected_measuretype}`;
      handleData(url, callBackChangeSetting, callBackError, "PUT", JSON.stringify(jsonobject));
  
      jsonobject = {
        measureType: selected_measuretype,
        settingType: "max",
        value: settingValue_Max
      };
      url = `${backend}/settings/${selected_measuretype}`;
      handleData(url, callBackChangeSetting, callBackError, "PUT", JSON.stringify(jsonobject));
    }
    else
    {
      this.disabled=true;
      html_setting_confirm.classList.add("c-button-disabled");
      return;
    }
  }) 
};

const listenToSettingValues = function(html_setting_confirm){
  html_setting_max.addEventListener("change", function(){
    if(this.form.checkValidity())
    {
      html_setting_confirm.disabled=false;
      html_setting_confirm.classList.remove("c-button-disabled");
    }
    else
    {
      html_setting_confirm.disabled=true;
      html_setting_confirm.classList.add("c-button-disabled");
    }
  }) 

  html_setting_min.addEventListener("change", function(){
    if(this.form.checkValidity())
    {
      html_setting_confirm.disabled=false;
      html_setting_confirm.classList.remove("c-button-disabled");
    }
    else
    {
      html_setting_confirm.disabled=true;
      html_setting_confirm.classList.add("c-button-disabled");
    }
  }) 
};

const listenToSettingsButton = function(){
  const html_setting_btn  = document.querySelector('.js-settings-btn');
  const html_setting_confirm  = document.querySelector('.js-setting-confirm-btn');
  const html_setting_cancel  = document.querySelector('.js-setting-cancel-btn');

  if(selected_measuretype == "water" || selected_measuretype == "light")
  {
    if(html_setting_btn && html_setting_confirm && html_setting_cancel)
    {
      console.log("LISTEN to setting events")
      listenToSettingsButton_Popup(html_setting_btn);
      listenToSettingsButton_Cancel(html_setting_cancel);
      listenToSettingsButton_Confirm(html_setting_confirm);
      listenToSettingValues(html_setting_confirm);
    }
  }
  else
  {
    html_setting_btn.classList.add("u-hide");
  }

};


const listenToUI = function() {
  listenToNavigateDetail();
  listenToChangeType();
  listenToAddButton();
  listenToChangeDate();
  listenToBack();
  //listenToChangeSettings();
  listenToSettingsButton();
  listenToActuators();
  listenToMainNavigation();
};

const listenToSocket = function () {
  socket.on("B2F_feedback", function(value) {
    console.log("B2F_feedback")
    console.log(value.feedback)
  });

  socket.on("B2F_update_page", function(value) {
    console.log("B2F_update_page - Request a page update")
    getPage_Home();
    getPage_Detail();
    getPage_Information();
  });

  socket.on("B2F_actuator_toggled", function(value) {
    console.log("B2F_actuator_toggled - Actuator toggled")
    console.log(value);
    measureType = value.measureType;
    status = value.status;

    html_obj = null;
    if(measureType == "water")
    {
      html_obj = html_pump_button;
    }
    if (measureType == "light")
    {
      html_obj = html_led_button;
    }
    
    if(html_obj != null)
    {
      if(status == 1)
      {
        html_obj.checked = true;
      }
      else
      {
        html_obj.checked = false;
      }
    }

  });
};
//#endregion


//#region ***  Data Access - get___ - general***
const getPage_Home = function(){
  console.info(`GET home page`);
  if(html_water && html_light && html_humid && html_temp)
  {
    getMeasurementLast();
  }
};

const getPage_Detail = function(){
  console.info(`GET detail page`);
  const querystring = new URLSearchParams(window.location.search);
  measureType = null;
  if (querystring.has("measureType")) 
  {
    measureType = querystring.get("measureType");
  };

  if(html_period)
  {
    getPeriodSetup();
  };

  if(html_title)
  {
    if(measureType == "light")
    {
      html_title.innerHTML = "Brightness";
    }
    else if(measureType == "water")
    {
      html_title.innerHTML = "Water Level";
    }
    else if(measureType == "humid")
    {
      html_title.innerHTML = "Humidity";
    }
    else if(measureType == "temp")
    {
      html_title.innerHTML = "Temperature";
    }
  };


  if(html_setting_title && html_title)
  {
    if (measureType != null) {
      setSelectedType(measureType);
      html_setting_title.innerHTML = `${html_title.innerHTML} settings`;
    } 
    else {
      console.log("ERROR: No measureType found");
    }
  };
};

const getPage_Information = function(){
  console.info(`GET information page`);
  if(html_ip)
  {
    getInformation();
  }
  else
  {
    console.info(`ERROR: No ip element found`);
  }
};
//#endregion


//#region ***  Data Access - get___ - specific ***
const getMeasurementLast = function() {
  console.info("GET latest measuremenets");
  const url = `${backend}/measurements/latest`;
  handleData(url, showMeasureLast, callBackError, "GET");
};

const getPeriodSetup = function(){
  console.info("GET setup periodee");
  const url = `${backend}/date`;
  handleData(url, showPeriod, callBackError, "GET");
};

const getMeasurePeriod = function() {
  console.info("GET measurements from period");
  
  start = `${html_period_date_start.value} ${html_period_time_start.value}`;
  end = `${html_period_date_end.value} ${html_period_time_end.value}`
  const jsonObject = {
    periodStart: start, 
    periodEnd: end
  };
  console.log(jsonObject);
  const url = `${backend}/measurements/period/${selected_measuretype}`;
  handleData(url, showMeasureFromPeriod, callBackError, "PUT", JSON.stringify(jsonObject));
};

const getSettings = function() {
  console.info(`GET settings for ${selected_measuretype}`);
  const url = `${backend}/settings/${selected_measuretype}`;
  handleData(url, showSettings, callBackError, "GET");
};

const getInformation = function() {
  console.info(`GET information`);
  const url = `${backend}/ip`;
  handleData(url, showIpAddress, callBackError, "GET");
};
//#endregion


//#region ***  Data Access - post___ ***

//#endregion



//#region ***  INIT / DOMContentLoaded  ***
const initDetail = function(){
  console.info(`INIT detail page`);
  html_title  = document.querySelector('.js-header__title');
  html_settings  = document.querySelector('.js-settings');
  html_setting_title  = document.querySelector('.js-settings_title');
  html_meting_list  = document.querySelector('.js-measure-list');
  html_setting_max = document.querySelector('.js-setting-max');
  html_setting_min = document.querySelector('.js-setting-min');
  html_setting_units = {
    unitMax: document.querySelector('.js-setting-unit-max'),
    unitMin: document.querySelector('.js-setting-unit-min')
  };
  html_period = document.querySelector('.js-period');

  if(html_period)
  {
    html_period_date_start = html_period.querySelector('#dateStart');
    html_period_time_start = html_period.querySelector('#timeStart');
    html_period_date_end = html_period.querySelector('#dateEnd');
    html_period_time_end = html_period.querySelector('#timeEnd');
  };

  getPage_Detail();
};

const initInfo = function(){
  console.info(`INIT info page`);
  html_ip = document.querySelector('.js-ip_address');
  getPage_Information();
};

const initHome = function(){
  console.info(`INIT home page`);
  html_datum = document.querySelector('.js-date');
  html_water = document.querySelector('.js-measure--water');
  html_light = document.querySelector('.js-measure--light');
  html_humid = document.querySelector('.js-measure--humid');
  html_temp = document.querySelector('.js-measure--temp');

  if(html_water)
  {
    html_pump_button = html_water.querySelector('.js-actuator-btn');
    html_pump_title = html_water.querySelector('.js-actuator-title');
  }

  if(html_water)
  {
    html_led_button = html_light.querySelector('.js-actuator-btn');
    html_led_title = html_light.querySelector('.js-actuator-title');
  }


};


const init = function () {
  console.info("DOM geladen");
  initHome();
  initDetail();
  initInfo();

  listenToUI();
  listenToSocket();
};

document.addEventListener("DOMContentLoaded", init);
//#endregion