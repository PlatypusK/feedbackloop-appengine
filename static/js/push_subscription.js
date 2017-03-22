ACTION_SAVE_ONE_SIGNAL='save one signal uid'


function saveOneSignalUidOnServer(oneSigUid){
	var oldAct=$('#action').val()
	$('#action').val(ACTION_SAVE_ONE_SIGNAL)
	var oldPayload=$('#payLoad').val()
	$('#payLoad').val(oneSigUid)
    $.ajax({
        url:'/save_one_signal',
        type:'post',
        data:$('#flaskForm').serialize(),
        success:function(){
            //whatever you wanna do after the form is successfully submitted
        }
    });
	$('#action').val(oldAct)
	$('#payLoad').val(oldPayload)
}
function onGetOneSigUid(uId){
	console.log(uId)
	saveOneSignalUidOnServer(uId);
}
function onNotGetOneSigUid(reason){
	console.log(reason)
}
OneSignal.push(function() {
  // Occurs when the user's subscription changes to a new value.
  OneSignal.on('subscriptionChange', function (isSubscribed) {
	console.log("The user's subscription state is now:", isSubscribed);
	if(isSubscribed){
		OneSignal.getUserId(onGetOneSigUid, onNotGetOneSigUid)
	}
  });
});
// OneSignal.push(function(){OneSignal.getUserId(onGetOneSigUid, onNotGetOneSigUid)});
