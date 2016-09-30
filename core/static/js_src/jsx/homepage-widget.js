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
    function noop(){}

function factory(React, ReactDOM, aja, StoreWrapper, Simodal){
    var MessageModal = React.createClass({
        getInitialState: function(){
          return {
              send_to: 0,
              sender_name: '',
              email: '',
              phone: '',
              text: '',
              errors: {
                  text: '',
                  email: '',
                  phone: '',
                  name: ''
              }
          }
        },
        componentDidMount: function(){
            var _this = this;
            this.validators = {
                sender_name: function(value){
                    var err = '';
                    if(!value.trim().length)
                    {
                        err = 'Please, fill your name';
                    }
                    this.setState({
                        sender_name: value,
                        sender_name_error: err
                    });
                }.bind(_this),
                email: function(value){
                    var err = '';
                    if(!value.trim().length)
                    {
                        err = 'Email should be set';
                    }
                    this.setState({
                        email: value,
                        email_error: err
                    });
                }.bind(_this),
                phone: function(value){
                    this.setState({
                        phone: value
                    });

                }.bind(_this),
                text: function(value){
                    var err = '';
                    if(!value.trim().length)
                    {
                        err = 'Text should not be empty';
                    }
                    this.setState({
                        text: value,
                        text_error: err
                    });
                }.bind(_this)
            }
        },
        onInputChange: function(input_name, event)
        {
            this.validators[input_name](event.target.value);
        },
        is_valid: function(err_dict){
            err_dict = err_dict || {};

            var update_state = {

            };
            var valid = true;

            ['sender_name', 'phone', 'email', 'text'].forEach(function(name){
                if(!this.state[name].trim().length)
                {
                    valid = false;
                    update_state[name + '_error'] = 'This field is required';
                }
                if(err_dict[name] !== undefined)
                {

                    valid = false;
                    update_state[name + '_error'] = err_dict[name][0];
                }
            }, this);
            this.setState(update_state);
            return valid;
        },
        submitForm: function(event)
        {
            event.preventDefault();
            if(this.is_valid())
            {
                aja().url(this.props.submit_url)
                    .method("POST")
                    .header("X-CSRFToken", this.props.csrf)
                    .type("json")
                    .data({
                        sender_name: this.state.sender_name,
                        email: this.state.email,
                        phone: this.state.phone,
                        text: this.state.text
                }).on('400',
                    function(res){
                        this.is_valid(JSON.parse(res));
                    }.bind(this)
                ).on('201',
                    function(res){
                        this.setState(
                            {form_sent: true}
                        )
                    }.bind(this)
                ).go()
            }
        },
        render: function(){
            return (
                <div className="message-modal">
                    <div className="headline">
                        <h4>Write a message to company
                            <a href="#" className=" simodal-close pull-right"><i className="fa fa-times"/></a>
                        </h4>
                    </div>
                    <form className="" action={this.props.submit_url} method="POST" onSubmit={this.submitForm}>
                        <div className={"inputs-wrapper " + (this.state.form_sent ? 'hidden' : '')}>
                           <div className="form-group">
                                <label htmlFor="input-message-name" className="control-label">Message type</label>
                                <select name="send_to" id="" className="form-control">
                                    <option value="0">Message</option>
                                    <option value="1">Email</option>
                                </select>
                            </div>
                            <div className={"form-group " + (this.state.sender_name_error ? "has-error" : "")}>
                                <label htmlFor="input-message-name" className="control-label">Your name</label>
                                <input type="text" onChange={this.onInputChange.bind(this, 'sender_name')}
                                       value={this.state.sender_name} name="sender_name" className="form-control" id="input-message-name"/>
                            </div>
                            <div className="row">
                                <div className="col-sm-6">
                                    <div className={"form-group " + (this.state.email_error ? "has-error" : "")}>
                                        <label htmlFor="input-message-email" className="control-label">Email</label>
                                        <input type="text" name="email" value={this.state.email}
                                               onChange={this.onInputChange.bind(this, 'email')}
                                               className="form-control" id="input-message-email"/>
                                    </div></div>
                                <div className="col-sm-6">
                                    <div className={"form-group " + (this.state.phone_error ? "has-error" : "")}>
                                        <label htmlFor="input-message-phone" className="control-label">Phone</label>
                                        <input type="text" value={this.state.phone}
                                               onChange={this.onInputChange.bind(this, 'phone')} name="phone" className="form-control" id="input-message-phone"/>
                                        <p>{this.state.phone_error}</p>
                                    </div>
                                </div>
                            </div>
                            <div className={"form-group " + (this.state.text_error ? "has-error" : "")}>
                                <label htmlFor="input-message-text" className="control-label">Message text</label>
                                <textarea onChange={this.onInputChange.bind(this, 'text')}
                                       value={this.state.text}  name="text" id="input-message-text" cols="30" rows="3" className="form-control"/>
                            </div>
                        </div>


                        <div className="form-group">
                            <input type="hidden" name="csrfmiddlewaretoken" value={this.props.csrf} />
                            <div className={"alert alert-info " + (this.state.form_sent ? '' : 'hidden')}>Thanks! Your message was sent!</div>
                            <button className={this.state.form_sent ? 'hidden' : 'btn btn-primary'}>
                                <i className="fa fa-check"/>Submit</button>
                            <a className={this.state.form_sent ? 'btn btn-primary simodal-close hidden' : 'hidden'}>
                                <i className="fa fa-check"/>
                                {(this.state.form_sent ? 'Close window' : 'Send message')}</a>

                        </div>
                    </form>

                </div>
            )
        }
    });

    var Organization = React.createClass({
        toggleFavorites: function(event){
            event.preventDefault();
            var pk = this.props.id;
            var favorites = StoreWrapper.get('favorites');
              if(!this.props.is_favorite)
              {
                    if(!favorites)
                    {
                        favorites = [pk];
                    }
                    else
                    {
                        if(favorites.indexOf(pk) == -1)
                        {
                            favorites.push(pk)
                        }
                    }
                    StoreWrapper.set('favorites', favorites);
                    new Simodal({
                        content: 'Фирма '+this.props.name+' в закладки!',
                        // can be set to: bottom left, bottom right, top left, top right
                        overlayClass: 'notifications-overlay bottom right',
                        modalClass: 'simodal',
                        modalOnShowClass: 'animated bounceIn',
                        keyboard: false,
                        closeOnClick: true,
                        kind: 'notification',
                        removeOnHide: true
                    });
              }
              else
              {

                if(!favorites)
                 return;

                var i = favorites.indexOf(pk);
                if(i != -1)
                {
                    favorites.splice(i, 1);
                    StoreWrapper.set('favorites', favorites);
                    new Simodal({
                        content: 'Фирма '+this.props.name+' удалена из закладок!',
                        // can be set to: bottom left, bottom right, top left, top right
                        overlayClass: 'notifications-overlay bottom right',
                        modalClass: 'simodal',
                        modalOnShowClass: 'animated bounceIn',
                        keyboard: false,
                        closeOnClick: true,
                        kind: 'notification',
                        removeOnHide: true
                    });
                }
              }
        },
        showMessageModal: function(event){
            event.preventDefault();
            this.props.onMessageClick(this.props.visitor_message_url);
        },
        render: function(){
           return (
                   <li className="brand">
                        <a className="brand-logo flex-center" href={this.props.url}>
                            <img src={this.props.logo.thumbnail} alt="" />
                        </a>
                        <div className="brand-info">
                            <strong className="brand-name">{this.props.name}</strong>
                            <div className="brand-controls">
                                {this.props.category}
                            </div>
                            <div className="brand-buttons clearfix">

                                <a href="#"
                                   className={"btn btn-link add-to-favorites " + (this.props.can_add ? "" : "disabled")}
                                   onClick={this.toggleFavorites}>
                                    <i className={this.props.is_favorite ? "fa fa-times" : "fa fa-star"}/>
                                </a>
                                <a href="#" className="btn btn-link"  onClick={this.showMessageModal}>
                                    <i className="fa fa-envelope"/> </a>
                                <a href="#" className="btn btn-link"  onClick={this.showMessageModal}>
                                    <i className="fa fa-video-camera"/> </a>

                                <a href={this.props.vacancies_url} className={this.props.vacancies.length ? "btn btn-link pull-right" : "hidden"} >
                                    <i className="fa fa-user-plus"/> </a>
                            </div>
                        </div>
                    </li>
           )
       }
    });
    var HomepageWrapper = React.createClass({
        getInitialState: function(){
            return {
                results:  [], // actual results, list of returned objects
                categories:  [],
                queryset: {},
                count: 0, // total count
                next: false, // link to next results page
                previous: false, // link to previous results page
                favorites: [], // link to previous results page
                locked: false // prevent loading if request already sent
            }
        },
        componentDidMount: function(){
            var _this = this;
            console.log(StoreWrapper)
            this.setState({
                favorites: StoreWrapper.get('favorites') || []
            });
            this.loadBusinesses();
            StoreWrapper.on('itemAdded', function(){
                _this.favoritesUpdated();
            });
            if(this.props.showCategories)
            {
                this.loadCategories();
            }
        },
        onScroll: function(event){
            var height = event.target.scrollHeight;
            var y = event.target.scrollTop + event.target.offsetHeight;
            if (height - 200 <= y) {
                this.getNextPage();
            }
        },
        loadBusinesses: function(callback){
            var _this = this;
            callback = callback || noop;
            if(this.state.locked) return;
            this.setState({
                locked: true
            });
            if(this.props.is_favorite)
            {
                var list = StoreWrapper.get('favorites');
                if(!list || !list.length)
                  return;
                aja().url(this.props.url)
                .data({
                    pks: list.join(',')
                }).on('success', function(response){
                      _this.setState({
                            // in order to allow infite scroll results uppend
                            results: response.results, // _this.state.results.concat(),
                            count: response.count,
                            next: response.next,
                            previous: response.previous,
                            locked: false
                      }, callback);
                }).on("error", function(response){
                    console.error(response)
                }).go();
            }
            else
            {
               aja().url(this.props.url).data(this.state.queryset)
                .on('success', function(response){
                      _this.setState({
                            // in order to allow infite scroll results uppend
                            results: response.results, // _this.state.results.concat(),
                            count: response.count,
                            next: response.next,
                            previous: response.previous,
                            locked: false
                      }, callback);
                 }).go();
            }
        },
        loadCategories: function(callback){
            var _this = this;
            callback = callback || noop;
            if(this.props.categories.length){
                this.setState({
                    categories: this.props.categories
                }, callback);
                return;
            }
            aja().url(this.props.categories_url)
                .on('success', function(response){
                      _this.setState({
                            categories: response.results
                      }, callback);
                 }).go();
        },
        updateQuery: function(params){
            var queryset = extend({}, this.state.queryset);
            extend(queryset, params);
            this.setState({
                queryset: queryset
            }, this.loadBusinesses)

        },
        favoritesUpdated: function(){
            var _this = this;
            if(this.props.is_favorite)
            {
                var list = StoreWrapper.get('favorites');
                if(!list || !list.length)
                  return;
                aja().url(this.props.url)
                .data({ pks: list.join(',')}).on('success', function(response){
                      _this.setState({
                            // in order to allow infite scroll results uppend
                            results: response.results, // _this.state.results.concat(),
                            count: response.count,
                            next: response.next,
                            previous: response.previous,
                            locked: false
                      });
                }).on("error", function(response){
                    console.error(response)
                }).go();
            }
            else
            {
               this.setState({
                    favorites: StoreWrapper.get("favorites")
                });
            }
        },
        getNextPage: function(){
            var _this = this;
          if(this.state.next && !this.state.locked)
          {
              this.setState({
                  locked: true
              }, function(){
                  aja().url(this.state.next).on('success', function(response){
                      _this.setState({
                            // in order to allow infinite scroll results uppend
                            results: _this.state.results.concat(response.results), // _this.state.results.concat(),
                            count: response.count,
                            next: response.next,
                            previous: response.previous,
                            locked: false
                      });
                    }).on("error", function(response){
                        console.error(response)
                    }).go();
              });
          }
        },
        showMessageModal: function(visitor_message_url){
            var wrapper =  document.createElement('div');
            ReactDOM.render(<MessageModal csrf={this.props.csrf_token} submit_url={visitor_message_url} />, wrapper);
            new Simodal({
                content: wrapper
            })
        },
        setCategory: function(category_id, event){
            event.preventDefault();
            var queryset = {};
            if(event.target.classList.contains('active'))
            {
                event.target.classList.remove('active')
            }
            else
            {
                event.target.classList.add('active');
                queryset = extend({}, this.state.queryset);
                queryset['category'] = category_id;
            }
            this.setState({
                queryset: queryset
            }, this.loadBusinesses)
        },
        render: function(){
            var businesses = [];
            var favorites = this.state.favorites;

            for(var i = 0, l = this.state.results.length; i < l; i++)
            {
                var can_add = true;
                if(!this.props.is_favorite &&
                    favorites.indexOf(this.state.results[i].id) != -1)
                {

                    can_add = false;
                }
                businesses.push(<Organization onMessageClick={this.showMessageModal} can_add={can_add} key={this.state.results[i].id}
                    {...this.state.results[i]} is_favorite={this.props.is_favorite} />)
            }


            var categories = [];
            this.state.categories.forEach(function(category){
                var children = [];
                category.children.forEach(function(child){
                    children.push(
                        <li key={child.id}><a onClick={this.setCategory.bind(this, child.id)} href="#">
                            {child.name}</a></li>
                    )
                }.bind(this));
                if(children.length)
                {
                    categories.push(
                        <div className="dropdown category" key={category.id}>
                            <a href="#" className="children-toggler" >
                                <img src={category.icon.thumbnail} className="category-icon"/>
                            </a>
                            <div className="dropdown-content">
                                <a href="#"  className="list-headline"
                                   onClick={this.setCategory.bind(this, category.id)}>{category.name}</a>
                                <ul className="list-unstyled">
                                    {children}
                                </ul>
                            </div>
                        </div>
                    )
                } else
                {
                    categories.push(
                        <div className="category" key={category.id}>
                            <a href="#" className="children-toggler"  title={category.name} >
                                <img src={category.icon.thumbnail}
                                     className="category-icon"/>
                            </a>
                        </div>
                    )
                }

            }.bind(this));

            return (
                <div>
                    <div className={this.props.showCategories ? "filters-list" : "hidden"}>
                        <div className="wrapper">
                            {categories}
                        </div>
                    </div>
                    <div className="brands-wrapper" onScroll={this.onScroll}>
                          <ul className="homepage-brands" >
                              {businesses}
                          </ul>
                    </div>
              </div>
            )
      }
    });

    function constructor(elem, options){
        var defaults = {
            url: '#',
            categories: [],
            // has user registered company?
            is_corporate_user: false,
            categories_url: '/api/categories/',
            showCategories: true,
            data: {},
            options: false
        };
        var opts = extend(defaults, options);

        // small wrapper around function to enable passing of query parameters through functions
        // maybe should use Flux or render on server side instead of this??
        // TODO: think about that!
        function HomepageWidgetWrapper(opts, elem){
            this.options = opts;
            this.element = elem;
            this.reactComponent = ReactDOM.render(<HomepageWrapper {...opts} />, elem);

        }
        HomepageWidgetWrapper.prototype.updateQueryParams = function(params){
            this.reactComponent.updateQuery(params)
        };
        return HomepageWidgetWrapper(opts, elem);
    }
    return constructor;
}


if ( typeof define === 'function' && define.amd ) {
  // AMD
  define( [
      'react',
      'react-dom',
      'aja',
      'plugins/store-wrapper',
      'plugins/simodal'
    ], factory );

}
else {
  // browser global
    window.HomepageWidget = factory(
    window.React,
    window.ReactDOM,
    window.aja,
    window.StoreWrapper,
    window.Simodal
  );
}
})(window);
