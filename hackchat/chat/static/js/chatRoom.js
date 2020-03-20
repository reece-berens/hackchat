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
		addMessage: function() {
			console.log("Add a message here");
		}
	}
});

var messageTypeVue = new Vue({
	delimiters: vueDelimiters,
	el: '#chatTypeWindow',
	data: {
		message: '',
		divStyleObject: {
			height: '10%',
			border: '3px',
			borderColor: 'white',
			borderStyle: 'solid',
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
			messageType
			firstName
			lastName
			contents
			email
			time
			fromOrg
	*/
	//TODO add some error checking here to ensure that the incoming
	//message data has all of the attributes it should
	console.log(messageData['messageType']);
	if (messageData['messageType'] == 'chatMessage')
	{
		chatVue.messages.push(messageData);
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
	var toSendDict = {};
	toSendDict['message'] = messageText;
	toSendDict['authorEmail'] = myEmail;
	toSendDict['roomName'] = roomName;
	console.log(toSendDict);

	chatSocket.send(JSON.stringify(toSendDict));
}

