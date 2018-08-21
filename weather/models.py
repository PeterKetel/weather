from datetime import datetime
from weather import db, login_manager, admin
from flask_login import UserMixin, LoginManager
from flask_admin.contrib.sqla import ModelView
from flask_admin import  AdminIndexView
from flask_admin.contrib import sqla


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#Models
class WeatherModelView(sqla.ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to the login page is the user doesn't have access
        return redirect(url_for('login', next=request.url))

class WeatherAdminIndexView(AdminIndexView):

    def is_accessible(self):
        return login.current_user.is_authenticated

    def inaccessible_callback(self, user_name, **kwargs):
        # redirect to the login page is the user doesn't have access
        return redirect(url_for('login', next=request.url))


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"City('{self.name}')"

class ViewCityList(ModelView):
    form_columns = ['name', 'user_id']

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(32), unique=True, nullable=False)
    user_role = db.Column(db.String(1), nullable=False, default='u')
    email = db.Column(db.String(64), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    last_seen = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    cities = db.relationship('City', backref='location', lazy=True)

    def __repr__(self):
        return f"User('{self.user_name}', '{self.user_role}','{self.email}', '{self.image_file}', '{self.last_seen}')"

class ViewUser(ModelView):
    form_columns = ['id', 'user_name', 'email']


admin.add_view(ViewUser(User, db.session))
admin.add_view(ViewCityList(City, db.session))

