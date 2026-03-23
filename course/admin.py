from flask import url_for, request
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from werkzeug.utils import redirect

from course import app, db, dao
from course.models import UserRole, Course, Student, User, Class, Room, Rule


class AdminAccessMixin:
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        return redirect('/admin/login')



class MyAdminHome(AdminAccessMixin, AdminIndexView):
    pass


class MyAdminModelView(AdminAccessMixin, ModelView):
    can_create = True
    can_edit = True
    can_delete = True



class UserAdmin(AdminAccessMixin, ModelView):
    column_list = ('username', 'active','role','created_date' )
    form_excluded_columns = ('student', 'created_date','role')
    column_labels = {'role':'Vai trò'}

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.password = dao.hash_password(model.password)



class StudentAdmin(AdminAccessMixin, ModelView):

    form_excluded_columns = ['registrations','created_date','user','active']
    column_labels = {
        'mssv': 'Mã số sinh viên',
        'full_name': 'Họ tên',
    }
    def after_model_change(self, form, model, is_created):
        if is_created:
            user = dao.add_user_student(student_id=model.id)
            model.user_id = user.id
            self.session.commit()


class CourseAdmin(AdminAccessMixin, ModelView):
    column_labels = {
        'course_code': 'Mã MH',
        'course_name': 'Tên MH',
        'credits': 'Số tín chỉ ',
    }

class ClassAdmin(AdminAccessMixin, ModelView):
    column_labels = {
        'class_code': 'Tên lớp',
        'room': 'Phòng',
        'schedule': 'Lịch học',
        'max_students': 'Sĩ số',
        'course': 'Môn học',
    }

class RoomAdmin(AdminAccessMixin, ModelView):
    column_labels = {

        'name': 'Tên phòng',
        'capacity': 'Chỗ ngồi sinh viên'
    }

class RuleAdmin(AdminAccessMixin, ModelView):
    form_excluded_columns = ['created_date']

    column_labels = {
        'key': 'Code',
        'name': 'Tên',
        'value': 'Giá trị',
        'description': 'Mô tả'
    }


admin = Admin(app,name='Admin',index_view=MyAdminHome(name='TRANG CHỦ'))
admin.add_view(CourseAdmin(Course, db.session,name='MÔN HỌC'))
admin.add_view(StudentAdmin(Student, db.session,name='SINH VIÊN'))
admin.add_view(UserAdmin(User, db.session,name='TÀI KHOẢN'))
admin.add_view(ClassAdmin(Class, db.session,name='LỚP'))
admin.add_view(RoomAdmin(Room, db.session,name='PHÒNG HỌC'))
admin.add_view(RuleAdmin(Rule, db.session,name='QUY ĐỊNH'))

