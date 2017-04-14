"use strict";
var ACTION_SUBMIT_REPLY="Submit survey reply";
var QST_STRING_ID="questionString__";
var ANS_AREA_STRING_ID="answerAreaId__";
var ANSWER_STRING_ID="answerId__";
var SURVEY_ITEM_ID="surveyItemId__";

/**
*Class that reconstructs the payload parameter into a construct that *is easy to call when displaying *the survey to the *subscriber
*/
function SurveyParams(){
		var parsedPay=JSON.parse($("#payLoad").val());
		this.channelId=parsedPay[0];
		this.channelName=parsedPay[1];
		this.channelDescription=parsedPay[2];
		this.loopId=parsedPay[3];
		var loopItems=JSON.parse(parsedPay[4]);
		this.message=loopItems[0].message;
		var questAndAns=loopItems[1];
		this.questions=[];
		this.answers=[];
		for(var i=0;i<questAndAns.length;i++){
			this.questions.push(questAndAns[i].question);
			this.answers.push(questAndAns[i].answers);
		}
/**
*Adds the users replies to the class instance
*/
	this.addReplies=function(rep){
		this.replies=rep;
	}
}
/**This returns a div that contains questions, answers and buttons 	for one item in the survey
 *@param{string} numId - all divcol elements and its children get a *specific numeric postfix to *uniquely identify them in the *document. 
 */
function getDivCol(numId){
	var divCol = document.createElement("div");
	divCol.className="col-md-4 surveyinput surveyitem";
	divCol.id=SURVEY_ITEM_ID+numId;
	return divCol;
}
/**
*Extracts the numeric id of the page element based on the position of the escape characters "__"
*/
function extractNumericId(idString, pageElement){
	return pageElement.id.substring(idString.indexOf("__")+2);
}
/**
*Creates an element containing the question for the div identified by the numId and returns it
*/
function getQstArea(numId, question){
	var questionPar=document.createElement("h4");
	questionPar.innerHTML=question;
	questionPar.id=QST_STRING_ID+numId;
	questionPar.className="questiondiv bottom_aligner";
	return questionPar;
}
/**
*Creates answer buttons for the question and div identified by numDiv and returns a div containing *those buttons
*/
function getAnswerButtons(numId, answers){
	var ansDiv=document.createElement("div");
	ansDiv.id=ANS_AREA_STRING_ID+numId;
	ansDiv.className="btn-toolbar";
	ansDiv.setAttribute("data-toggle","buttons");
	for(var i=0;i<answers.length;i++){
	var ansLabel=document.createElement("label");
		ansDiv.append(ansLabel);
		ansLabel.className="btn btn-primary answerbutton";
		ansLabel.innerHTML=answers[i];
		var ansInput=document.createElement("input");
		ansLabel.append(ansInput);
		ansInput.type=("radio");
		ansInput.name="options";
		ansInput.id="answer__"+i;
		ansInput.autocomplete="off";
	}
	console.log(ansDiv);
	return ansDiv;
}

/**
*This function sets up the survey buttons and question headers
*/
function showQuestions(){
	var params=new SurveyParams();
	var div = $("#rowId").get(0);
	console.log(div);
	for(var i=0;i<params.questions.length;i++){
		var divCol=getDivCol(i);
		console.log(divCol);
		console.log('here')
		console.log(params.questions[i]);
		console.log(extractNumericId(SURVEY_ITEM_ID, divCol));
		console.log(divCol);
		div.appendChild(divCol);
		divCol.appendChild(getQstArea(i,params.questions[i]));
		divCol.appendChild(getAnswerButtons(i,params.answers[i]));
		console.log(div);
	}
}
/**
*Shows the jumbotron parameters
*/
function showHeaderItems(){
	var params=new SurveyParams();
	$("#headLine").html(params.channelName);
	$("#messageParagraph").html(params.message);

}
/**
*Checks if the radiobutton element has been activated
*/
function isActive(element, cls) {
	console.log(element);
	return (element.className).includes(cls);
}
/**
*Sends the reply to the server, putting the replies in the instance params of SurveyParams and *converting it to a JSON string for *transport to the server
*/
function submitReply(){
	var params=new SurveyParams();
	var isChecked=[];
	var hasAnswered=false;
	for(var i=0;i<params.answers.length;i++){
		var ans = $('#'+ANS_AREA_STRING_ID+i).get(0);
		var labChildren=ans.childNodes;
		console.log(ans);
		console.log(labChildren);
		var isChecked2=[];
		for(var j=0;j<labChildren.length;j++){
		// for(var labChild of labChildren){
			console.log(labChildren[j])
			if(isActive(labChildren[j],"btn btn-primary answerbutton active")){
				isChecked2.push(true);
				hasAnswered=true;
			}
			else{
				isChecked2.push(false)
			}
		}
		if(!hasAnswered){
			toast("#toast", "Please respond to all the questions before pressing submit");
			return;
		}
		hasAnswered=false
		isChecked.push(isChecked2);
	}
	params.addReplies(isChecked);
	console.log(params);
	console.log(params.stringify);
	$("#action").val(ACTION_SUBMIT_REPLY);
	$("#payLoad").val(JSON.stringify(params));
	/* console.log($("#flaskForm").get(0)); */
	$("#flaskForm").submit();
	console.log(isChecked);
}