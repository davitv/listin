(function(window){
    // vars
    var document = window.document;

    // -------------------------- helpers -------------------------- //

    // extend objects
    function extend( a, b ) {
      for ( var prop in b ) {
        a[ prop ] = b[ prop ];
      }
      return a;
    }
    function noop(){};

     function sendForm(form, callback) {
        var formData = new FormData(form);
        var xhr = new XMLHttpRequest();
        xhr.open("POST", form.getAttribute("action"));
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        xhr.onreadystatechange = function() { // (3)
          if (xhr.readyState != 4) return;
          callback && callback(JSON.parse(xhr.responseText))
        };
        xhr.send(formData);
     }
    
function factory(React, ReactDOM, aja,  moment){
    var Message = React.createClass({
        render: function(){
            return (
                <div className={"comment " + (this.props.current_user == this.props.sender.id ? "comment-right" : '')} >
                    <div className="comment-userpic">
                        <img src={this.props.sender.userpic.thumbnail} alt="" className="img-responsive" />
                    </div>
                    <div className="comment-text">
                        <span className="arrow"/>
                        <div className="author">
                            <a href="#" className="author">{this.props.sender.first_name} {this.props.sender.last_name} </a>
                            <small className="datetime" ><i className="fa fa-clock-o" /><span>
                                12 часов назад</span></small>
                        </div>
                        <p className="comment-p" >
                            {this.props.text}
                        </p>
                    </div>
                </div>
            )
        }
    });

    var MessagingWrapper = React.createClass({
        getInitialState: function(){
            return {
                usersList: [],
                results:  [], // actual results, list of returned objects
                recipient:  null, // actual results, list of returned objects
                currentRoom:  {
                    name: "Organization Room",
                    pk: 0
                }, // actual results, list of returned objects
                count: 0, // total count
                next: false, // link to next results page
                previous: false, // link to previous results page
                locked: false // prevent loading if request already sent
            }
        },
        componentDidMount: function(){
            this.loadUsers();
            this.loadComments();
        },
        onCommentSent: function(){
           this.loadComments(function(){
               var comments_wrapper = ReactDOM.findDOMNode(this.refs.comments_wrapper);
               comments_wrapper.scrollTop = comments_wrapper.scrollHeight;
           });
        },
        loadComments: function(callback){
            var _this = this;
            callback = callback || noop;
            aja().url(this.props.url)
                .on('success', function(response){
                      _this.setState({
                            // in order to allow infite scroll results uppend
                            results: response.results, // _this.state.results.concat(),
                            count: response.count,
                            next: response.next,
                            previous: response.previous
                      }, callback);
                 }).go();
        },
        loadUsers: function(callback){
            var _this = this;
            callback = callback || noop;

            aja().url(this.props.users_url).header("Accept", '*/*')
                 .on('success', function(response){
                      _this.setState({
                            usersList: response.results
                      }, callback);
                 }).go();
        },
        onPost: function(event){
            var _this = this;
            event.preventDefault();
            sendForm(ReactDOM.findDOMNode(this.refs.postForm), function(){
                _this.loadComments();
            })
        },
        onRecipientChange: function(user, event){
            var _this = this;
            event.preventDefault();
            this.setState({
                recipient: user
            })
        },
        render: function(){
            var users = [];
            var _this = this;
            var room_name = this.state.recipient ? this.state.recipient.first_name + ' ' + this.state.recipient.last_name : "Organization Room";
            this.state.usersList.forEach(function(user){
                users.push(
                    <li key={user.id}>
                        <a href="#" onClick={_this.onRecipientChange.bind(_this, user)}>
                            <img src={user.userpic.thumbnail} alt={user.first_name + ' ' + user.last_name} className="userpic" />
                            <div className="user-name">{user.first_name + ' ' + user.last_name}</div>
                            <div className="user-position">{user.position}</div>
                        </a>
                    </li>
                );
            });
            if(!users.length)
                users = (<div className="alert alert-info">No staff for this organization</div>);
            
            var messages = [];
            this.state.results.forEach(function(message){
               messages.push(<Message {...message} key={message.id} current_user={_this.props.current_user} />)
            });
            
            return (
              <div className="widget widget-messaging">

                    <div className="widget-headline">
                        <h4 className="pull-left">
                           <i className="fa fa-comment-o" /> Messaging </h4>
                            <div className="dropdown dropdown-button pull-right">
                                <a className="dropdown-link btn btn-default" href="#">
                                    {room_name}
                                    <i className="fa fa-angle-down fa-fw"/>
                                </a>
                                <div className="dropdown-content users-dropdown">
                                  <ul className="list-unstyled">
                                     {users}
                                  </ul>
                                </div>
                            </div>
                    </div>

                    <div className="widget-content">
                            {messages}
                    </div>

                    <div className="widget-footer">
                        <form action={this.props.post_url} onSubmit={this.onPost} method="POST" ref="postForm">
                            <div className="chat-form">
                                <div className="input-cont">
                                    <input className="form-control" type="text" name="text" placeholder="fdfs" />
                                </div>
                                <input type="hidden" name="csrfmiddlewaretoken" value={this.props.csrf_token} />
                                <input type="hidden" name="to_users" value={this.state.recipient ? this.state.recipient.id : ''} />
                                <div className="btn-cont">
                                    <span className="arrow" />
                                    <button className="btn blue icn-only"><i className="fa fa-check icon-white"/></button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            )
      }
    });

    function constructor(elem, options){
        var defaults = {
          url: '#',
          users_url: '#',
          post_url: '#',
          data: {},
          options: false,
          connectedForm: false
        };
        var opts = extend(defaults, options);
        return ReactDOM.render(<MessagingWrapper {...opts} />, elem);
    }
    return constructor;
}


if ( typeof define === 'function' && define.amd ) {
  // AMD
  define( [
      'react',
      'react-dom',
      'aja/aja.min',
      'moment'
    ], factory );

}
else {
  // browser global
    window.MessagingWidget = factory(
    window.React,
    window.ReactDOM,
    window.aja,
    window.moment
  );
}
})(window);
