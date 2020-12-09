from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

class AdminModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated and current_user.super

    def inaccessible_callback(self, name, **kwargs):
        if current_user.is_authenticated:
            return redirect("/")
        return redirect("/login")
