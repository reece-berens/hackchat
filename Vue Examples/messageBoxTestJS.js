var userIsOrganizer = false;

var app = new Vue({
	el: '#app',
	data: {
		messageText: '',
		messages: [
			{text: 'MSG 1', author: "You", isOrg: false},
			{text: 'Message 2', author: "Bill The Organizer", isOrg: true},
		],
		orgStyleObject: {
			fontSize: '16pt',
			color: 'blue'
		},
		normalStyleObject: {
			fontSize: '14pt',
			color: 'black'
		}
	},
	methods: {
		addMessage: function() {
			var newMessage = this.msgText.trim();
			if (!newMessage) {return;}
			this.messages.push(
				{text: newMessage, author: "You", isOrg: userIsOrganizer}
			);
			this.msgText = '';
		}
	}
});

$("#outsideBtn").click(function () {
	console.log("ON CLICK");
	app.messages.push(
		{text: "Other User Text", author: "Other User", isOrg: false}
	);
});

