var ANS_STRING_ID="addAnswer_";
var QST_STRING_ID="question_";
var SUR_STRING_ID="surveyItem_";
var ANS_AREA_STRING_ID="answersArea_";
var ACTION_PUBLISH="publish";

function extractNumericAnsId(ans_id){
	return ans_id.substring(ans_id.indexOf("_")+1);
}
function addAnswer(clicked_id){
	var numId=extractNumericAnsId(clicked_id);
	var div = document.getElementById(ANS_AREA_STRING_ID+numId);
	var input = document.createElement("textarea");
	input.name = "post";
	input.className="answerbox"
	input.placeholder="Enter an answer option"
	input.maxLength = "5000";
	input.cols = "40";
	input.rows = "1";
	div.appendChild(input); //appendChild
}
/**This returns a new id that will be the last numerical id of the child divs of the supplied div if made into a new item*/
function getNumIdColLast(div){
	return (parseInt(extractNumericId(SUR_STRING_ID,div.lastElementChild))+1);
}
/**
*Extracts the numeric id of the page element based on the position of the escape characters "__"
*/
function extractNumericId(idString, pageElement){
	return pageElement.id.substring(idString.indexOf("_")+1);
}
/**This returns a div that contains questions, answers and buttons for one item in the surveya
 *@param{string} numId - all divcol elements and its children get a specific numeric postfix to uniquely identify them in the document. 
 */
function getDivCol(numId){
	var divCol = document.createElement("div");
	divCol.className="col-md-4 surveyinput";
	divCol.id=SUR_STRING_ID+numId
	return divCol
}
/**This returns the button that creates more answer fields
 *@param{string} numId - all divcol elements and its children get a specific numeric postfix to uniquely identify them in the document. 
 */
function getAnsButton(numId){
	var ansButton=document.createElement("button");
	ansButton.id=ANS_STRING_ID+numId;
	ansButton.className="addanswerbutton btn btn-secondary";
	ansButton.addEventListener("click", function(){addAnswer(ansButton.id)}); 	
	ansButton.innerHTML="&dArr; Add Answer &dArr;";
	return ansButton;
}
/**This returns a textarea where the user can input the question for the survey item
 *@param{string} numId - all divcol elements and its children get a specific numeric postfix to uniquely identify them in the document. 
 */
function getQstArea(numId){
	var question=document.createElement("textarea");
	question.className="questionbox";
	question.placeholder="Enter a question here";
	question.rows=3;
	question.id=QST_STRING_ID+numId;
	return question;
}
/**This returns a div where the user can input the question for the survey item
 *@param{string} numId - all divcol elements and its children get a specific numeric postfix to uniquely identify them in the document. 
 */
function getAnsDiv(numId){
	var ansDiv=document.createElement("div")
	ansDiv.id=ANS_AREA_STRING_ID+numId;
	return ansDiv;
}
function addQuestion(){
	var div = document.getElementById("rowId");
	var numId=getNumIdColLast(div);
	var divCol=getDivCol(numId);
	var ansButton=getAnsButton(numId)
	var numId=getNumIdColLast(div);
	var question=getQstArea(numId)
	var ansDiv=getAnsDiv(numId);
	div.appendChild(divCol);
	divCol.appendChild(question);
	divCol.appendChild(ansDiv);
	divCol.appendChild(ansButton);
}
function publish(){
	var loopObj=new Loop();
	var response=loopObj.toJson();
	console.log(loopObj.toJson());
	// flaskForm=document.getElementById("flaskForm");
	// jStringField=document.getElementById("jsonString");
	// jStringField.value=response;
	$('#jsonString').val(response);
	$('#action').val(ACTION_PUBLISH)
	// action=document.getElementById("action");
	// console.log(action);
	// action.value=ACTION_PUBLISH;
	// console.log(flaskForm);
	// flaskForm.submit();
	$('#flaskForm').submit();
}
function Loop(){
	this.message=$('#messageBox').val()
	var rowDiv=document.getElementById("rowId");
	var loopElementsCollection=rowDiv.children;
	var arr=Array.prototype.slice.call( loopElementsCollection );
	console.log(arr);
	this.loops=[];
	for (var i = 0; i < arr.length; i++) {
		console.log(arr[i]);
		var numId=extractNumericId(SUR_STRING_ID,arr[i]);
		this.loops.push(new LoopItem(numId));
	}

	this.toJson=function(){
		return JSON.stringify([new MessageItem(this.message),this.loops])
	}
}
function MessageItem(messageValue){
	this.message=messageValue;
}
function LoopItem(numId){
	this.question=getQuestion(numId)
	this.answers=getAnswers(numId)

}
function getQuestion(numId){
	console.log(numId);
	console.log(QST_STRING_ID+numId);
	return document.getElementById(QST_STRING_ID+numId).value;
}
function getAnswers(numId){
	var ansDiv=document.getElementById(ANS_AREA_STRING_ID+numId);
	console.log(ansDiv);
	var answerFieldsCollection=ansDiv.children;//get all answers for loopitem
	var arr = Array.prototype.slice.call( answerFieldsCollection );//convert to array
	var answers=[];
	for (var i = 0; i < arr.length; i++) {
		answers.push(arr[i].value);
	}
	return answers
}	

	


