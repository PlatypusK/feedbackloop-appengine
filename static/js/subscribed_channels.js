var ACTION_SEARCH="1";
function searchChannel(){
	var action=document.getElementById("action");
	action.value=ACTION_SEARCH;
	var searchWord=document.getElementById("searchWord");
	searchWord.value=document.getElementById("searchBox").value;
	var searchForm=document.getElementById("flaskForm");
	console.log(searchForm);
	searchForm.submit();
}