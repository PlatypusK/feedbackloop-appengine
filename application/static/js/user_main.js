var ACTION_SHOW_SURVEY='Show survey';

function getChosenLoop(loopId,activeLoops){
	for(var i=0;i<activeLoops.length;i++){
		console.log(activeLoops[i][3])
		console.log(loopId)
		if(activeLoops[i][3]==loopId){
			return activeLoops[i];
		}
	}
	return "no loop found"
}

function selectSurvey(loopId){
	$('#payLoad').val(JSON.stringify(getChosenLoop(loopId.value,JSON.parse($('#payLoad').val()))))
	$('#action').val(ACTION_SHOW_SURVEY)
	$('#flaskForm').attr('action','/show_survey')
	$('#flaskForm').submit();
}
// function getMessageList(){
	// var payLoad=document.getElementById('payLoad');
	// console.log(payLoad)
	// messages=[];
	// loopInfoList=JSON.parse(payLoad.value)
	// for(var i=0;i<loopInfoList.length;i++){
		// loop=JSON.parse(loopInfoList[i][4])
		// messages.push(loop[0].message)
	// }
	// return messages;
// }

// function showMessage(){
	// var surveyString=document.getElementById('0_messageParagraph');
	// messages=getMessageList();
	// for(var i=0;i<messages.length;i++){
		// document.getElementById(i+'_messageParagraph').innerHTML=messages[i];
	// }
// }
// showMessage();