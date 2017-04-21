# feedbackloop-appengine

This project was started with the aim of creating surveys quickly and painlessly and distributing them to all subscribed students in a class instantly. It does this by utilizing a fast and user-friendly interface for creating the surveys and using web hooks to display notifications on subscribed devices whenever new surveys are published. The hope is that the notification options along with the ease of use should facilitate quicker and more frequent answers from students and smaller and more directed surveys from teachers. 

Assuming the replies to the surveys are indeed much quicker using this application, it is possible to ask follow up questions whenever a set of answers leads to new questions. This would be very slow with a static website serving a single survey for weeks at a time relying on students to go there on their own initiative

# Technology
The backend is created in Flask. The frontend is written in javascript using bootstrap templates. The notifications are implemented using the OneSignal REST Api.

# Unittests

Unittests for the backend are in the test folder at the root of the application. Unittests for the javascript is in the application/static/js/jstests/qunit folder. The tests for the backend are a mix of unittests and integration tests as much of the functionality can only be properly tested with a simulated database. The project aims for a coverage of 90% or more on all backend code and javascript code.

# Planned features that have not yet been implemented

Notifications will not work on iOS mobile as web hooks are not implemented yet. To get this working a native app must be created or the current app must be integrated into a minimal webview with notification capability and put on apple store.

Blackboard integration. It would be good to add all the people in a class that are members on blackboard to the subscribers

User Interface needs some polishing

# Explanatory remarks

In this project, loop is used as a synonym for survey. This was originally meant to be the name used in the actual GUI, but it felt gimmicky and user testing showed it to be confusing. It remains in the codebase though.

The payLoad field is used in most forms to send information to the client. In most of the javascript, the client alters the value of this field prior to submitting it to the server. it also changes the action field value which tells the view function what the client wants. The form attributes are also changed in some client code to call different view functions or GET instead of POST.

Passwords are stored in the flask session and passed to the server over HTTPs on each request. This can be easily changed into token based authentication if desired.

# Deployment

A local server can be run with dev_appserver.py. It is assumed that Python 2.7.9 is used as the SSL library referenced in app.yaml is not compatible with higher versions

The app is deployed to appengine using the command “gcloud app deploy”. This is assuming a project has already been created on appengine and the gcloud tool installed with the correct project selected. To set the app engine id for deployment use the command “gcloud config set project [PROJECT-ID]”. The gcloud tool is part of the App engine SDK toolset. This is useful for testing a new deployment when the application goes live. This can be done in the admin panel on appengine. To use the notification functionality it is necessary to create a new OneSignal application, point it to the new address in the onesignal admin panel and update the Authorization parameter and App id parameter in the util_notify.py file on the server. It is also necessary to update the appId in onesignal_app_setup.js. Remember that the authorization parameter should be kept a secret in a production deployment, so don’t use the one on github for anything except testing. This should be considered a password for being allowed to post notifications to OneSignal


