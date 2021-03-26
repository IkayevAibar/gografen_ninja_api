from ninja import errors
from ninja.params import Form
from grafen import settings
from . import models, schemas
from auth.jwt import AuthBearer
from .tokens import account_activation_token

from typing import List

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.template.loader import render_to_string

from ninja import Router, File
from ninja.files import UploadedFile
from ninja.renderers import BaseRenderer
from ninja.errors import ValidationError
from ninja.errors import HttpError

import random
# Create your views here.


app = Router()

# USER

@app.get('/auth_user',auth=AuthBearer(),response=schemas.UserCreateSchemaOut)
def get_auth(request):
    return request.auth, request.get_host()

@app.post("/user", response=schemas.UserCreateSchemaOut, tags=["users"])
def create_user(request , data: schemas.UserCreateSchemaIn):
    user = models.User(email=data.email,phone = data.phone,is_active=False) # User is django auth.User
    user.set_password(data.password)
    try:
        # user.save()
        mail_subject = 'Activate your account.'
        message = render_to_string('acc_active_email.html', {
            'user': user,
            'domain': request.get_host(),
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
        })
        # email = EmailMessage(mail_subject, message, to=[user.email])
        # email.send()
        send_mail(
            mail_subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
    except:
        raise HttpError(422, "Введены неправильные данные(email,password) или существует такая же почта!!!")
    school = models.School(sub_domen=str(user.id)+".gografen.com",school_name=str(user.id)+"gografen"+str(random.randint(1,10000)),creator_id=user)
    # school.save()
    user.school_id = school
    # user.save(update_fields=['school_id'])
    
    return "user"

@app.post("/s_user", response=schemas.UserCreateSchemaOut, tags=["users"])
def create_simple_user(request , data: schemas.UserCreateSchemaIn):
    user = models.User(email=data.email,phone = data.phone,is_active=False)
    user.set_password(data.password)
    
    try:
        user.school_id = request.auth.school_id
        user.save()
        mail_subject = 'Activate your account.'
        message = render_to_string('acc_active_email.html', {
            'user': user,
            'domain': request.get_host(),
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
        })
        print(message)
        # email = EmailMessage(
        #             mail_subject, message, to=[user.email]
        # )
        # email.send()
        send_mail(
            mail_subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
    except:
        raise HttpError(422, "Введены неправильные данные(email,password) или существует такая же почта!!!")
    return user


@app.get('/users', response=List[schemas.UserSchema], tags=["users"])
def get_users(request):
    return models.User.objects.all().exclude(id=1)

@app.get('/users_by_school/{school_id}', response=List[schemas.UserSchema], tags=["users"],auth=AuthBearer())
def get_users_by_school(request,school_id: int):
    return models.User.objects.filter(school_id=school_id).exclude(id=1)

@app.put("/users/{user_id}", tags=["users"])
def update_user(request, user_id: int, payload: schemas.UserUpdateSchemaIn):
    user = get_object_or_404(models.User, id=user_id)
    list_ = []
    for attr, value in payload.dict().items():
        setattr(user, attr, value)
        list_.append(attr)
    user.save(update_fields=list_)
    return {"success": True}

@app.delete("/users/{user_id}", tags=["users"])
def delete_user(request, user_id: int):
    if(user_id==1):
        raise HttpError(422, "Невозможно удалить модератора!")
    user = get_object_or_404(models.User, id=user_id)
    school = models.School.objects.filter(creator_id=user.id).first()
    if(school):
        school.delete()
    user.delete()
    return {"success": True}

# SCHOOL

@app.get('/schools', response=List[schemas.SchoolSchema], tags=["schools"],auth=AuthBearer())
def get_schools(request):
    return models.School.objects.all()

@app.get('/school/{school_id}', response=schemas.SchoolSchema, tags=["schools"])
def get_school(request,school_id: int):
    return get_object_or_404(models.School,id=school_id)


@app.post("/schools", response=schemas.SchoolSchema, tags=["schools"])
def create_school(request , data: schemas.SchoolCreateSchema):
    user = get_object_or_404(models.User, id=data.creator_id)
    school = models.School.objects.create(creator_id=user,school_name=data.school_name,sub_domen=data.sub_domen,school_logo_1=data.school_logo_1,school_logo_2=data.school_logo_2) 
    try:
        school.save()
    except:
        raise HttpError(422, "Введены неправильные данные!!!")
    user.school_id = school;
    user.save(update_fields=['school_id'])
    return school

@app.delete("/schools/{school_id}", tags=["schools"])
def delete_school(request, school_id: int):
    school = get_object_or_404(models.School, id=school_id)
    school.delete()
    return {"success": True}

@app.put("/schools/{school_id}", tags=["schools"])
def update_school(request, school_id: int, payload: schemas.SchoolCreateSchema):
    school = get_object_or_404(models.School, id=school_id)
    for attr, value in payload.dict().items():
        if(attr=="creator_id"):
            school.creator_id = get_object_or_404(models.User, id=value)
        else:
            setattr(school, attr, value)
    school.save()
    return {"success": True}

#COURSE

@app.get('/courses', response=List[schemas.CourseSchema], tags=["courses"])
def get_courses(request):
    '''
    (READ)Request to get all courses.
    '''
    return models.Course.objects.all()

@app.get('/course/{course_id}', response=schemas.CourseSchema, tags=["courses"])
def get_course(request,course_id:int):
    return get_object_or_404(models.Course,id=course_id)


@app.post("/course", response=schemas.CourseSchema, tags=["courses"])
def create_course(request , data: schemas.CourseCreateSchema):#
    try:
        # lesson = models.Lesson.objects.create(**data.dict())
        course = models.Course.objects.create(title=data.title,cost=data.cost,short_desc=data.short_desc,full_desc=data.full_desc,end_date=data.end_date)
        for i in data.vector_id:
            course.vector_id.add(models.Vector.objects.filter(id=i.id).first())
        for i in data.teacher_id:
            course.teacher_id.add(models.User.objects.filter(id=i.id).first())
        course.save()
    except:
        raise HttpError(422, "Введены неправильные данные!!!")
    
    return course

@app.delete("/courses/{course_id}", tags=["courses"])
def delete_course(request, course_id: int):
    course = get_object_or_404(models.Course, id=course_id)
    course.delete()
    return {"success": True}

@app.put("/courses/{course_id}", tags=["courses"])
def update_course(request, course_id: int, payload: schemas.CourseCreateSchema):
    course = get_object_or_404(models.Course, id=course_id)
    list_=[]
    for attr, value in payload.dict().items():
        
        if(attr=="vector_id"):
            course.vector_id.clear()
            if(value):
                for i in value:
                    print(i.get('id'))
                    course.vector_id.add(models.Vector.objects.filter(id=i.get('id')).first())
        elif(attr=="teacher_id"):
            course.teacher_id.clear()
            if(value):
                for i in value:
                    course.teacher_id.add(models.User.objects.filter(id=i.get('id')).first())
        else:
            list_.append(attr)
            setattr(course, attr, value)
    course.save(update_fields=list_)
    return {"success": True}

#LESSON
@app.get('/lessons', response=List[schemas.LessonSchema], tags=["lessons"])
def get_lessons(request):
    return models.Lesson.objects.all()

@app.get('/lesson/{lesson_id}', response=schemas.LessonSchema, tags=["lessons"])
def get_lesson(request,lesson_id:int):
    return get_object_or_404(models.Lesson,id=lesson_id)

@app.post("/lesson", response=schemas.LessonSchema, tags=["lessons"])
def create_lesson(request , data: schemas.LessonCreateSchema):#
    try:
        # lesson = models.Lesson.objects.create(**data.dict())
        lesson = models.Lesson.objects.create(title=data.title,short_desc=data.short_desc,full_desc=data.full_desc,course_id=models.Course.objects.filter(id=data.course_id.id).first())
        
        for i in data.teacher_id:
            lesson.teacher_id.add(models.User.objects.filter(id=i.id).first())
        lesson.save()
    except:
        raise HttpError(422, "Введены неправильные данные!!!")
    
    return lesson

@app.delete("/lessons/{lesson_id}", tags=["lessons"])
def delete_lesson(request, lesson_id: int):
    lesson = get_object_or_404(models.Lesson, id=lesson_id)
    lesson.delete()
    return {"success": True}

@app.put("/lessons/{lesson_id}", tags=["lessons"])
def update_lesson(request, lesson_id: int, payload: schemas.LessonCreateSchema):
    lesson = get_object_or_404(models.Lesson, id=lesson_id)
    list_=[]
    for attr, value in payload.dict().items():
        if(attr=="course_id"):
            list_.append(attr)
            if(value):
                lesson.course_id=get_object_or_404(models.Course,id=value.get('id'))
        elif(attr=="teacher_id"):
            lesson.teacher_id.clear()
            if(value):
                for i in value:
                    lesson.teacher_id.add(models.User.objects.filter(id=i.get('id')).first())
        else:
            list_.append(attr)
            setattr(lesson, attr, value)
    lesson.save(update_fields=list_)
    return {"success": True}

#KnowladgeBase
@app.post("/kb/{type_name}/{type_id}",response=List[schemas.KnowledgeBaseSchema], tags=["knowladgebase"])
def create_knowladge_base(request, type_name: int,type_id:int,files: List[UploadedFile] = File(...)):
    list_ = []
    for f in files:
        kb = models.KnowledgeBase(name=f.name,files=f,type_name=type_name,type_id=type_id,creator_id=models.User.objects.filter(id=request.auth.id).first())
        kb.save()
        list_.append(kb)
    return list_


@app.get('/kbs', response=List[schemas.KnowledgeBaseSchema], tags=["knowladgebase"])
def get_knowladge_bases(request):
    return models.KnowledgeBase.objects.all()

@app.get('/kb/{type_name}/{type_id}', response=List[schemas.KnowledgeBaseSchema], tags=["knowladgebase"])
def get_knowladge_base(request, type_name: int,type_id:int):
    return models.KnowledgeBase.objects.filter(type_name=type_name,type_id=type_id)

@app.put("/kb/{kb_id}", tags=["knowladgebase"])
def update_knowladge_base(request, kb_id: int, payload: schemas.KnowledgeBaseSchemaIn):
    kb = get_object_or_404(models.KnowledgeBase, id=kb_id)
    for attr, value in payload.dict().items():
        setattr(kb, attr, value)
    kb.save()
    return {"success": True}

@app.delete("/kb/{kb_id}", tags=["knowladgebase"])
def delete_knowladge_base(request, kb_id: int):
    kb = get_object_or_404(models.KnowledgeBase, id=kb_id)
    kb.delete()
    return {"success": True}

#COMMENT
@app.post("/comment", response=schemas.CommentSchema, tags=["comments"],auth=AuthBearer())
def create_comment(request , data: schemas.CommentSchemaIn):
    # user = get_object_or_404(models.User, id=data.user_id)
    comment = models.Comment.objects.create(user_id=request.auth,course_id=models.Course.objects.filter(id=data.course_id).first(),content=data.content) 
    try:
        comment.save()
    except:
        raise HttpError(422, "Введены неправильные данные!!!")
    return comment

@app.get('/comments', response=List[schemas.CommentSchema], tags=["comments"])
def get_comments(request):
    return models.Comment.objects.all()

@app.get('/comment/{comment_id}', response=schemas.CommentSchema, tags=["comments"])
def get_comment(request,comment_id:int):
    return get_object_or_404(models.Comment,id=comment_id)

@app.put("/comment/{comment_id}", tags=["comments"])
def update_comment(request, comment_id: int, payload: schemas.CommentSchemaIn):
    comment = get_object_or_404(models.Comment, id=comment_id)
    for attr, value in payload.dict().items():
        if(attr=="course_id"):
            comment.course_id=models.Course.objects.filter(id=value).first()
        else:
            setattr(comment, attr, value)
    comment.save()
    return {"success": True}

@app.delete("/comment/{comment_id}", tags=["comments"])
def delete_comment(request, comment_id: int):
    comment = get_object_or_404(models.Comment, id=comment_id)
    comment.delete()
    return {"success": True}

#EXERCISE
@app.post("/exercise", response=schemas.ExerciseSchema, tags=["exercises"],auth=AuthBearer())
def create_exercise(request , data: schemas.ExerciseSchemaIn):
    exercise = models.Exercise.objects.create(creator_id=request.auth,ex_id=models.Exercise_list.objects.filter(id=data.ex_id).first(),text=data.text,desc=data.desc,title=data.title) 
    try:
        exercise.save()
    except:
        raise HttpError(422, "Введены неправильные данные!!!")
    return exercise


@app.get('/exercises', response=List[schemas.ExerciseSchema], tags=["exercises"])
def get_exercises(request):
    return models.Exercise.objects.all()

@app.get('/exercise/{exercise_id}', response=schemas.ExerciseSchema, tags=["exercises"])
def get_exercise(request,exercise_id:int):
    return get_object_or_404(models.Exercise,id=exercise_id)

@app.put("/exercise/{exercise_id}", tags=["exercises"])
def update_exercise(request, exercise_id: int, payload: schemas.ExerciseSchemaIn):
    exercise = get_object_or_404(models.Exercise, id=exercise_id)
    for attr, value in payload.dict().items():
        if(attr=="ex_id"):
            exercise.ex_id=models.Exercise_list.objects.filter(id=value).first()
        else:
            setattr(exercise, attr, value)
    exercise.save()
    return {"success": True}


@app.delete("/exercise/{exercise_id}", tags=["exercises"])
def delete_exercise_list(request, exercise_id: int):
    exercise = get_object_or_404(models.Exercise, id=exercise_id)
    exercise.delete()
    return {"success": True}

#Exercise_list
@app.post("/exercise_list", response=schemas.Exercise_listSchema, tags=["exercise_lists"],auth=AuthBearer())
def create_exercise_list(request , data: schemas.Exercise_listSchemaIn):
    ex_list = models.Exercise.objects.create(creator_id=request.auth,lesson_id=models.Lesson.objects.filter(id=data.lesson_id).first(),title=data.title) 
    try:
        ex_list.save()
    except:
        raise HttpError(422, "Введены неправильные данные!!!")
    return ex_list


@app.get('/exercise_lists', response=List[schemas.Exercise_listSchema], tags=["exercise_lists"])
def get_exercise_lists(request):
    return models.Exercise_list.objects.all()

@app.get('/exercise_list/{ex_id}', response=schemas.Exercise_listSchema, tags=["exercise_lists"])
def get_exercise_list(request,ex_id:int):
    return get_object_or_404(models.Exercise_list,id=ex_id)

@app.put("/exercise_list/{ex_id}", tags=["exercise_lists"])
def update_exercise_list(request, ex_id: int, payload: schemas.Exercise_listSchemaIn):
    exercise = get_object_or_404(models.Exercise_list, id=ex_id)
    for attr, value in payload.dict().items():
        if(attr=="lesson_id"):
            exercise.lesson_id=models.Lesson.objects.filter(id=value).first()
        else:
            setattr(exercise, attr, value)
    exercise.save()
    return {"success": True}

@app.delete("/exercise_list/{ex_id}", tags=["exercise_lists"])
def delete_exercise(request, ex_id: int):
    exercise = get_object_or_404(models.Exercise_list, id=ex_id)
    exercise.delete()
    return {"success": True}
#Vector
@app.post("/vector", response=schemas.VectorSchema, tags=["vectors"],auth=AuthBearer())
def create_vector(request , data: schemas.VectorSchemaIn):
    vector = models.Vector.objects.create(creator_id=request.auth,**data.dict()) 
    try:
        vector.save()
    except:
        raise HttpError(422, "Введены неправильные данные!!!")
    return vector


@app.get('/vectors', response=List[schemas.VectorSchema], tags=["vectors"])
def get_vectors(request):
    return models.Vector.objects.all()

@app.get('/vector/{vector_id}', response=schemas.VectorSchema, tags=["vectors"])
def get_vector(request,vector_id:int):
    return get_object_or_404(models.Vector,id=vector_id)

@app.put("/vector/{vector_id}", tags=["vectors"])
def update_vector(request, vector_id: int, payload: schemas.VectorSchemaIn):
    vector = get_object_or_404(models.Vector, id=vector_id)
    for attr, value in payload.dict().items():
        setattr(vector, attr, value)
    vector.save()
    return {"success": True}

@app.delete("/vector/{vector_id}", tags=["vectors"])
def delete_vector(request, vector_id: int):
    vector = get_object_or_404(models.Vector, id=vector_id)
    vector.delete()
    return {"success": True}


#Course_User
