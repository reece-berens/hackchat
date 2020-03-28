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
			height: '10%',
			border: '3px',
			borderColor: 'white',
			borderStyle: 'solid',
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
			})
		},
		showAllChannels: function() {
			return this.channelList;
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
		chatVue.addMessage(messageData);
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
