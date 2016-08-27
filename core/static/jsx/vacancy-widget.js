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
    function noop(){

    }

     function sendForm(form, callback, err) {
        var formData = new FormData(form);
        var xhr = new XMLHttpRequest();
        xhr.open("POST", form.getAttribute("action"));
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        xhr.onreadystatechange = function() { // (3)

          if (xhr.readyState != 4) return;

          if ([200, 201].indexOf(xhr.status) != -1)
            callback && callback(JSON.parse(xhr.responseText));
          else
            err && err(JSON.parse(xhr.responseText));
        };
        xhr.send(formData);
     }
    
function factory(React, ReactDOM, aja){
    var RatingWidget = React.createClass({
        getInitialState: function(){
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
                degree_choices: [
                    [0, "unset"],
                    [1, "bachelor"],
                    [2, "Master"],
                    [3, "Ph.D"],
                    [4, "incomplete higher"]
                ]
          }
        },
        componentDidMount: function(){
            var _this = this;
            this.setState({
                post_url: this.props.post_url,
                organization: this.props.organization
            });
            
            if(this.props.instance)
            {

            }
            else if(this.props.get_url)
            {
                aja().url(this.props.get_url)
                    .on('success', function(res){
                        var inst = res;
                        _this.setState({
                            name: inst.name,
                            description: inst.description,
                            specialization: inst.specialization,
                            degree: inst.degree,
                            skills: inst.skills,
                            languages: inst.languages,
                            organization: inst.organization
                        })
                    }).go();
            }
        },
        removeLanguage: function(language, event){
            event.preventDefault();
            var languages = this.state.languages.slice();
            languages.splice(languages.indexOf(language), 1);
            this.setState({
                languages: languages
            })
        },
        addLanguage: function(event){
            event.preventDefault();
            var language_input = this.refs.language_input;
            var language = language_input.value.trim();
            if(this.state.languages.indexOf(language) == -1)
            {
                var languages = this.state.languages.slice();
                languages.push(language);
                this.setState({
                    languages: languages
                });
                language_input.value = "";
            }
        },
        removeSkill: function(skill, event){
            event.preventDefault();
            var skills = this.state.skills.slice();
            skills.splice(skills.indexOf(skill), 1);
            this.setState({
                skills: skills
            })
        },
        addSkill: function(event){
            event.preventDefault();
            var skills_input = this.refs.skills_input;
            var skill = skills_input.value.trim();
            if(this.state.skills.indexOf(skill) == -1)
            {
                var skills = this.state.skills.slice();
                skills.push(skill);
                this.setState({
                    skills: skills
                });
                skills_input.value = "";
            }
        },
        isValid: function(){
            var errors = {};
            if(!this.state.name.length)
            {
                errors['name'] = 'This field is required';
            }

            if(!this.state.description.length)
            {
                errors['description'] = 'This field is required';
            }

            this.setState({
                errors: errors
            });
            return Object.keys(errors).length === 0;
        },
        submitForm: function(event){
            event.preventDefault();
            var _this = this;
            this.setState({
                is_loading: true
            });
            if(this.isValid())
                sendForm(ReactDOM.findDOMNode(this), function(res){
                    if(res.id)
                        _this.setState({
                            post_url: '/api/vacancies/' + res.id + '/',
                            is_loading: false
                        });
                },
                function(err){

                });
            else this.setState({is_loading: false});
        },
        handleNameChange: function(key, event){
            event.preventDefault();
            this.setState({
                name: event.target.value
            });
        },
        handleDescriptionChange: function(key, event){
            event.preventDefault();
            this.setState({
                description: event.target.value
            })
        },
        handleSpecialityChange: function(event){
            event.preventDefault();
            this.setState({
                specialization: event.target.value
            })
        },
        render: function(){
            var skills = [];
            var skills_value = this.state.skills.join(',');

            this.state.skills.forEach(function(skill){
               skills.push(
                   <div className="input-group" key={skill}>
                      <div  className="form-control" >{skill}</div>
                      <span className="input-group-btn">
                        <a className="btn btn-default remove-value" onClick={this.removeSkill.bind(this, skill)}>
                            <i className="fa fa-times"/>
                        </a>
                      </span>
                  </div>
               )
            }, this);
            var languages = [];
            var languages_value = this.state.languages.join(',');

            this.state.languages.forEach(function(language){
               languages.push(
                   <div className="input-group" key={language}>
                      <div  className="form-control" >{language}</div>
                      <span className="input-group-btn">
                        <a className="btn btn-default remove-value" onClick={this.removeLanguage.bind(this, language)}>
                            <i className="fa fa-times"/>
                        </a>
                      </span>
                  </div>
               )
            }, this);
            var degree = [];
            this.state.degree_choices.forEach(function(choice){
               degree.push(
                   <option key={choice[0]} value={choice[0]}>{choice[1]}</option>
               )
            }, this);

            return (
                <form action={this.state.post_url} method="POST" >
                      <div className={this.state.errors.name ? "form-group has-error" : "form-group"}>
                          <label htmlFor="cv-name" className="control-label">Vacancy Name</label>
                          <input name="name" id="cv-name" className="form-control" value={this.state.name}
                          onChange={this.handleNameChange.bind(this, 'name')} />
                      </div>
                      <div className={this.state.errors.description ? "form-group has-error" : "form-group"} >
                          <label htmlFor="cv-description" className="control-label">Vacancy Description</label>
                          <textarea name="description" onChange={this.handleDescriptionChange.bind(this, 'name')} value={this.state.description} id="cv-description" cols="30" rows="5" className="form-control" />
                      </div>
        
                      <h4>Education</h4>
                      <div className="row">
                          <div className="col-md-6">
                              <div className="form-group">
                                  <label htmlFor="cv-speciality" className="control-label">Speciality</label>
                                  <input onChange={this.handleSpecialityChange} name="specialization" id="cv-speciality" className="form-control" value={this.state.specialization}/>
                              </div>
                          </div>
                          <div className="col-md-6">
        
                          <div className="form-group">
                              <label htmlFor="cv-degree" className="control-label">Degree</label>
                              <select name="degree" id="" value={this.state.degree} onChange={function(event){
                                this.setState({
                                    'degree': event.target.value
                                })
                              }.bind(this)}>
                                  {degree}
                              </select>
                          </div>
                          </div>
                      </div>
        
                      <div className="row">
                          <div className="col-sm-6">
                              <div className="form-group list-input">
                                <label htmlFor="" className="control-label">Skills</label>
                                <input type="hidden" className="concatenated-input" name="skills" />
                                <div className="list-wrapper">
                                    {skills}
                                </div>
                                <div className="input-group">
                                  <input type="text" name=""  ref="skills_input" className="form-control" placeholder="Skill name" />
                                  <input type="hidden" name="skills"  value={skills_value} />
                                  <span className="input-group-btn">
                                    <a className="btn btn-primary add-value" onClick={this.addSkill}>
                                        <i className="fa fa-plus"/>
                                    </a>
                                  </span>
                                </div>
                              </div>
                          </div>
                          <div className="col-sm-6">
                              <div className="form-group list-input">
                                <label htmlFor="" className="control-label">Languages</label>
                                  <div className="list-wrapper">
                                      {languages}
                                  </div>
                                <div className="input-group">
                                  <input type="text" ref="language_input" className="form-control" name="languages" placeholder="Language name" />
                                  <input type="hidden" name="languages"  value={languages_value} />
                                  <span className="input-group-btn">
                                    <button className="btn btn-primary add-value" onClick={this.addLanguage}>
                                        <i className="fa fa-plus"/>
                                    </button>
                                  </span>
                                </div>
                              </div>
                          </div>
                      </div>
                      <div>
                          <hr/>
                          <input type="hidden" name="csrfmiddlewaretoken" value={this.props.csrf_token} />
                          <input type="hidden" name="organization" value={this.state.organization} />
                          <button className={this.state.is_loading ?  "btn btn-primary disabled" :  "btn btn-primary"} onClick={this.submitForm}>
                            <i className={this.state.is_loading ?  "fa fa-spinner fa-spin" :  "fa fa-save"}/> Save Vacancy
                          </button>
                      </div>
                </form>
            )
        }
    });

    function constructor(elem, options){
        var defaults = {
            instance: false,
            get_url: 0,
            csrf_token: 0,
            organization: 0,
            post_url: '#'
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
      'aja/aja.min'
    ], factory );

}
else {
  // browser global
    window.VacancyFormWidget = factory(
    window.React,
    window.ReactDOM,
    window.aja
  );
}
})(window);
