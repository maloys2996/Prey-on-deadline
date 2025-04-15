from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Room, RoomUser, Deadline, Message
from app.forms import (RegistrationForm, LoginForm, RoomCreationForm, DeadlineForm,
                       AddParticipantForm, MessageForm, ProfileForm)

from datetime import datetime, time

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    rooms = Room.query.all()
    return render_template('index.html', rooms=rooms)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first():
            flash('Пользователь с таким именем или email уже существует.')
            return redirect(url_for('main.register'))
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Вы успешно зарегистрированы! Пожалуйста, авторизуйтесь.')
        return redirect(url_for('main.login'))
    else:
        if request.method == 'POST':
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Ошибка в поле {getattr(form, field).label.text}: {error}")
    return render_template('register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Вы вошли в систему!')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Неверное имя пользователя или пароль.')
    return render_template('login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.')
    return redirect(url_for('main.login'))


@bp.route('/create_room', methods=['GET', 'POST'])
@login_required
def create_room():
    form = RoomCreationForm()
    if form.validate_on_submit():
        room = Room(name=form.name.data, owner=current_user)
        db.session.add(room)
        db.session.commit()
        room_user = RoomUser(room=room, user=current_user, can_set_deadlines=True)
        db.session.add(room_user)
        db.session.commit()
        flash('Комната создана!')
        return redirect(url_for('main.room_detail', room_id=room.id))
    return render_template('create_room.html', form=form)


@bp.route('/room/<int:room_id>')
@login_required
def room_detail(room_id):
    room = Room.query.get_or_404(room_id)
    deadlines = room.deadlines.order_by(Deadline.due_date.asc()).all()
    participants = [ru.user for ru in room.users]
    form = MessageForm()
    messages = room.messages.order_by(Message.timestamp.asc()).all()
    return render_template('room_detail.html', room=room, deadlines=deadlines,
                           participants=participants, form=form, messages=messages)


@bp.route('/room/<int:room_id>/set_deadline', methods=['GET', 'POST'])
@login_required
def set_deadline(room_id):
    room = Room.query.get_or_404(room_id)
    room_user = RoomUser.query.filter_by(room_id=room.id, user_id=current_user.id).first()
    if not room_user or not room_user.can_set_deadlines:
        flash('У вас нет прав для установки дедлайнов в этой комнате.')
        return redirect(url_for('main.room_detail', room_id=room.id))
    form = DeadlineForm()
    if form.validate_on_submit():
        deadline_date = form.due_date.data
        deadline_time = form.due_time.data if form.due_time.data is not None else time(0, 0)
        due_datetime = datetime.combine(deadline_date, deadline_time)
        if form.apply_to_all.data:
            deadline = Deadline(
                description=form.description.data,
                due_date=due_datetime,
                room=room,
                created_by_id=current_user.id,
                for_team=True,
                assigned_to_id=None
            )
            db.session.add(deadline)
            db.session.commit()
            flash('Дедлайн установлен для всей команды.')
            return redirect(url_for('main.room_detail', room_id=room.id))
        else:
            if not form.assigned_to.data:
                flash('Пожалуйста, укажите имя пользователя или выберите назначение для всей команды.')
            else:
                assigned_user = User.query.filter_by(username=form.assigned_to.data).first()
                if not assigned_user:
                    flash('Пользователь не найден.')
                else:
                    deadline = Deadline(
                        description=form.description.data,
                        due_date=due_datetime,
                        room=room,
                        assigned_to_id=assigned_user.id,
                        created_by_id=current_user.id,
                        for_team=False
                    )
                    db.session.add(deadline)
                    db.session.commit()
                    flash('Дедлайн установлен для пользователя.')
                    return redirect(url_for('main.room_detail', room_id=room.id))
    return render_template('set_deadline.html', form=form, room=room)


@bp.route('/room/<int:room_id>/add_participant', methods=['GET', 'POST'])
@login_required
def add_participant(room_id):
    room = Room.query.get_or_404(room_id)
    if room.owner != current_user:
        flash('Только владелец комнаты может добавлять участников.')
        return redirect(url_for('main.room_detail', room_id=room.id))

    form = AddParticipantForm()
    if form.validate_on_submit():
        participant = User.query.filter_by(username=form.username.data).first()
        if not participant:
            flash('Пользователь не найден.')
        else:
            existing = RoomUser.query.filter_by(room_id=room.id, user_id=participant.id).first()
            if existing:
                flash('Пользователь уже является участником комнаты.')
            else:
                room_user = RoomUser(room=room, user=participant, can_set_deadlines=form.can_set_deadlines.data)
                db.session.add(room_user)
                db.session.commit()
                flash('Участник добавлен.')
                return redirect(url_for('main.room_detail', room_id=room.id))
    return render_template('add_participant.html', form=form, room=room)


@bp.route('/room/<int:room_id>/chat', methods=['POST'])
@login_required
def post_message(room_id):
    room = Room.query.get_or_404(room_id)
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(room=room, sender_id=current_user.id, content=form.content.data)
        db.session.add(message)
        db.session.commit()
    return redirect(url_for('main.room_detail', room_id=room.id))


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.about = form.about.data
        if form.avatar.data:
            filename = secure_filename(form.avatar.data.filename)
            avatar_path = 'app/static/uploads/' + filename
            form.avatar.data.save(avatar_path)
            current_user.avatar = 'uploads/' + filename  # Относительный путь из папки static
        db.session.commit()
        flash("Профиль обновлен.")
        return redirect(url_for('main.profile'))
    form.about.data = current_user.about
    return render_template('profile.html', form=form)


@bp.route('/user/<int:user_id>')
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_profile.html', user=user)
