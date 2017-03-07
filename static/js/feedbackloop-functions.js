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
}
setNavItemActive()
