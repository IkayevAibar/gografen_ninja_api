from typing import List
from datetime import datetime
from datetime import date
from ninja import Schema
from ninja.orm import create_schema
from . import models

# UserSchema = create_schema(User, depth=1, fields=['id','username','first_name','last_name', 'groups'])

UserSchema = create_schema(models.User, depth=1, fields=['id','email','phone','school_id'])
# UserCreateSchemaIn = create_schema(models.User, fields=['email','phone','password'])

class UserCreateSchemaIn(Schema):
    email: str
    phone: str
    password: str
   



UserCreateSchemaOut = create_schema(models.User, depth=1, fields=['id','email','phone','school_id'])
# UserForLessonSchema = create_schema(models.User, fields=['id'])
class UserForLessonSchema(Schema):
    id: int

UserUpdateSchemaIn = create_schema(models.User, depth=1, exclude=['password','id','school_id','groups','is_online','user_permissions','card','last_login','is_superuser','is_staff','is_active','date_joined','lead_activity','client_activity'])
SchoolCreateSchema = create_schema(models.School, exclude=['id'])
SchoolSchema = create_schema(models.School)
CourseSchema = create_schema(models.Course)
CourseForLessonSchema = create_schema(models.Course,fields=['id'])
Course_userSchema = create_schema(models.Course_user)
LessonSchema = create_schema(models.Lesson)
class VectorForCourseSchema(Schema):
    id: int

# LessonCreateSchema = create_schema(models.Lesson, exclude=['id','duration','pub_date','video'])
class LessonCreateSchema(Schema):
    title: str
    short_desc: str
    full_desc: str
    course_id: CourseForLessonSchema
    teacher_id: List[UserForLessonSchema]

class CourseCreateSchema(Schema):
    title: str
    cost: int
    short_desc: str = None
    full_desc: str = None
    end_date: str = None
    vector_id: List[VectorForCourseSchema]=None
    teacher_id: List[UserForLessonSchema]


CommentSchema = create_schema(models.Comment)
CommentSchemaIn = create_schema(models.Comment,exclude=['id','pub_date','change_date','user_id'])
ExerciseSchema = create_schema(models.Exercise)
ExerciseSchemaIn = create_schema(models.Exercise,exclude=['id','creator_id'])
Exercise_listSchema = create_schema(models.Exercise_list)
Exercise_listSchemaIn = create_schema(models.Exercise_list,exclude=['id','creator_id','pub_date'])
KnowledgeBaseSchema = create_schema(models.KnowledgeBase)
HomeWorkSchema = create_schema(models.HomeWork)
VectorSchemaIn = create_schema(models.Vector,exclude=['id','pub_date','course_count','duration','creator_id'])
VectorSchema = create_schema(models.Vector)


class KnowledgeBaseSchemaIn(Schema):
    name: str
    type_name: int
    type_id: int
 