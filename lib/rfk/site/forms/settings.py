from wtforms import Form, SubmitField, BooleanField, TextField, SelectField, \
    PasswordField, IntegerField, FieldList, FormField, HiddenField, TextAreaField, validators


class SettingsForm(Form):
    # basic settings
    old_password = PasswordField('Old Password', [validators.Required()])
    new_password = PasswordField('New Password', [validators.Optional(),
                                                  validators.Length(min=5, message='Password too short.'),
                                                  validators.EqualTo('new_password_retype',
                                                                     message='Passwords must match.')])
    new_password_retype = PasswordField('Verify password', [validators.Optional()])
    email = TextField('E-Mail', [validators.Optional(), validators.Email(),
                                 validators.Length(max=255, message='Address too long.')])

    # default show settings
    show_def_name = TextField('Name',
                              [validators.Optional(), validators.Length(max=255, message='Show name too long.')])
    show_def_desc = TextField('Description',
                              [validators.Optional(), validators.Length(max=255, message='Show description too long.')])
    show_def_tags = TextField('Tags',
                              [validators.Optional(), validators.Length(max=255, message='Show tags too long.')])
    show_def_logo = HiddenField('Logo', [validators.Optional()])

    # misc settings
    use_icy = BooleanField('Use ICY-Tags for unplanned shows', [validators.Optional()])
