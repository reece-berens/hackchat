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