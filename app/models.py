from django.contrib.auth.base_user import BaseUserManager
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils import timezone
import datetime
from django.contrib.auth.models import AbstractUser,UserManager as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
import os
from django.core.cache import cache 
from grafen import settings
from django.contrib.auth.models import Group
from django.contrib.contenttypes.fields import GenericRelation
# from comment.models import Comment

class UserManager(BaseUserAdmin):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        school = School(sub_domen=str(user.id)+".gografen.com",school_name=str(user.id)+user.first_name,creator_id=user)
        school.save()
        user.school_id = school
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


Group.add_to_class('description', models.CharField(max_length=180,null=True, blank=True))
Group.add_to_class('school_id', models.ForeignKey('app.School',on_delete=models.SET_NULL,blank=True,null=True,help_text='Школа'))
# Group.add_to_class('creator_id', models.ForeignKey('app.User',on_delete=models.SET_NULL,blank=True,null=True,help_text='zxc'))

def content_file_name_logo(instance, filename):
    return os.path.join(str(instance.id),'logo',filename)

def content_file_name_courses(instance, filename):
    return os.path.join(str(instance.creator_id.school_id.id),'courses',str(instance.title)+"_"+str(instance.creator_id.school_id.id) ,filename)

def content_file_name_hw(instance, filename):
    return os.path.join(str(instance.student_id.school_id.id),'hw',str(instance.course_id.title),str(instance.lesson_id.id) ,filename)

def content_file_name_ex(instance, filename):
    return os.path.join(str(instance.creator_id.school_id.id),'exercise',str(instance.lesson_id.id),str(instance.id),filename)

def content_file_name_ex_list(instance, filename):
    return os.path.join(str(instance.creator_id.school_id.id),'exercise',str(instance.lesson_id.id) ,filename)

def content_file_name_knowledge(instance, filename):
    return os.path.join(str(instance.creator_id.school_id.id),'knowledgebase',str(instance.type_name),str(instance.type_id),filename)

def get_upload_path(instance, filename):
    return os.path.join(
      "knowledge","school_%d" % instance.school_id.id, "user_%d" % instance.id,filename)

# Create your models here.

class User(AbstractUser):
    username=None
    USERNAME_FIELD = 'email'
    email = models.EmailField(_('email address'),max_length=150, unique=True) # changes email to unique and blank to false
    REQUIRED_FIELDS = []
    phone=models.CharField('Телефон',max_length=15,null=True,blank=True)
    fathername = models.CharField('Отчество', max_length=150, blank=True,null=True)
    gender_CHOICES = [
        (0, 'None'),
        (1, 'Мужчина'),
        (2, 'Женщина'),
    ]
    gender = models.IntegerField('Пол',choices=gender_CHOICES,default=0)
    birth_date = models.DateField('Дата рождение',default= datetime.date.today,blank=True)
    card = models.CharField('Банковская карта',max_length=16,null=True,blank=True)
    country = models.CharField('Страна',max_length=20,default="Казахстан",null=True)
    lead_activity = models.DateTimeField('Активность лида',default=timezone.now,null=True)
    client_activity = models.DateTimeField('Активность клиента',null=True,blank=True)
    school_id = models.ForeignKey(
        'School',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Школа",)
    is_online = models.BooleanField(default=False)

    objects = UserManager()

    # USERNAME_FIELD = 'identifier'
    def has_group(user, group_name):
        return user.groups.filter(name=group_name).exists()
    def __str__(self):
        return "%d | %s" % (self.id, self.email)
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

class School(models.Model):
    school_name = models.CharField('Школа',max_length=20,null=True,blank=True,unique=True)
    sub_domen = models.CharField('Домен',max_length=30,null=True,blank=True,unique=True)
    school_logo_1 = models.FileField('Лого 250x64',upload_to=content_file_name_logo,blank=True, null=True)
    school_logo_2 = models.FileField('Лого 16x16',upload_to=content_file_name_logo,blank=True, null=True)
    creator_id = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text='Создатель школы')
    class Meta:
        verbose_name = "Школа"
        verbose_name_plural = "Школы"
    def __str__(self):
        return "%s" % (self.school_name)

class Comment(models.Model):
    user_id = models.ForeignKey('User',on_delete=models.CASCADE,blank=True,null=True,verbose_name='Комментатор')
    course_id = models.ForeignKey('Course',on_delete=models.CASCADE,blank=True,null=True,verbose_name='Курс')
    pub_date = models.DateTimeField('Дата публикации',default= timezone.now)
    change_date = models.DateTimeField('Дата изменении',blank=True,null=True)
    content = models.CharField('Контент',max_length=1500,null=True,blank=True)
    parent = models.ForeignKey(
        "self",
        verbose_name="Родительский комментарий",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )
    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
    def __str__(self):
        return "{} - {}".format(self.user_id, self.course_id)

class Course(models.Model):
    title = models.CharField('Название',max_length=150)
    cost = models.IntegerField('Стоимость',default=0,help_text='в тенге')
    poster = models.FileField('Постер',upload_to=content_file_name_courses,blank=True, null=True)
    mini_poster = models.FileField('Мини Постер',upload_to=content_file_name_courses,blank=True, null=True)
    short_desc = models.TextField('Короткое описание',max_length=2000,blank=True, null=True)
    full_desc = models.TextField('Полное описание',max_length=5000,blank=True, null=True)
    lesson_count = models.IntegerField('Количество уроков',default=0,blank=True, null=True)
    start_date = models.DateField('Начало даты',default= datetime.date.today)
    end_date = models.DateField('Конец даты',blank=True, null=True)
    duration = models.IntegerField('Длителность',default=0,help_text='в минутах',blank=True, null=True)
    pub_date = models.DateTimeField('Дата публикации',default=timezone.now)
    teacher_id = models.ManyToManyField('User',blank=True,null=True,help_text='Создатель курса')
    vector_id = models.ManyToManyField('Vector',blank=True,null=True,help_text='Направление')
    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
    # comments = GenericRelation(Comment)
    def update_num_lessons(self):
        self.lesson_count=Lesson.objects.filter(course_id=self).count()
        return self.save(update_fields=["lesson_count"])
    def update_duration(self):
        lessons = Lesson.objects.filter(course_id=self)
        c_dur = 0
        for l in lessons:
            c_dur+=l.duration
        self.duration=c_dur
        return self.save(update_fields=["duration"])
    def __str__(self):
        return "%s Price:%s tg" % (self.title, self.cost)

class Lesson(models.Model):
    title = models.CharField('Название',max_length=150)
    short_desc = models.TextField('Короткое описание',max_length=2000,blank=True, null=True)
    full_desc = models.TextField('Полное описание',max_length=5000,blank=True, null=True)
    video = models.FileField('Содержание урока',upload_to='lessons',blank=True, null=True)
    duration = models.IntegerField('Длителность',default=0,help_text='в минутах',blank=True, null=True)
    pub_date = models.DateField('Дата публикации',default= datetime.date.today,blank=True)
    course_id = models.ForeignKey('Course',on_delete=models.SET_NULL,blank=True,null=True,help_text='курс')
    teacher_id = models.ManyToManyField('User',blank=True,null=True,help_text='Учитель курса')
    # comments = GenericRelation(Comment)
    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
    def __str__(self):
        return "%s" % (self.title)

class HomeWork(models.Model):
    title = models.CharField('Название',max_length=150,default="",blank=True, null=True)
    desc = models.TextField('Короткое описание',max_length=5000,blank=True, null=True)
    pub_date = models.DateField('Дата публикации',default= datetime.date.today,blank=True)
    lesson_id = models.ForeignKey('Lesson',on_delete=models.SET_NULL,blank=True,null=True,help_text='урок')
    course_id = models.ForeignKey('Course',on_delete=models.SET_NULL,blank=True,null=True,help_text='курс')
    student_id = models.ForeignKey('User',on_delete=models.CASCADE,blank=True,null=True,help_text='Ученик курса')
    checked = models.BooleanField(_("Проверено?"),default=False,blank=True,null=True)
    grade = models.CharField(_("Оценка"),max_length=10,default="0/0",blank=True,null=True)
    class Meta:
        verbose_name = "Домашнее Задание"
        verbose_name_plural = "Домашние Задании"
    def __str__(self):
        return "%s" % (self.title)
    def __unicode__(self):
       return self.title

class Exercise(models.Model):
    title = models.CharField('Название шаблона',max_length=150,default="",blank=True, null=True)
    desc = models.TextField('Условие упражнение',max_length=200,blank=True, null=True)
    text = models.TextField('Текст для упражнения',blank=True,null=True)
    creator_id = models.ForeignKey('User',on_delete=models.CASCADE,blank=True,null=True)
    ex_id = models.ForeignKey('Exercise_list',on_delete=models.CASCADE,blank=True,null=True)
    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"


class Exercise_list(models.Model):
    title = models.CharField('Название задании',max_length=150,default="",blank=True, null=True)
    creator_id = models.ForeignKey('User',on_delete=models.CASCADE,blank=True,null=True)
    pub_date = models.DateField('Дата публикации',default=datetime.date.today,blank=True)
    lesson_id = models.ForeignKey('Lesson',on_delete=models.SET_NULL,blank=True,null=True,help_text='урок')
    class Meta:
        verbose_name = "Список Задач"
        verbose_name_plural = "Списки Задач"



class KnowledgeBase(models.Model):
    name = models.CharField('Название файла',max_length=150,blank=True,null=True)
    files = models.FileField('Файлы',upload_to=content_file_name_knowledge,blank=True, null=True)
    pub_date = models.DateField('Дата публикации',default= datetime.date.today,blank=True)
    CHOICES = [
        (0, 'None'),
        (1, 'Урок'),
        (2, 'Лист Задач'),
        (3, 'Задача'),
        (4, 'ДЗ'),
    ]
    type_name = models.IntegerField('Тип для файла',choices=CHOICES,default=0)
    type_id = models.IntegerField('ID для файла',blank=True,null=True)
    creator_id = models.ForeignKey('User',on_delete=models.CASCADE,blank=True,null=True)
    class Meta:
        verbose_name = "База Знании"
        verbose_name_plural = "Базы Знании"

class Vector(models.Model):
    title = models.CharField('Название',max_length=150)
    short_desc = models.TextField('Короткое описание',max_length=800,blank=True, null=True)
    pub_date = models.DateField('Дата публикации',default= datetime.date.today,blank=True)
    course_count = models.IntegerField('Количество курсов',default=0,blank=True, null=True)
    creator_id = models.ForeignKey('User',on_delete=models.CASCADE,blank=True,null=True,help_text='Создатель курса')
    duration = models.IntegerField('Длителность',default=0,help_text='в минутах',blank=True, null=True)
    def update_num_courses(self):
        self.course_count=Course.objects.filter(vector_id=self).count()
        return self.save(update_fields=["course_count"])
    def update_duration(self):
        cs = Course.objects.filter(vector_id=self)
        v_dur = 0
        for c in cs:
            v_dur+=c.duration
        self.duration=v_dur
        return self.save(update_fields=["duration"])
    class Meta:
        verbose_name = "Направление"
        verbose_name_plural = "Направлении"
    def __str__(self):
        return "%s" % (self.title)

class Course_user(models.Model):
    course_id = models.ForeignKey('Course',on_delete=models.CASCADE,blank=True,null=True,help_text='курс')
    student_id = models.ForeignKey('User',on_delete=models.CASCADE,blank=True,null=True,help_text='Ученик курса')
    start_date = models.DateField('Начало даты',default= datetime.date.today)
    end_date = models.DateField('Конец даты',blank=True, null=True)
    activity = models.DateTimeField('Активность клиента',null=True,blank=True)
    class Meta:
        verbose_name = "Доступ к Курсу"
        verbose_name_plural = "Доступы к Курсам"
    def __str__(self):
        return "%s|%s" % (self.student_id.username,self.course_id.title)
