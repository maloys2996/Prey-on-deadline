from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, TimeField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Optional


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Подтвердите пароль', validators=[
            DataRequired(), EqualTo(
                'password', message="Пароли не совпадают")])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RoomCreationForm(FlaskForm):
    name = StringField('Название комнаты', validators=[DataRequired()])
    submit = SubmitField('Создать комнату')


class DeadlineForm(FlaskForm):
    description = StringField('Описание дедлайна', validators=[DataRequired()])
    due_date = DateField('Дата выполнения (ГГГГ-ММ-ДД)', validators=[DataRequired()], format='%Y-%m-%d')
    due_time = TimeField('Время выполнения (необязательно, ЧЧ:ММ)', format='%H:%M', validators=[Optional()])
    assigned_to = StringField('Пользователь (username)')  # Не обязательное поле
    apply_to_all = BooleanField('Назначить для всей команды')
    submit = SubmitField('Назначить дедлайн')


class AddParticipantForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    can_set_deadlines = BooleanField('Разрешить устанавливать дедлайны')
    submit = SubmitField('Добавить участника')


class MessageForm(FlaskForm):
    content = TextAreaField('Сообщение', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class ProfileForm(FlaskForm):
    about = TextAreaField('О себе', validators=[Optional()])
    avatar = FileField('Аватар', validators=[FileAllowed(['jpg', 'png', 'gif'], 'Только изображения!')])
    submit = SubmitField('Сохранить')
