BOOL_TYPE='boolean question';
	
// function testPlotly(){
	// TESTER = document.getElementById('tester');
	// Plotly.plot( TESTER, [{
	// x: [1, 2, 3, 4, 5],
	// y: [1, 2, 4, 8, 16] }], {
	// margin: { t: 0 } } );
// }

class Question{
	constructor(question, answers){
		this.question=question;
		this.answers=answers;
	}
	/**Creates an array with all replies to the *specific question for all users who have replied. allReplies is an array of arrays of boolean arrays. Each item of the outer array is the complete reply of one user. Each item of the secondary array is the users answers to one question. Each item of the inner array indicates whether the user ticked off the answer or not
	The qIndex parameter indicates which of the questions we want the answer to
	*/
	setReplies(allReplies, qIndex){
		console.log(allReplies)
		this.replies=[]
		for(var reply of allReplies){
			console.log(reply)
			console.log(reply[qIndex]);
			this.replies.push(reply[qIndex]);
		}
	}
	/**Count how often each alternative was answered with true*/
	setCountBool(){
		this.count=new Array(this.answers.length).fill(0);
		for(var reply of this.replies){
			for(var i=0; i<reply.length;i++){
				if(reply[i]==true){
					this.count[i]++;
				}
			}
		}
	}
}
class ReplyParams{
	constructor(){
		var payLoad=$('#payLoad').get(0)
		console.log(payLoad)
		if(payLoad.value=="no data"){
			toast($('#toast'),'It looks like there are no replies so far')
			return;
		}
		console.log($("#payLoad").val())
		var parsedPay=JSON.parse($("#payLoad").val());
		console.log(parsedPay);
		var surveys=JSON.parse(parsedPay[0])
		var replyStringList=parsedPay[1]
		this.message=surveys[0].message
		this.questions=[];
		this.answers=[];
		this.replies=[];
		for(var survey of surveys[1]){
			this.questions.push(survey.question);
			this.answers.push(survey.answers);
		}
		for(var repString of replyStringList){
			this.replies.push(JSON.parse(repString));
		}
		console.log(this.message);
		console.log(this.questions);
		console.log(this.answers);
		console.log(this.replies);
		if(this.replies.length==0){
			toast('#toast', "Looks like nobody replied yet");
		}
	}
	addReplies(rep){
		this.replies=rep;
	}
}
var t0 = performance.now();
var params= new ReplyParams();
var t1 = performance.now();
console.log("params instance created in " + (t1 - t0) + " milliseconds.")
class PieSlice{
	constructor(answer, count){
		this.label=answer;
		this.value=count;
	}
}
/**Expects an instance of the question class and the numericindex of the col-div the plot should go in*/
function showPlot(qInst, plotIndex){
	this.pieData=[]
	for(var i=0;i<qInst.answers.length;i++){
		this.pieData.push(new PieSlice(qInst.answers[i],qInst.count[i]));
	}
	console.log(this.pieData);
		
	var pie = new d3pie(plotIndex+"_plotDiv", {
		"header": {
			"title": {
				"text": qInst.question,
				"fontSize": 14,
				"font": "verdana"
			}
		},
		"size": {
			"canvasHeight": 400,
			"canvasWidth": 590,
			"pieOuterRadius": "88%"
		},
		"data": {
			"content": this.pieData
		},
		"labels": {
			"outer": {
				"pieDistance": 32
			},
			"inner": {
				"format": "value"
			},
			"mainLabel": {
				"font": "verdana",
				"fontSize": 12
			},
			"percentage": {
				"color": "#e1e1e1",
				"font": "verdana",
				"decimalPlaces": 0
			},
			"value": {
				"color": "#e1e1e1",
				"font": "verdana",				
			},
			"lines": {
				"enabled": true,
				"color": "#cccccc"
			},
			"truncation": {
				"enabled": true
			}
		},
		"effects": {
			"pullOutSegmentOnClick": {
				"effect": "linear",
				"speed": 400,
				"size": 8
			}
		}
	});
}
function makePlots(){
	this.questions=[]
	for(var i=0;i<params.questions.length;i++){
		console.log(params)
		question=new Question(params.questions[i], params.answers[i])
		question.setReplies(params.replies,i);
		question.setCountBool();
		console.log(this.question);
		this.questions.push(question)
		showPlot(question,i);
	}
}
makePlots();