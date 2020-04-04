var vueDelimiters = ['[[', ']]'];

var chatVue = new Vue({
	el: "#chatWindow",
	delimiters: vueDelimiters,
	data: {
		messages: initialMessages,
		selfEmail: myEmail,
		organizerStyleObject: {
			fontSize: '16pt',
			color: '#49fb35',
		},
		normalStyleObject: {
			fontSize: '14pt',
			color: 'white',
		},
		selfStyleObject: {
			backgroundColor: '#575757',
			//textAlign: 'right',
		},
		selfTimeStyleObject: {
			textAlign: 'right',
			color: '#fff',
			fontSize: '10pt',
		},
		normalTimeStyleObject: {
			textAlign: 'left',
			color: '#fff',
			fontSize: '10pt',
		},
		baseStyleObject: {
			border: '2px',
			borderStyle: 'solid',
			borderColor: '#4e4e4e',
			borderRadius: '5px',
			paddingTop: '5px',
			margin: '5px auto',
			width: '95%',
		},
		chatWindowStyleObject: {
			height: '90%',
			border: '3px',
			borderColor: 'white',
			borderStyle: 'solid',
			marginBottom: '5px',
		}
	},
	methods: {
		addMessage: function(e) {
			this.messages.push(e);
		}
	}
});

var messageTypeVue = new Vue({
	delimiters: vueDelimiters,
	el: '#chatTypeWindow',
	data: {
		message: '',
		divStyleObject: {
			//height: '10%',
			border: '3px',
			borderColor: 'white',
			borderStyle: 'solid',
		},
		textAreaStyleObject: {
			backgroundColor: '#575757',
			color: 'white',
			resize: 'none',
			marginTop: '2px',
			marginLeft: '2px'
		},
		buttonStyleObject: {
			//marginTop: '2px',
			paddingLeft: '5px',
		}
	},
	methods: {
		muteUser: function() {
			document.getElementById("chatMessageInput").readOnly = true;
			document.getElementById("chatMessageSend").disabled = true;
		},
		unMuteUser: function() {
			document.getElementById("chatMessageInput").readOnly = false;
			document.getElementById("chatMessageSend").disabled = false;
		}
	}
});

var channelVue = new Vue({
	delimiters: vueDelimiters,
	el: '#channelColumn',
	data: {
		channelList: initialChannelList,
		selfIsOrganizer: selfIsOrganizer,
	},
	methods: {
		addChannel: function(e) {
			this.channelList.push(e);
		},
		redirect: function(name) {
			//console.log("INSIDE REDIRECT VUE " + name);
			window.location.replace('http://' + window.location.host + '/chat/' + name);
		}
	},
	computed: {
		//https://forum.vuejs.org/t/how-to-best-work-with-v-for-and-computed-lists/49994
		showOnlyNonOrganizerChannels: function() {
			//console.log("Inside only non");
			return this.channelList.filter(c => {
				//console.log(c);
				if (c.organizerOnly == false)
				{
					return true;
				}
				else
				{
					return false;
				}
			});
		},
		showAllChannels: function() {
			return this.channelList;
		}
	}
});

var participantVue = new Vue({
	delimiters: vueDelimiters,
	el: "#participantColumn",
	data: {
		participantList: initialParticipantList,
		selfIsOrganizer: selfIsOrganizer,
	},
	methods: {
		addParticipant: function(e) {
			this.participantList.push(e);
		},
		findEmailFromID: function(id) {
			return this.participantList.find(p => p.id == id).email;
		},
		organizerMute: function(email) {
			//bring up a mute modal box asking how long to mute the user for
			console.log("INSIDE ORGANIZER MUTE");
			console.log(email[0][0]);
			muteModalVue.showMuteModal(email[0][0]);
		},
		getParticipantName: function(email) {
			participant = this.participantList.find(p => p.email == email);
			return participant.firstName + " " + participant.lastName;
		}
	},
	computed: {
		getOrganizerList: function() {
			return this.participantList.filter(p => {
				//console.log(p);
				if (p.isOrganizer == true)
				{
					return true;
				}
				else
				{
					return false;
				}
			});
		},
		getParticipantList: function() {
			return this.participantList.filter(p => {
				if (p.isOrganizer == false)
				{
					return true;
				}
				else
				{
					return false;
				}
			});
		}
	}
});

var muteModalVue = new Vue({
	delimiters: vueDelimiters,
	el: "#muteModal",
	data: {
		participantEmail: '',
		participantName: '',
	},
	methods: {
		showMuteModal: function(email) {
			console.log(email);
			this.participantEmail = email;
			this.participantName = participantVue.getParticipantName(email);
			console.log(this.participantName);
			$("#muteModal").modal();
		},
		muteParticipant: function() {
			console.log("Inside muteParticipant");
			muteMinutes = document.getElementById("muteTimeInput").value;
			console.log(muteMinutes);
			$("#muteModal").modal('hide');
			chatSocket.send(JSON.stringify({
				messageType: 'muteUser',
				requestingEmail: myEmail,
				mutingEmail: this.participantEmail,
				muteMinutes: parseInt(muteMinutes)
			}));
			console.log("Sent message to server");
		}
	}
});

var chatSocket = new WebSocket('ws://' + window.location.host + 
	'/ws/chat/' + roomName + '/');

chatSocket.onmessage = function(e) {
	console.log("GOT MESSAGE FROM SERVER");
	var messageData = JSON.parse(e.data);
	/*
		messageData object has the following attributes:
			messageType - all have this
			messageType == 'chatMessage'
				firstName
				lastName
				contents
				email
				time
				fromOrg
			messageType == 'newChannel'
				channelName
				organizerOnly
			messageType == 'newParticipant'
				firstName
				lastName
				isOrganizer
	*/
	//TODO add some error checking here to ensure that the incoming
	//message data has all of the attributes it should
	console.log(messageData['messageType']);
	console.log(messageData);
	if (messageData['messageType'] == 'chatMessage')
	{
		if (messageData['contents'].includes('@' + myName) || messageData['contents'].includes('@everyone'))
		{
			playNotificationSound();
		}
		chatVue.addMessage(messageData);
	}
	else if (messageData['messageType'] == 'userMuted')
	{
		if (messageData['email'] == myEmail)
		{
			messageTypeVue.muteUser();
			if (parseInt(messageData['muteMinutes']) == -1)
			{
				alert("ALERT: You have been muted permanently.");
			}
			else
			{
				alert("ALERT: You have been muted for " + messageData['muteMinutes'] + " minutes.");
			}
		}
	}
	else if (messageData['messageType'] == 'userUnmuted')
	{
		if (messageData['email'] == myEmail)
		{
			messageTypeVue.unMuteUser();
			alert("ALERT: You have been un-muted.");
		}
	}
};

chatSocket.onclose = function(e) {
	console.error('Chat socket has closed unexpectedly');
};

$('#chatMessageInput').keyup(function(e) {
	if (e.which == 13)
	{
		//Enter key has been pressed, send the message
		sendMessage();
		$('#chatMessageInput')[0].value = '';
	}
});

$('#chatMessageSend').click(function(e) {
	sendMessage();
	$('#chatMessageInput')[0].value = '';
});

function sendMessage() {
	var messageText = $("#chatMessageInput")[0].value;
	console.log(messageText);
	var toSendDict = {'messageType': 'message'};
	toSendDict['message'] = messageText;
	toSendDict['authorEmail'] = myEmail;
	toSendDict['roomName'] = roomName;
	console.log(toSendDict);

	chatSocket.send(JSON.stringify(toSendDict));
}

function sendMute(id, muteTime) {
	//id is id of user to mute, muteTime is number of minutes (-1 = permanent)
	var toSendDict = {'messageType': 'muteUser'};
	emailOfMuteUser = participantVue.findEmailFromID(id);
	console.log("Muting user " + emailOfMuteUser);
	toSendDict['mutingEmail'] = emailOfMuteUser;
	toSendDict['muteMinutes'] = muteTime;
	toSendDict['requestingEmail'] = myEmail;

	chatSocket.send(JSON.stringify(toSendDict));
}

//https://stackoverflow.com/questions/9419263/playing-audio-with-javascript/18628124#18628124
function playNotificationSound() {
	audioNotification.play();
}

if (startMuted == true)
{
	messageTypeVue.muteUser();
}