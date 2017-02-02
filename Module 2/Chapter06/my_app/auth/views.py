import requests
from flask import request, render_template, flash, redirect, url_for, \
    session, Blueprint, g
from flask.ext.login import current_user, login_user, logout_user, \
    login_required
from my_app import db, login_manager, oid, facebook, google, twitter
from my_app.auth.models import User, RegistrationForm, LoginForm, OpenIDForm

auth = Blueprint('auth', __name__)

GOOGLE_OAUTH2_USERINFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@auth.before_request
def get_current_user():
    g.user = current_user


@auth.route('/')
@auth.route('/home')
def home():
    return render_template('home.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('username'):
        flash('Your are already logged in.', 'info')
        return redirect(url_for('auth.home'))

    form = RegistrationForm(request.form)

    if request.method == 'POST' and form.validate():
        username = request.form.get('username')
        password = request.form.get('password')
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash(
                'This username has been already taken. Try another one.',
                'warning'
            )
            return render_template('register.html', form=form)
        user = User(username, password)
        db.session.add(user)
        db.session.commit()
        flash('You are now registered. Please login.', 'success')
        return redirect(url_for('auth.login'))

    if form.errors:
        flash(form.errors, 'danger')

    return render_template('register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and current_user.is_authenticated():
        flash('You are already logged in.', 'info')
        return redirect(url_for('home'))

    form = LoginForm(request.form)
    openid_form = OpenIDForm(request.form)

    if request.method == 'POST':
        if request.form.has_key('openid'):
            openid_form.validate()
            if openid_form.errors:
                flash(openid_form.errors, 'danger')
                return render_template(
                    'login.html', form=form, openid_form=openid_form
                )
            openid = request.form.get('openid')
            return oid.try_login(openid, ask_for=['email', 'nickname'])
        else:
            form.validate()
            if form.errors:
                flash(form.errors, 'danger')
                return render_template(
                    'login.html', form=form, openid_form=openid_form
                )
            username = request.form.get('username')
            password = request.form.get('password')
            existing_user = User.query.filter_by(username=username).first()

            if not (existing_user and existing_user.check_password(password)):
                flash(
                    'Invalid username or password. Please try again.',
                    'danger'
                )
                return render_template('login.html', form=form)

        login_user(existing_user)
        flash('You have successfully logged in.', 'success')
        return redirect(url_for('auth.home'))

    if form.errors:
        flash(form.errors, 'danger')

    return render_template('login.html', form=form, openid_form=openid_form)


@oid.after_login
def after_login(resp):
    username = resp.nickname or resp.email
    if not username:
        flash('Invalid login. Please try again.', 'danger')
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User(username, '')
        db.session.add(user)
        db.session.commit()
    login_user(user)
    return redirect(url_for('auth.home'))


@auth.route('/facebook-login')
def facebook_login():
    return facebook.authorize(
        callback=url_for(
            'auth.facebook_authorized',
            next=request.args.get('next') or request.referrer or None,
            _external=True
        ))


@auth.route('/facebook-login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['facebook_oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')

    user = User.query.filter_by(username=me.data['email']).first()
    if not user:
        user = User(me.data['email'], '')
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash(
        'Logged in as id=%s name=%s' % (me.data['id'], me.data['name']),
        'success'
    )
    return redirect(request.args.get('next'))


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('facebook_oauth_token')


@auth.route('/google-login')
def google_login():
    return google.authorize(
        callback=url_for('auth.google_authorized', _external=True))


@auth.route('/oauth2callback')
@google.authorized_handler
def google_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_oauth_token'] = (resp['access_token'], '')
    userinfo = requests.get(GOOGLE_OAUTH2_USERINFO_URL, params=dict(
        access_token=resp['access_token'],
    )).json()

    user = User.query.filter_by(username=userinfo['email']).first()
    if not user:
        user = User(userinfo['email'], '')
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash(
        'Logged in as id=%s name=%s' % (userinfo['id'], userinfo['name']),
        'success'
    )
    return redirect(url_for('auth.home'))


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_oauth_token')


@auth.route('/twitter-login')
def twitter_login():
    return twitter.authorize(
        callback=url_for(
            'auth.twitter_authorized',
            next=request.args.get('next') or request.referrer or None,
            _external=True
        ))


@auth.route('/twitter-login/authorized')
@twitter.authorized_handler
def twitter_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['twitter_oauth_token'] = resp['oauth_token'] + \
            resp['oauth_token_secret']

    user = User.query.filter_by(username=resp['screen_name']).first()
    if not user:
        user = User(resp['screen_name'], '')
        db.session.add(user)
        db.session.commit()

    login_user(user)
    flash('Logged in as twitter handle=%s' % resp['screen_name'])
    return redirect(request.args.get('next'))


@twitter.tokengetter
def get_twitter_oauth_token():
    return session.get('twitter_oauth_token')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.home'))
