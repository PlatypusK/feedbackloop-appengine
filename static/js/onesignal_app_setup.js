var OneSignal = window.OneSignal || [];
OneSignal.push(function() {
  // Be sure to call this code *before* you initialize the web SDK
  
  // This registers the workers at the root scope, which is allowed by the HTTP header "Service-Worker-Allowed: /"
  OneSignal.SERVICE_WORKER_PARAM = { scope: '/' };
});


OneSignal.push(["init", {
  path: '/static/js/',
  appId: "b3baf272-6679-4697-99bb-63d2b2c37b0e",
  autoRegister: true,
  notifyButton: {
	enable: true /* Set to false to hide */
  }
}]);
