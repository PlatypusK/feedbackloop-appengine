var ACTION_SEARCH="search";
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
function channelDetails(detailsButton){
}
	