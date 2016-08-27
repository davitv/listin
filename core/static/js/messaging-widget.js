var _extends = Object.assign || function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; };

(function (window) {
    // vars
    var document = window.document;

    // -------------------------- helpers -------------------------- //

    // extend objects
    function extend(a, b) {
        for (var prop in b) {
            a[prop] = b[prop];
        }
        return a;
    }
    function noop() {};

    function sendForm(form, callback) {
        var formData = new FormData(form);
        var xhr = new XMLHttpRequest();
        xhr.open("POST", form.getAttribute("action"));
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        xhr.onreadystatechange = function () {
            // (3)
            if (xhr.readyState != 4) return;
            callback && callback(JSON.parse(xhr.responseText));
        };
        xhr.send(formData);
    }

    function factory(React, ReactDOM, aja, moment) {
        var Message = React.createClass({
            displayName: "Message",

            render: function () {
                return React.createElement(
                    "div",
                    { className: "comment " + (this.props.current_user == this.props.sender.id ? "comment-right" : '') },
                    React.createElement(
                        "div",
                        { className: "comment-userpic" },
                        React.createElement("img", { src: this.props.sender.userpic.thumbnail, alt: "", className: "img-responsive" })
                    ),
                    React.createElement(
                        "div",
                        { className: "comment-text" },
                        React.createElement("span", { className: "arrow" }),
                        React.createElement(
                            "div",
                            { className: "author" },
                            React.createElement(
                                "a",
                                { href: "#", className: "author" },
                                this.props.sender.first_name,
                                " ",
                                this.props.sender.last_name,
                                " "
                            ),
                            React.createElement(
                                "small",
                                { className: "datetime" },
                                React.createElement("i", { className: "fa fa-clock-o" }),
                                React.createElement(
                                    "span",
                                    null,
                                    "12 часов назад"
                                )
                            )
                        ),
                        React.createElement(
                            "p",
                            { className: "comment-p" },
                            this.props.text
                        )
                    )
                );
            }
        });

        var MessagingWrapper = React.createClass({
            displayName: "MessagingWrapper",

            getInitialState: function () {
                return {
                    usersList: [],
                    results: [], // actual results, list of returned objects
                    recipient: null, // actual results, list of returned objects
                    currentRoom: {
                        name: "Organization Room",
                        pk: 0
                    }, // actual results, list of returned objects
                    count: 0, // total count
                    next: false, // link to next results page
                    previous: false, // link to previous results page
                    locked: false // prevent loading if request already sent
                };
            },
            componentDidMount: function () {
                this.loadUsers();
                this.loadComments();
            },
            onCommentSent: function () {
                this.loadComments(function () {
                    var comments_wrapper = ReactDOM.findDOMNode(this.refs.comments_wrapper);
                    comments_wrapper.scrollTop = comments_wrapper.scrollHeight;
                });
            },
            loadComments: function (callback) {
                var _this = this;
                callback = callback || noop;
                aja().url(this.props.url).on('success', function (response) {
                    _this.setState({
                        // in order to allow infite scroll results uppend
                        results: response.results, // _this.state.results.concat(),
                        count: response.count,
                        next: response.next,
                        previous: response.previous
                    }, callback);
                }).go();
            },
            loadUsers: function (callback) {
                var _this = this;
                callback = callback || noop;

                aja().url(this.props.users_url).header("Accept", '*/*').on('success', function (response) {
                    _this.setState({
                        usersList: response.results
                    }, callback);
                }).go();
            },
            onPost: function (event) {
                var _this = this;
                event.preventDefault();
                sendForm(ReactDOM.findDOMNode(this.refs.postForm), function () {
                    _this.loadComments();
                });
            },
            onRecipientChange: function (user, event) {
                var _this = this;
                event.preventDefault();
                this.setState({
                    recipient: user
                });
            },
            render: function () {
                var users = [];
                var _this = this;
                var room_name = this.state.recipient ? this.state.recipient.first_name + ' ' + this.state.recipient.last_name : "Organization Room";
                this.state.usersList.forEach(function (user) {
                    users.push(React.createElement(
                        "li",
                        { key: user.id },
                        React.createElement(
                            "a",
                            { href: "#", onClick: _this.onRecipientChange.bind(_this, user) },
                            React.createElement("img", { src: user.userpic.thumbnail, alt: user.first_name + ' ' + user.last_name, className: "userpic" }),
                            React.createElement(
                                "div",
                                { className: "user-name" },
                                user.first_name + ' ' + user.last_name
                            ),
                            React.createElement(
                                "div",
                                { className: "user-position" },
                                user.position
                            )
                        )
                    ));
                });
                if (!users.length) users = React.createElement(
                    "div",
                    { className: "alert alert-info" },
                    "No staff for this organization"
                );

                var messages = [];
                this.state.results.forEach(function (message) {
                    messages.push(React.createElement(Message, _extends({}, message, { key: message.id, current_user: _this.props.current_user })));
                });

                return React.createElement(
                    "div",
                    { className: "widget widget-messaging" },
                    React.createElement(
                        "div",
                        { className: "widget-headline" },
                        React.createElement(
                            "h4",
                            { className: "pull-left" },
                            React.createElement("i", { className: "fa fa-comment-o" }),
                            " Messaging "
                        ),
                        React.createElement(
                            "div",
                            { className: "dropdown dropdown-button pull-right" },
                            React.createElement(
                                "a",
                                { className: "dropdown-link btn btn-default", href: "#" },
                                room_name,
                                React.createElement("i", { className: "fa fa-angle-down fa-fw" })
                            ),
                            React.createElement(
                                "div",
                                { className: "dropdown-content users-dropdown" },
                                React.createElement(
                                    "ul",
                                    { className: "list-unstyled" },
                                    users
                                )
                            )
                        )
                    ),
                    React.createElement(
                        "div",
                        { className: "widget-content" },
                        messages
                    ),
                    React.createElement(
                        "div",
                        { className: "widget-footer" },
                        React.createElement(
                            "form",
                            { action: this.props.post_url, onSubmit: this.onPost, method: "POST", ref: "postForm" },
                            React.createElement(
                                "div",
                                { className: "chat-form" },
                                React.createElement(
                                    "div",
                                    { className: "input-cont" },
                                    React.createElement("input", { className: "form-control", type: "text", name: "text", placeholder: "fdfs" })
                                ),
                                React.createElement("input", { type: "hidden", name: "csrfmiddlewaretoken", value: this.props.csrf_token }),
                                React.createElement("input", { type: "hidden", name: "to_users", value: this.state.recipient ? this.state.recipient.id : '' }),
                                React.createElement(
                                    "div",
                                    { className: "btn-cont" },
                                    React.createElement("span", { className: "arrow" }),
                                    React.createElement(
                                        "button",
                                        { className: "btn blue icn-only" },
                                        React.createElement("i", { className: "fa fa-check icon-white" })
                                    )
                                )
                            )
                        )
                    )
                );
            }
        });

        function constructor(elem, options) {
            var defaults = {
                url: '#',
                users_url: '#',
                post_url: '#',
                data: {},
                options: false,
                connectedForm: false
            };
            var opts = extend(defaults, options);
            return ReactDOM.render(React.createElement(MessagingWrapper, opts), elem);
        }
        return constructor;
    }

    if (typeof define === 'function' && define.amd) {
        // AMD
        define(['react', 'react-dom', 'aja/aja.min', 'moment'], factory);
    } else {
        // browser global
        window.MessagingWidget = factory(window.React, window.ReactDOM, window.aja, window.moment);
    }
})(window);