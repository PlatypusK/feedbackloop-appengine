var ACTION_SEARCH="search";
function searchChannel(){
	$('#action').val(ACTION_SEARCH)
	$('#payLoad').val($('#searchBox').val())
	console.log($('#payLoad').val())
	$('#flaskForm').submit();
}
function channelDetails(detailsButton){
}