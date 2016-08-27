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

    function factory(React, ReactDOM, aja, moment) {

        var Comment = React.createClass({
            displayName: "Comment",

            render: function () {
                return React.createElement(
                    "div",
                    { className: "comment" },
                    React.createElement(
                        "div",
                        { className: "comment-userpic" },
                        React.createElement("img", { src: this.props.user.userpic.thumbnail, alt: "", className: "img-responsive" })
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
                                this.props.user.first_name + ' ' + this.props.user.last_name
                            ),
                            " ",
                            React.createElement(
                                "small",
                                { className: "datetime" },
                                React.createElement("i", { className: "fa fa-clock-o" }),
                                " ",
                                moment(this.props.created_at).fromNow()
                            )
                        ),
                        React.createElement(
                            "p",
                            { className: "comment-p" },
                            " ",
                            this.props.text,
                            " "
                        )
                    )
                );
            }
        });

        var CommentsForm = React.createClass({
            displayName: "CommentsForm",

            send: function (callback) {
                var _this = this;
                var formData = new FormData(ReactDOM.findDOMNode(this));
                var xhr = new XMLHttpRequest();
                xhr.open("POST", this.props.url);
                xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
                xhr.onreadystatechange = function () {
                    // (3)
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
            onSubmit: function (event) {
                event.preventDefault();
                this.send(this.props.onSend);
            },
            clear: function () {
                var textarea = ReactDOM.findDOMNode(this.refs.input_text);
                textarea.value = '';
            },
            render: function () {

                return React.createElement(
                    "form",
                    { action: this.props.url, method: "POST", onSubmit: this.onSubmit },
                    React.createElement(
                        "div",
                        { className: "form-group" },
                        React.createElement("textarea", { id: "", cols: "30", rows: "5", name: "text", className: "form-control", ref: "input_text" })
                    ),
                    React.createElement(
                        "div",
                        { className: "form-group" },
                        React.createElement("input", { type: "hidden", name: "csrfmiddlewaretoken", value: this.props.csrf_token }),
                        React.createElement("input", { type: "hidden", name: "organization", value: this.props.organization }),
                        React.createElement(
                            "button",
                            { className: "btn-primary btn" },
                            "Submit"
                        )
                    )
                );
            }
        });

        var CommentsWrapper = React.createClass({
            displayName: "CommentsWrapper",

            getInitialState: function () {
                return {
                    results: [], // actual results, list of returned objects
                    users: [], // actual results, list of returned objects
                    count: 0, // total count
                    next: false, // link to next results page
                    previous: false, // link to previous results page
                    locked: false // prevent loading if request already sent
                };
            },
            componentDidMount: function () {
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

                aja().url(this.props.url).data({
                    organization: this.props.organization_id
                }).on('success', function (response) {
                    _this.setState({
                        // in order to allow infite scroll results uppend
                        results: response.results, // _this.state.results.concat(),
                        count: response.count,
                        next: response.next,
                        previous: response.previous
                    }, callback);
                }).go();
            },
            render: function () {
                var comments = [];

                for (var i = 0, l = this.state.results.length; i < l; i++) {
                    comments.push(React.createElement(Comment, _extends({ key: this.state.results[i].id }, this.state.results[i])));
                }
                if (!l) {
                    comments = React.createElement(
                        "div",
                        { className: "alert alert-info" },
                        React.createElement(
                            "strong",
                            null,
                            "There are no comments yet!"
                        )
                    );
                }

                var commentForm = null;
                if (this.props.is_authed) {
                    commentForm = React.createElement(CommentsForm, {
                        url: this.props.url,
                        csrf_token: this.props.csrf_token,
                        organization: this.props.organization_id,
                        onSend: this.onCommentSent
                    });
                } else {
                    commentForm = [React.createElement(
                        "div",
                        null,
                        React.createElement(
                            "h5",
                            null,
                            "You have to log in for leaving a comment"
                        ),
                        React.createElement(
                            "div",
                            { className: "btn-group", role: "group" },
                            React.createElement(
                                "a",
                                { className: "btn btn-default", href: this.props.social_urls.fb },
                                React.createElement("i", { className: "fa fa-facebook fa-fw" })
                            ),
                            React.createElement(
                                "a",
                                { className: "btn btn-default", href: this.props.social_urls.vk },
                                React.createElement("i", { className: "fa fa-vk fa-fw" })
                            ),
                            React.createElement(
                                "a",
                                { className: "btn btn-default disabled", href: "#" },
                                React.createElement("i", { className: "fa fa-linkedin fa-fw" })
                            ),
                            React.createElement(
                                "a",
                                { className: "btn btn-default", href: this.props.social_urls.gp },
                                React.createElement("i", { className: "fa fa-google-plus fa-fw" })
                            )
                        )
                    )];
                }
                return React.createElement(
                    "div",
                    { className: "widget widget-comments" },
                    React.createElement(
                        "div",
                        { className: "widget-content", ref: "comments_wrapper" },
                        comments
                    ),
                    React.createElement(
                        "div",
                        { className: "widget-footer" },
                        commentForm
                    )
                );
            }
        });

        function constructor(elem, options) {
            var defaults = {
                url: '#',
                users_url: '#',
                data: {},
                organization_id: null,
                options: false,
                connectedForm: false
            };
            var opts = extend(defaults, options);
            return ReactDOM.render(React.createElement(CommentsWrapper, opts), elem);
        }
        return constructor;
    }

    if (typeof define === 'function' && define.amd) {
        // AMD
        define(['react', 'react-dom', 'aja/aja.min', 'moment'], factory);
    } else {
        // browser global
        window.CommentsWidget = factory(window.React, window.ReactDOM, window.aja, window.moment);
    }
})(window);