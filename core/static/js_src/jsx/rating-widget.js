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

function factory(React, ReactDOM, aja){
    var RatingWidget = React.createClass({
        getInitialState: function(){
          return {
              total: this.props.total,
              positive: this.props.positive,
              negative: this.props.negative
          }
        },
        componentDidMount: function(){
            var _this = this;
            aja().url(this.props.vote_url).method('GET').type('json')
                .on('success', function(res){
                    _this.setState(res)
                }).go()
        },
        vote: function(is_positive, event){
            if(!!event)
                event.preventDefault();
            if(is_positive)
                this.setState({
                    positive: this.state.positive + 1,
                    negative: (this.state.negative ? this.state.negative - 1 : 0)
                });
            else
                this.setState({
                    positive: (this.state.positive ? this.state.positive - 1 : 0),
                    negative: this.state.negative + 1
                });
            var _this = this;
            aja().url(this.props.vote_url).method('POST').type('json')
                .data({
                    is_positive: is_positive ? 1 : 0,
                    csrfmiddlewaretoken: this.props.csrf_token
                }).on('success', function(res){
                    _this.setState(res)
                }).go()
        },
        render: function(){
            return (
                <div className="widget-rating ">
                    <div className="rating-negative">
                        <a href="#" className="rating-btn" onClick={this.vote.bind(this, false)}>
                            <i className="fa fa-times"/>
                        </a>
                        not trusted <br/> {this.state.negative}
                    </div>
                    <div className="rating-positive">
                        <a href="#" className="rating-btn " onClick={this.vote.bind(this, true)}>
                            <i className="fa fa-check"/>
                        </a>
                         trusted by
                        <br/> {this.state.positive}
                    </div>
                    <div className={this.props.is_authenticated ? 'hidden' : ''}>
                        <h5>You have to authorize in order to vote</h5>
                        <div className="btn-group" role="group">
                          <a className="btn btn-default" href={this.props.social_urls.fb} >
                              <i className="fa fa-facebook fa-fw"/>
                          </a>
                          <a className="btn btn-default" href={this.props.social_urls.vk} >
                              <i className="fa fa-vk fa-fw" />
                          </a>
                          <a className="btn btn-default" href={this.props.social_urls.gp}>
                              <i className="fa fa-google-plus fa-fw"/>
                          </a>
                          <a className="btn btn-default disabled" href={this.props.social_urls.ln}>
                              <i className="fa fa-linkedin fa-fw"/>
                          </a>
                        </div>
                    </div>
                </div>
            )
        }
    });

    function constructor(elem, options){
        var defaults = {
          retrieve_url: '#',
          vote_url: '#',
          total: 0,
          positive: 0,
          negative: 0,
          is_authenticated: 0,
          csrf_token: false
        };
        var opts = extend(defaults, options);
        return ReactDOM.render(<RatingWidget {...opts} />, elem);
    }
    return constructor;
}


if ( typeof define === 'function' && define.amd ) {
  // AMD
  define( [
      'react',
      'react-dom',
      'aja'
    ], factory );

}
else {
  // browser global
    window.RatingWidget = factory(
    window.React,
    window.ReactDOM,
    window.aja
  );
}
})(window);
