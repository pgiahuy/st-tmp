from flask import url_for, request
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.fields import InlineModelFormList, QuerySelectMultipleField
from flask_admin.form import DatePickerWidget
from flask_login import current_user
from werkzeug.utils import redirect
from wtforms.fields.datetime import DateField
from wtforms.validators import ValidationError

import course.utils
from course import app, db, dao, utils
from course.models import UserRole, Course, Student, User, CourseClass, Room, SystemConfig, Registration, Semester, \
    ScheduleSlot, CourseClassSchedule


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

    def create_model(self, form):
        try:
            utils.add_student_with_user(
                mssv=form.mssv.data,
                full_name=form.full_name.data,
                email=form.email.data
            )
            return True
        except Exception as e:
            print("Error:", e)
            return False


class CourseAdmin(AdminAccessMixin, ModelView):

    column_labels = {
        'course_code': 'Mã MH',
        'course_name': 'Tên MH',
        'credits': 'Số tín chỉ ',
    }



class CourseClassAdmin(AdminAccessMixin, ModelView):
    column_list = (
        'class_code',
        'course',
        'room',
        'max_students',
        'schedule_associations',
        'semester'
    )

    column_labels = {
        'class_code': 'Mã lớp',
        'course': 'Môn học',
        'room': 'Phòng học',
        'max_students': 'Sĩ số tối đa',
        'schedule_associations': 'Lịch học'
    }

    column_formatters = {

        'schedule_associations': lambda v, c, m, p: ", ".join([
        f"{a.slot.weekday.value} - {a.slot.session.value}"
        for a in m.schedule_associations if a.slot
    ]) if m.schedule_associations else "Chưa xếp lịch",

        'course': lambda v, c, m, p: f"{m.course.course_code} - {m.course.course_name}" if m.course else "N/A"
    }

    form_args = {
        'course': {
            'label': 'Môn học',
            'query_factory': lambda: Course.query.all(),
            'get_label': lambda c: f"{c.course_code} - {c.course_name}"
        },

    }

    form_excluded_columns = ('schedule_associations','registrations','created_date')

    form_extra_fields = {
        'slots_picker': QuerySelectMultipleField(
            'Chọn Lịch Học',
            query_factory=lambda: ScheduleSlot.query.all(),
            get_label=lambda s: f"{s.weekday.value} - {s.session.value}"
        )
    }




    column_searchable_list = ['class_code']
    column_filters = ['room.name', 'course.course_name', 'semester']

    def on_model_change(self, form, model, is_created):

        selected_slots = form.slots_picker.data
        room = form.room.data

        if not selected_slots or not room:
            return

        slot_ids = [s.id for s in selected_slots]
        room_id = room.id
        current_class_id = model.id if not is_created else None

        conflict = dao.check_schedule_conflict(
            db.session,
            room_id,
            slot_ids,
            current_class_id
        )

        if conflict:
            other_class = conflict.class_code

            conflicting_slot = None
            for assoc in conflict.schedule_associations:
                if assoc.slot.id in slot_ids:
                    conflicting_slot = assoc.slot
                    break

            if conflicting_slot:
                time_info = f"{conflicting_slot.weekday.value} ({conflicting_slot.session.label})"
            else:
                time_info = "không xác định"

            raise ValidationError(
                f"Trùng lịch: Phòng {room.name} đã được sử dụng bởi lớp '{other_class}' "
                f"vào {time_info}. Vui lòng kiểm tra lại!"
            )

        model.schedule_associations = [
            CourseClassSchedule(slot=s) for s in selected_slots
        ]
    def on_model_delete(self, model):

        count = db.session.query(Registration).filter_by(course_class_id=model.id).count()
        if count > 0:
            raise ValidationError(f"Không thể xóa, lớp đã có {count} sinh viên đăng ký!")




class ScheduleSlotAdmin(AdminAccessMixin, ModelView):
    pass

class RegistrationAdmin(AdminAccessMixin, ModelView):
    pass


class SemesterAdmin(AdminAccessMixin, ModelView):
    column_list = ('id', 'name', 'year', 'start_date', 'start_registration_date', 'end_registration_date','end_date')

    column_searchable_list = ('name', 'year')

    column_sortable_list = ('id', 'name', 'year')

    form_overrides = {
        'start_date': DateField,
        'start_registration_date': DateField,
        'registration_deadline': DateField,
        'end_registration_date': DateField,
        'end_date': DateField
    }
    form_args = {
        'start_date': {'widget': DatePickerWidget()},
        'start_registration_date': {'widget': DatePickerWidget()},
        'end_registration_date': {'widget': DatePickerWidget()},
        'end_date': {'widget': DatePickerWidget()}
    }

    form_excluded_columns = ('created_date', 'registrations')


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
admin.add_view(CourseClassAdmin(CourseClass, db.session,name='LỚP'))
admin.add_view(RegistrationAdmin(Registration, db.session,name='ĐĂNG KÝ'))
admin.add_view(ScheduleSlotAdmin(ScheduleSlot, db.session,name='BUỔI HỌC'))

admin.add_view(SemesterAdmin(Semester, db.session,name='HỌC KỲ'))
admin.add_view(RoomAdmin(Room, db.session,name='PHÒNG HỌC'))
admin.add_view(RuleAdmin(SystemConfig, db.session,name='QUY ĐỊNH'))

