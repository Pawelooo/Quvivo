from datetime import date
import os
import random
import requests, secrets
from PIL import Image
from flask import render_template, json, redirect, url_for, flash, request


from oferty import app, OTODOMParser, db, bcrypt
from oferty.models import User, Announcement, Post, Comment, Appartment
from oferty.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostFrom, AddCommentForm, \
    AddAppartmentToObservation
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/', methods=['GET', "POST"])
def home():
    if request.method == "POST":
        db.session.query(Appartment).delete()
        db.session.commit()
        city = request.form['miasto']
        if city != '':
            new_city = remove_non_ascii(city.lower())
            search_flat_from_city(new_city)

            return redirect(url_for('show_offers'))
        else:
            flash('Podaj nazwe miasta !', 'danger')
    if request.method == 'GET':
        offerts = random_offerts()
        posts = Post.query.order_by(Post.id.desc()).first()
        return render_template('base.html', offerts=offerts, posts=posts)
    return render_template('base.html')


def random_offerts():
    lista = []
    with open(f'oferty/JSON/lista_mieszkan_oto1.json', 'r') as file:
        data = json.load(file)
    if data:
        while len(lista) < 3:
            number = random.choice(list(data))
            if data[number] not in lista:
                lista.append(data[number])
    return lista


def remove_non_ascii(name_of_city):
    polish_char = {'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z'}
    for char in name_of_city:
        if char in polish_char:
            name_of_city = name_of_city.replace(char, polish_char[char])
    return name_of_city


def search_flat_from_city(miasto):
    for i in range(1, 3):
        otodom_html = requests.get(f'https://www.otodom.pl/sprzedaz/mieszkanie/{miasto}/?page={i}')
        otodom_parser = OTODOMParser.OTODOMParser(otodom_html.text)
        otodom_parser.collect_info_about_flats()
    return miasto


@app.route('/oferty_mieszkan', methods=['GET', "POST"])
def show_offers():
    time = date.today()
    appartments = Appartment.query.all()
    form = AddAppartmentToObservation()
    if request.method == "POST":
        if form.validate_on_submit():
            annoucments = Announcement(annoucements=Appartment.link, user_id=current_user)
            db.session.add(annoucments)
            db.session.commit()
            return redirect('home')
    return render_template('oferty.html', appartments=appartments, form=form, time=time)


@app.route('/register', methods=['GET', "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Twoje konto zostało stworzone! Teraz mozesz się zalogować', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Logowanie nie powiodło się. Sprawdź login i hasło', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profilowe', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Twoje konto zostało zaaktualizowe pomyślnie!', 'success')
        return redirect(url_for('account'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profilowe/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostFrom()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, autor=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Twoj post został dodany !', 'success')
        return redirect(url_for('forum'))
    return render_template('create_post.html', title='New Post', form=form)


@app.route('/forum', methods=['GET'])
def forum():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.paginate(page=page, per_page=5)
    posts_count = Post.comments
    return render_template('forum.html', posts=posts, comment_count=posts_count)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter(Comment.post_id == post_id)
    form = AddCommentForm()
    if request.method == "POST":
        if form.validate_on_submit():
            comment = Comment(text=form.text.data, post_id=post.id)
            db.session.add(comment)
            db.session.commit()
            flash('Twój komentarz został dodany do postu', "success")
            return redirect((url_for('post', post_id=post.id)))
    return render_template('post.html', title=post.title, form=form, post=post, comment=comments)


@app.route("/post/<int:post_id>/comment", methods=["GET", "POST"])
@login_required
def comment_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = AddCommentForm()
    if request.method == "POST":
        if form.validate_on_submit():
            comment = Comment(text=form.text.data, post_id=post.id)
            db.session.add(comment)
            db.session.commit()
            flash('Twój komentarz został dodany do postu', "success")
            return redirect(url_for("post", post_id=post.id))
    return render_template("comment_post.html", form=form, post_id=post_id)
