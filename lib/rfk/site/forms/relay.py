from wtforms import Form, SubmitField, BooleanField, TextField, SelectField, \
    PasswordField, IntegerField, FieldList, FormField, HiddenField, TextAreaField, validators

from rfk.database.streaming import Relay


class RelayForm(Form):
    address = TextField('Address', [validators.Required()])
    port = TextField('Port', [validators.Required()])
    bandwidth = TextField('Bandwidth in kbps', [validators.Required()])
    admin_username = TextField('Admin Username', [validators.Required()])
    admin_password = TextField('Admin Password', [validators.Required()])
    auth_username = TextField('Auth Username', [validators.Required()])
    auth_password = TextField('Auth Password', [validators.Required()])
    relay_username = TextField('Relay Username', [validators.Required()])
    relay_password = TextField('Relay Password', [validators.Required()])
    type = SelectField('Type', coerce=int, choices=Relay.TYPE.tuples())


def new_relay(rform):
    return RelayForm(rform)
