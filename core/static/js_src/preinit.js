
import Dropdown from 'plugins/dropdown'

module.exports = () => {
    new Dropdown();
    var lang_radios = document.getElementsByClassName('language-radio');

    Array.prototype.forEach.call(lang_radios, function(radio){
        radio.addEventListener('change', function(event){
            var name = this.getAttribute('name'),
                value = this.getAttribute('value');
            if(name == 'language')
            {
                window.location.href = value;
            }
            console.log(this.getAttribute('name'), this.getAttribute('value'))
        })
    });

    function fabric() {
        var connection = null;

        function SocketConnection(options) {
            this.options = options;
            this.connection = connection || new WebSocket(options.url);
            this._initEventListeners();
        }

        SocketConnection.prototype._initEventListeners = function(){
            this.connection.onopen = this.options.onOpen.bind(this);
            this.connection.onmessage = this.options.onMessage.bind(this);
            this.connection.onclose = this.options.onClose.bind(this);
        };

        return SocketConnection;
    }

    var SocketConnection = fabric();
    var connection = new SocketConnection({
        url: "ws://localhost:8081/websocket",
        onOpen: function(){
            console.log("Connection opened")
        },
        onClose: function(){
            console.log("Connection closed")
        },
        onMessage: function(message){
            console.log("Received a message", message)
        }
    });

}
