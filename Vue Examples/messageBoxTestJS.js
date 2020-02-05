var app = new Vue({
	el: '#app',
	data: {
		todoText: '',
		todos: [
			{text: 'Vue.js', done: true},
			{text: 'Vue.js', done: false},
		]
	},
	methods: {
		addTodo: function() {
			var newTodo = this.todoText.trim();
			if (!newTodo) {return;}
			this.todos.push(
				{text: newTodo}
			);
			this.todoText = '';
		}
	}
});

