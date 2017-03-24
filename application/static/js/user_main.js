var ACTION_SHOW_SURVEY='Show survey';

function getChosenLoop(loopId,activeLoops){
	for(var i=0;i<activeLoops.length;i++){
		if(activeLoops[i][3]==loopId){
			return activeLoops[i];
		}
	}
}
function selectSurvey(loopId){
	console.log(loopId);
	var payLoad=document.getElementById('payLoad');	
	payLoad.value=JSON.stringify(getChosenLoop(loopId.value,JSON.parse(payLoad.value)))
	document.getElementById('action').value=ACTION_SHOW_SURVEY;
	document.getElementById('flaskForm').submit();
	
}
function getMessageList(){
	var payLoad=document.getElementById('payLoad');
	console.log(payLoad)
	messages=[];
	loopInfoList=JSON.parse(payLoad.value)
	for(var i=0;i<loopInfoList.length;i++){
		loop=JSON.parse(loopInfoList[i][4])
		messages.push(loop[0].message)
	}
	return messages;

}

function showMessage(){
	var surveyString=document.getElementById('0_messageParagraph');
	var elmNr=0;
	messages=getMessageList();
	for(var i=0;i<messages.length;i++){
		document.getElementById(i+'_messageParagraph').innerHTML=messages[i];
		elmNr++;
	}
}
showMessage();