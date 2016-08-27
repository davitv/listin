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
    function noop() {}

    function sendForm(form, callback, err) {
        var formData = new FormData(form);
        var xhr = new XMLHttpRequest();
        xhr.open("POST", form.getAttribute("action"));
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        xhr.onreadystatechange = function () {
            // (3)

            if (xhr.readyState != 4) return;

            if ([200, 201].indexOf(xhr.status) != -1) callback && callback(JSON.parse(xhr.responseText));else err && err(JSON.parse(xhr.responseText));
        };
        xhr.send(formData);
    }

    function factory(React, ReactDOM, aja) {
        var RatingWidget = React.createClass({
            displayName: "RatingWidget",

            getInitialState: function () {
                return {
                    name: "",
                    description: "",
                    specialization: "",
                    degree: "",
                    skills: [],
                    errors: {},
                    languages: [],
                    post_url: "#",
                    is_loading: false,
                    result_message: false,
                    degree_choices: [[0, "unset"], [1, "bachelor"], [2, "Master"], [3, "Ph.D"], [4, "incomplete higher"]]
                };
            },
            componentDidMount: function () {
                var _this = this;
                this.setState({
                    post_url: this.props.post_url,
                    organization: this.props.organization
                });

                if (this.props.instance) {} else if (this.props.get_url) {
                    aja().url(this.props.get_url).on('success', function (res) {
                        var inst = res;
                        _this.setState({
                            name: inst.name,
                            description: inst.description,
                            specialization: inst.specialization,
                            degree: inst.degree,
                            skills: inst.skills,
                            languages: inst.languages,
                            organization: inst.organization
                        });
                    }).go();
                }
            },
            removeLanguage: function (language, event) {
                event.preventDefault();
                var languages = this.state.languages.slice();
                languages.splice(languages.indexOf(language), 1);
                this.setState({
                    languages: languages
                });
            },
            addLanguage: function (event) {
                event.preventDefault();
                var language_input = this.refs.language_input;
                var language = language_input.value.trim();
                if (this.state.languages.indexOf(language) == -1) {
                    var languages = this.state.languages.slice();
                    languages.push(language);
                    this.setState({
                        languages: languages
                    });
                    language_input.value = "";
                }
            },
            removeSkill: function (skill, event) {
                event.preventDefault();
                var skills = this.state.skills.slice();
                skills.splice(skills.indexOf(skill), 1);
                this.setState({
                    skills: skills
                });
            },
            addSkill: function (event) {
                event.preventDefault();
                var skills_input = this.refs.skills_input;
                var skill = skills_input.value.trim();
                if (this.state.skills.indexOf(skill) == -1) {
                    var skills = this.state.skills.slice();
                    skills.push(skill);
                    this.setState({
                        skills: skills
                    });
                    skills_input.value = "";
                }
            },
            isValid: function () {
                var errors = {};
                if (!this.state.name.length) {
                    errors['name'] = 'This field is required';
                }

                if (!this.state.description.length) {
                    errors['description'] = 'This field is required';
                }

                this.setState({
                    errors: errors
                });
                return Object.keys(errors).length === 0;
            },
            submitForm: function (event) {
                event.preventDefault();
                var _this = this;
                this.setState({
                    is_loading: true
                });
                if (this.isValid()) sendForm(ReactDOM.findDOMNode(this), function (res) {
                    if (res.id) _this.setState({
                        post_url: '/api/vacancies/' + res.id + '/',
                        is_loading: false
                    });
                }, function (err) {});else this.setState({ is_loading: false });
            },
            handleNameChange: function (key, event) {
                event.preventDefault();
                this.setState({
                    name: event.target.value
                });
            },
            handleDescriptionChange: function (key, event) {
                event.preventDefault();
                this.setState({
                    description: event.target.value
                });
            },
            handleSpecialityChange: function (event) {
                event.preventDefault();
                this.setState({
                    specialization: event.target.value
                });
            },
            render: function () {
                var skills = [];
                var skills_value = this.state.skills.join(',');

                this.state.skills.forEach(function (skill) {
                    skills.push(React.createElement(
                        "div",
                        { className: "input-group", key: skill },
                        React.createElement(
                            "div",
                            { className: "form-control" },
                            skill
                        ),
                        React.createElement(
                            "span",
                            { className: "input-group-btn" },
                            React.createElement(
                                "a",
                                { className: "btn btn-default remove-value", onClick: this.removeSkill.bind(this, skill) },
                                React.createElement("i", { className: "fa fa-times" })
                            )
                        )
                    ));
                }, this);
                var languages = [];
                var languages_value = this.state.languages.join(',');

                this.state.languages.forEach(function (language) {
                    languages.push(React.createElement(
                        "div",
                        { className: "input-group", key: language },
                        React.createElement(
                            "div",
                            { className: "form-control" },
                            language
                        ),
                        React.createElement(
                            "span",
                            { className: "input-group-btn" },
                            React.createElement(
                                "a",
                                { className: "btn btn-default remove-value", onClick: this.removeLanguage.bind(this, language) },
                                React.createElement("i", { className: "fa fa-times" })
                            )
                        )
                    ));
                }, this);
                var degree = [];
                this.state.degree_choices.forEach(function (choice) {
                    degree.push(React.createElement(
                        "option",
                        { key: choice[0], value: choice[0] },
                        choice[1]
                    ));
                }, this);

                return React.createElement(
                    "form",
                    { action: this.state.post_url, method: "POST" },
                    React.createElement(
                        "div",
                        { className: this.state.errors.name ? "form-group has-error" : "form-group" },
                        React.createElement(
                            "label",
                            { htmlFor: "cv-name", className: "control-label" },
                            "Vacancy Name"
                        ),
                        React.createElement("input", { name: "name", id: "cv-name", className: "form-control", value: this.state.name,
                            onChange: this.handleNameChange.bind(this, 'name') })
                    ),
                    React.createElement(
                        "div",
                        { className: this.state.errors.description ? "form-group has-error" : "form-group" },
                        React.createElement(
                            "label",
                            { htmlFor: "cv-description", className: "control-label" },
                            "Vacancy Description"
                        ),
                        React.createElement("textarea", { name: "description", onChange: this.handleDescriptionChange.bind(this, 'name'), value: this.state.description, id: "cv-description", cols: "30", rows: "5", className: "form-control" })
                    ),
                    React.createElement(
                        "h4",
                        null,
                        "Education"
                    ),
                    React.createElement(
                        "div",
                        { className: "row" },
                        React.createElement(
                            "div",
                            { className: "col-md-6" },
                            React.createElement(
                                "div",
                                { className: "form-group" },
                                React.createElement(
                                    "label",
                                    { htmlFor: "cv-speciality", className: "control-label" },
                                    "Speciality"
                                ),
                                React.createElement("input", { onChange: this.handleSpecialityChange, name: "specialization", id: "cv-speciality", className: "form-control", value: this.state.specialization })
                            )
                        ),
                        React.createElement(
                            "div",
                            { className: "col-md-6" },
                            React.createElement(
                                "div",
                                { className: "form-group" },
                                React.createElement(
                                    "label",
                                    { htmlFor: "cv-degree", className: "control-label" },
                                    "Degree"
                                ),
                                React.createElement(
                                    "select",
                                    { name: "degree", id: "", value: this.state.degree, onChange: function (event) {
                                            this.setState({
                                                'degree': event.target.value
                                            });
                                        }.bind(this) },
                                    degree
                                )
                            )
                        )
                    ),
                    React.createElement(
                        "div",
                        { className: "row" },
                        React.createElement(
                            "div",
                            { className: "col-sm-6" },
                            React.createElement(
                                "div",
                                { className: "form-group list-input" },
                                React.createElement(
                                    "label",
                                    { htmlFor: "", className: "control-label" },
                                    "Skills"
                                ),
                                React.createElement("input", { type: "hidden", className: "concatenated-input", name: "skills" }),
                                React.createElement(
                                    "div",
                                    { className: "list-wrapper" },
                                    skills
                                ),
                                React.createElement(
                                    "div",
                                    { className: "input-group" },
                                    React.createElement("input", { type: "text", name: "", ref: "skills_input", className: "form-control", placeholder: "Skill name" }),
                                    React.createElement("input", { type: "hidden", name: "skills", value: skills_value }),
                                    React.createElement(
                                        "span",
                                        { className: "input-group-btn" },
                                        React.createElement(
                                            "a",
                                            { className: "btn btn-primary add-value", onClick: this.addSkill },
                                            React.createElement("i", { className: "fa fa-plus" })
                                        )
                                    )
                                )
                            )
                        ),
                        React.createElement(
                            "div",
                            { className: "col-sm-6" },
                            React.createElement(
                                "div",
                                { className: "form-group list-input" },
                                React.createElement(
                                    "label",
                                    { htmlFor: "", className: "control-label" },
                                    "Languages"
                                ),
                                React.createElement(
                                    "div",
                                    { className: "list-wrapper" },
                                    languages
                                ),
                                React.createElement(
                                    "div",
                                    { className: "input-group" },
                                    React.createElement("input", { type: "text", ref: "language_input", className: "form-control", name: "languages", placeholder: "Language name" }),
                                    React.createElement("input", { type: "hidden", name: "languages", value: languages_value }),
                                    React.createElement(
                                        "span",
                                        { className: "input-group-btn" },
                                        React.createElement(
                                            "button",
                                            { className: "btn btn-primary add-value", onClick: this.addLanguage },
                                            React.createElement("i", { className: "fa fa-plus" })
                                        )
                                    )
                                )
                            )
                        )
                    ),
                    React.createElement(
                        "div",
                        null,
                        React.createElement("hr", null),
                        React.createElement("input", { type: "hidden", name: "csrfmiddlewaretoken", value: this.props.csrf_token }),
                        React.createElement("input", { type: "hidden", name: "organization", value: this.state.organization }),
                        React.createElement(
                            "button",
                            { className: this.state.is_loading ? "btn btn-primary disabled" : "btn btn-primary", onClick: this.submitForm },
                            React.createElement("i", { className: this.state.is_loading ? "fa fa-spinner fa-spin" : "fa fa-save" }),
                            " Save Vacancy"
                        )
                    )
                );
            }
        });

        function constructor(elem, options) {
            var defaults = {
                instance: false,
                get_url: 0,
                csrf_token: 0,
                organization: 0,
                post_url: '#'
            };
            var opts = extend(defaults, options);
            return ReactDOM.render(React.createElement(RatingWidget, opts), elem);
        }
        return constructor;
    }

    if (typeof define === 'function' && define.amd) {
        // AMD
        define(['react', 'react-dom', 'aja/aja.min'], factory);
    } else {
        // browser global
        window.VacancyFormWidget = factory(window.React, window.ReactDOM, window.aja);
    }
})(window);