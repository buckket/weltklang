from wtforms import Form, SubmitField, BooleanField, TextField, SelectField,\
                    PasswordField, IntegerField, FieldList, FormField,HiddenField,TextAreaField, validators

class ApiKeyForm(Form):
    application = TextField('Application', [validators.Required()])
    description = TextField('Description', [validators.Required()])
    
def new_apikey_form(rform):
    return ApiKeyForm(rform)