var ACTION_SEARCH="search";
var ACTION_SUBSCRIBE="subscribe";
function searchChannel(){
	var action=document.getElementById("action");
	action.value=ACTION_SEARCH;
	var searchWord=document.getElementById("payLoad");
	console.log(searchWord);
	searchWord.value=document.getElementById("searchBox").value;
	console.log(searchWord);
	var searchForm=document.getElementById("flaskForm");
	console.log(searchForm);
	searchForm.submit();
}
function subscribe(subscribeTo){
	console.log(subscribeTo.value);
	var action=document.getElementById("action");
	action.value=ACTION_SUBSCRIBE;
	var subscribeToChannel=document.getElementById("payLoad");
	subscribeToChannel.value=subscribeTo.value;
	var searchForm=document.getElementById("flaskForm");
	console.log(searchForm);
	searchForm.submit();
}