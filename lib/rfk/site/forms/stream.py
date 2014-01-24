from wtforms import Form, SubmitField, BooleanField, TextField, SelectField, \
    PasswordField, IntegerField, FieldList, FormField, HiddenField, TextAreaField, validators

from rfk.database.streaming import Stream


class StreamForm(Form):
    name = TextField('Name', [validators.Required()])
    code = TextField('Unique identifier', [validators.Required()])
    mount = TextField('Mountpoint', [validators.Required()])
    type = SelectField('Codec', coerce=int, choices=Stream.TYPES.tuples())
    quality = TextField('Quality', [validators.Required()])


def new_stream(rform):
    return StreamForm(rform)
