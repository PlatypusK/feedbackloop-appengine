var ACTION_CREATE_LOOP='create_loop'
var ACTION_VIEW_LOOP_RESULTS='view loop results'


function createNewLoop(createButton){
	$('#action').val(ACTION_CREATE_LOOP)
	$('#flaskForm').submit();
}
/**
*Puts the loop id of the selected loop in the payload as a string and submits the form
*asking the server to redirect to showing the survey
*/
function loopDetailsClicked(detButton){
	$('#action').val(ACTION_VIEW_LOOP_RESULTS)
	$('#payLoad').val(detButton.value)
	$('#flaskForm').submit()
}