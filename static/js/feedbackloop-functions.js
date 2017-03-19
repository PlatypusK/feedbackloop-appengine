var questionDivs=[];



function changeclass (id, newCssClassName) {
		document.getElementById(id).className = newCssClassName;
}
function setNavItemActive(){
	if(document.URL.indexOf("login") >= 0){ 
		changeclass("login_link", "nav-item active")
	}
	else if(document.URL.indexOf("new_user") >= 0){
		changeclass("new_user", "nav-item active")
	}
	else if(document.URL.indexOf("forgot_password") >= 0){
		changeclass("forgot_password", "nav-item active")
	}
	else if(document.URL.indexOf("about") >= 0){
		changeclass("about", "nav-item active")
	}
	else if(document.URL.indexOf("user_main") >= 0){
		changeclass("user_main", "nav-item active")
	}
	else if(document.URL.indexOf("view_owned_channels") >= 0){
		changeclass("view_owned_channels", "nav-item active")
	}	
	else if(document.URL.indexOf("subscribed_channels") >= 0){
		changeclass("subscribed_channels", "nav-item active")
	}
}
/**
*Lets you show a toast which is a short message that fades away
*requires a jquery style id string for a html object of the form
*<div class='toast' id="toast" style='display:none'></div>
*Also requires the class .toast defined in feedbackloop.css
*/
function toast($id, message){
	$($id).text(message);
	$($id).stop().fadeIn(400).delay(3000).fadeOut(400);
}
setNavItemActive()
