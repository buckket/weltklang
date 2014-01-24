from wtforms import Form, SubmitField, BooleanField, TextField, SelectField, \
    PasswordField, IntegerField, FieldList, FormField, HiddenField, TextAreaField, validators


class SeriesForm(Form):
    name = TextField('Name', [validators.Required()])
    description = TextAreaField('Description', [validators.Required()])
    public = BooleanField('Public')
    image = HiddenField('Image')


def new_series_form(rform):
    return SeriesForm(rform)
