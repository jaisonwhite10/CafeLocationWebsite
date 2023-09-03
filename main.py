from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, AnonymousUserMixin, login_user, LoginManager, current_user, logout_user
from forms import CafeForm, RegisterForm, LoginForm, CommentForm
from functools import wraps
from flask_gravatar import Gravatar


app = Flask(__name__)
app.config['SECRET_KEY'] = 'CafeWebsiteProject'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager(app)
gravatar = Gravatar(app)


@login_manager.user_loader
def load_user(user_id):
    return (User.query.filter_by(id=user_id).first())


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    cafes = db.relationship('Cafe', back_populates='author')
    comments = db.relationship('Comment', back_populates='comment_author')


class Cafe(db.Model):
    __tablename__ = 'cafes'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship('User', back_populates='cafes')
    comments = db.relationship('Comment', back_populates='cafe')
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment_author = db.relationship('User', back_populates='comments')
    text = db.Column(db.Text)
    date = db.Column(db.String(250), nullable=False)

    cafe = db.relationship('Cafe', back_populates='comments')
    cafe_id = db.Column(db.Integer, db.ForeignKey('cafes.id'))


with app.app_context():
    db.create_all()


def admin_only(function):
    @wraps(function)
    def check_user_id(*args, **kwargs):
        if current_user.is_authenitcated and current_user.id == 1:
            return function(*args, **kwargs)
        else:
            return abort(403)

    return check_user_id


def click():
    print('ok')


@app.route('/', methods=['GET','POST'])
def get_all_cafes():
    global new_filter
    global filter_list


    new_filter = request.args.get("new_filter", type=str)
    filter_list = request.args.getlist("filter_list", type=str)
    page = request.args.get('page',1,type=int)

    # print(new_filter)
    print(filter_list)
    print(request.form.get('search'))
    if current_user.is_authenticated and current_user.id == 1:
        admin = True
    else:
        admin = False



    if not filter_list:
        cafes = Cafe.query.all()
        pagination = Cafe.query.paginate(page=page,per_page=3)

    filter_labels = ['has seats', 'has toilet', 'has wifi', 'has sockets', 'can take calls']
    filter_dict = {'seats': 'has seats', 'has_toilet': 'has toilet', 'has_wifi': 'has wifi',
                   'has_sockets': 'has sockets',
                   'can_take_calls': 'can take calls'}
    for item in filter_dict:
        # print(item)
        # print(filter_dict[item])

        if filter_dict[item] in filter_list:
            print('ok')
            print(item)
            kwargs = {item: 'Yes'}
            cafes = Cafe.query.filter_by(**kwargs)
            pagination = cafes.paginate(page=1,per_page=2)
    if request.method == 'POST':
        cafe_search_name = request.form.get('searchbar')
        print(cafe_search_name)
        cafes = Cafe.query.filter_by(name=cafe_search_name)

    return render_template('index6.html', cafes=cafes, filter_labels=filter_labels, new_filter=new_filter,
                           logged_in=current_user.is_authenticated, filter_list=filter_list,pagination=pagination)


@app.route("/cafe/<int:cafe_id>", methods=['GET', 'POST'])
def show_cafe(cafe_id):

    form = CommentForm()
    requested_cafe = Cafe.query.get(cafe_id)
    comment_box = None


    if current_user.is_authenticated and current_user.id == 1:
        admin = True
    else:
        admin = False


    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('You need to login or register to comment.')
            return redirect(url_for('login'))
        else:
            new_comment = Comment(author_id=current_user.id, text=request.form.get('body'), cafe_id=requested_cafe.id,
                                  date=date.today().strftime("%B %d, %Y")
                                  )

            with app.app_context():
                db.session.add(new_comment)
                db.session.commit()
            return redirect(url_for('get_all_cafes'))
    return render_template("show_cafe.html", cafe=requested_cafe, form=form, admin=admin,comment_box=comment_box)


@app.route("/edit-cafe/<int:cafe_id>")
@admin_only
def edit_cafe(cafe_id):
    cafe = Cafe.query.filter_by(id=cafe_id).first()
    edit_form = CafeForm(name=cafe.name, map_url=cafe.map_url,
                         img_url=cafe.img_url,
                         location=cafe.location,
                         seats=cafe.seats,
                         has_toilet=cafe.has_toilet,
                         has_wifi=cafe.has_wifi,
                         has_sockets=cafe.has_sockets,
                         can_take_calls=cafe.can_take_calls,
                         coffee_price = cafe.coffee_price
                         )
    if edit_form.validate_on_submit():
        cafe.name = edit_form.name.data
        cafe.map_url = edit_form.map_url.data
        cafe.img_url = edit_form.img_url.data
        cafe.location = edit_form.location.data
        cafe.seats = edit_form.seats.data
        cafe.has_toilet = edit_form.has_toilet.data
        cafe.has_wifi = edit_form.has_wifi.data
        cafe.has_sockets = edit_form.has_sockets.data
        cafe.can_take_calls = edit_form.can_take_calls
        db.session.commit()
        return redirect(url_for("show_cafe", cafe_id=cafe.id))

    return render_template("show_cafe.html", form=edit_form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    user = User.query.filter_by(email=request.form.get('email')).first()
    if request.method == 'POST':
        if user:
            flash('User already exists please log in!')
            return redirect(url_for('login'))
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=10)
        with app.app_context():
            new_user = User(name=name, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            user = User.query.filter_by(password=hashed_password).first()
            login_user(user)
            return redirect(url_for('get_all_cafes'))
    return render_template('register.html', form=form, logged_in=current_user.is_authenticated)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('That email does not exist. Please try again!')
        elif not check_password_hash(user.password, password):
            flash('Password incorrect. Please try again!')
        else:
            login_user(user)
            return redirect(url_for('get_all_cafes'))

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_cafes'))


@app.route('/suggest_place', methods=['GET', 'POST'])
def suggest_place():
    form = CafeForm()
    # if current_user.is_authenticated and request.method == 'POST':
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name')
        map_url = request.form.get('map_url')
        img_url = request.form.get('img_url')
        location = request.form.get('location')
        seats = request.form.get('seats')
        has_toilet = bool(request.form.get('has_toilet'))
        has_wifi = bool(request.form.get('has_wifi'))
        has_sockets = bool(request.form.get('has_sockets'))
        can_take_calls = bool(request.form.get('can_take_calls'))
        coffee_price = request.form.get('coffee_price')
        new_cafe = Cafe(name=name, map_url=map_url, img_url=img_url, location=location, seats=seats,
                        has_toilet=has_toilet,
                        has_wifi=has_wifi, has_sockets=has_sockets, can_take_calls=can_take_calls,coffee_price=coffee_price
                        )
        with app.app_context():
            db.session.add(new_cafe)
            db.session.commit()
        return redirect(url_for('get_all_cafes'))
    return render_template('suggest_place.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
