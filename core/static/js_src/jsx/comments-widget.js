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

function factory(React, ReactDOM, aja,  moment){

    var Comment = React.createClass({
        render: function(){
          return (
              <div className="comment">
                    <div className="comment-userpic">
                        <img src={this.props.user.userpic.thumbnail} alt="" className="img-responsive" />
                    </div>
                    <div className="comment-text">
                        <span className="arrow" />
                        <div className="author"><a href="#" className="author">
                            {this.props.user.first_name + ' ' + this.props.user.last_name}
                        </a> <small className="datetime">
                            <i className="fa fa-clock-o" /> {moment(this.props.created_at).fromNow()}</small>
                        </div>
                        <p className="comment-p"> {this.props.text} </p>
                    </div>
              </div>
          )
        }
    });
    
    var CommentsForm = React.createClass({
        send: function(callback){
            var _this = this;
            var formData = new FormData(ReactDOM.findDOMNode(this));
            var xhr = new XMLHttpRequest();
            xhr.open("POST", this.props.url);
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
            xhr.onreadystatechange = function() { // (3)
              if (xhr.readyState != 4) return;
              if (xhr.status != 201) {
                  console.error(JSON.parse(xhr.responseText));
              } else {
                  callback && callback(JSON.parse(xhr.responseText));
                  _this.clear();
              }
            };
            xhr.send(formData);

        },
        onSubmit: function(event) {
            event.preventDefault();
            this.send(this.props.onSend);
        },
        clear: function() {
            var textarea = ReactDOM.findDOMNode(this.refs.input_text);
            textarea.value = '';
        },
        render: function(){

          return (
              <form action={this.props.url} method="POST" onSubmit={this.onSubmit}>
                    <div className="form-group">
                        <textarea id="" cols="30" rows="5" name="text" className="form-control" ref="input_text"/>
                    </div>
                    <div className="form-group">
                        <input type="hidden" name="csrfmiddlewaretoken" value={this.props.csrf_token} />
                        <input type="hidden" name="organization" value={this.props.organization} />
                        <button className="btn-primary btn">Submit</button>
                    </div>
              </form>
          )
      }
    });

    var CommentsWrapper = React.createClass({
        getInitialState: function(){
            return {
                results:  [], // actual results, list of returned objects
                users:  [], // actual results, list of returned objects
                count: 0, // total count
                next: false, // link to next results page
                previous: false, // link to previous results page
                locked: false // prevent loading if request already sent
            }
        },
        componentDidMount: function(){
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

            aja().url(this.props.url).data({
                organization: this.props.organization_id
            }).on('success', function(response) {
                _this.setState({
                    // in order to allow infite scroll results uppend
                    results: response.results, // _this.state.results.concat(),
                    count: response.count,
                    next: response.next,
                    previous: response.previous
                }, callback);
            }).go();
        },
        render: function(){
            var comments = [];

            for(var i = 0, l = this.state.results.length; i < l; i++)
            {
                comments.push(<Comment key={this.state.results[i].id} {...this.state.results[i]} />)
            }
            if(!l)
            {
                comments = <div className="alert alert-info"><strong>There are no comments yet!</strong></div>
            }

            var commentForm = null;
            if(this.props.is_authed)
            {
                commentForm = <CommentsForm
                        url={this.props.url}
                        csrf_token={this.props.csrf_token}
                        organization={this.props.organization_id}
                        onSend={this.onCommentSent}
                    />
            }
            else
            {
                commentForm = [
                    <div>
                        <h5>You have to log in for leaving a comment</h5>
                        <div className="btn-group" role="group">
                          <a className="btn btn-default" href={this.props.social_urls.fb}>
                              <i className="fa fa-facebook fa-fw"/>
                          </a>
                          <a className="btn btn-default" href={this.props.social_urls.vk}>
                              <i className="fa fa-vk fa-fw"/>
                          </a>
                          <a className="btn btn-default disabled" href="#">
                              <i className="fa fa-linkedin fa-fw"/>
                          </a>
                          <a className="btn btn-default" href={this.props.social_urls.gp}>
                              <i className="fa fa-google-plus fa-fw"/>
                          </a>
                        </div>
                    </div>
                ]
            }
            return (
              <div className="widget widget-comments">

                  <div className="widget-content" ref="comments_wrapper">
                      {comments}
                  </div>
                  <div className="widget-footer">
                      {commentForm}
                  </div>
              </div>
            )
      }
    });

    function constructor(elem, options){
        var defaults = {
          url: '#',
          users_url: '#',
          data: {},
          organization_id: null,
          options: false,
          connectedForm: false
        };
        var opts = extend(defaults, options);
        return ReactDOM.render(<CommentsWrapper {...opts} />, elem);
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
    window.CommentsWidget = factory(
    window.React,
    window.ReactDOM,
    window.aja,
    window.moment
  );
}
})(window);
