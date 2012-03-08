# a little trick so you can run:
# $ python example/app.py 
# from the root of the security project
import sys, os
sys.path.pop(0)
sys.path.insert(0, os.getcwd())

from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import (Security, LoginForm, user_datastore, 
                      login_required, roles_required, roles_accepted)
from flask.ext.security.datastore.sqlalchemy import SQLAlchemyUserDatastore

def create_app(auth_config=None):
    
    app = Flask(__name__)
    app.debug = True
    app.config['SECRET_KEY'] = 'secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['AUTH'] = auth_config or {}
    
    db = SQLAlchemy(app)
    
    Security(app, SQLAlchemyUserDatastore(db))
    
    @app.route('/')
    def index():
        return render_template('index.html', content='Home Page')
    
    @app.route('/login')
    def login():
        return render_template('login.html', content='Login Page', form=LoginForm())
    
    @app.route('/custom_login')
    def custom_login():
        return render_template('login.html', content='Custom Login Page', form=LoginForm())
    
    @app.route('/profile')
    @login_required
    def profile():
        return render_template('index.html', content='Profile Page')
    
    @app.route('/post_login')
    @login_required
    def post_login():
        return render_template('index.html', content='Post Login')
    
    @app.route('/post_logout')
    def post_logout():
        return render_template('index.html', content='Post Logout')
    
    @app.route('/admin')
    @roles_required('admin')
    def admin():
        return render_template('index.html', content='Admin Page')
    
    @app.route('/admin_or_editor')
    @roles_accepted('admin', 'editor')
    def admin_or_editor():
        return render_template('index.html', content='Admin or Editor Page')
    
    @app.before_first_request
    def before_first_request():
        db.create_all()
        
        user_datastore.create_user(username='matt', email='matt@lp.com', 
                                   password='password',
                                   roles=['admin'])
        
        user_datastore.create_user(username='joe', email='joe@lp.com', 
                                   password='password',
                                   roles=['editor'])
        
        user_datastore.create_user(username='jill', email='jill@lp.com', 
                                   password='password',
                                   roles=['author'])
        
        user_datastore.create_user(username='tiya', email='tiya@lp.com', 
                                   password='password', active=False)
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run()