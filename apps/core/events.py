from django.dispatch import Signal

# -------------------------------------------------------
# Account Events
# -------------------------------------------------------
user_registered = Signal()        # user_id

# -------------------------------------------------------
# Course Events
# -------------------------------------------------------
course_created = Signal()         # course_id, instructor_id
course_published = Signal()       # course_id, instructor_id
course_unpublished = Signal()     # course_id, instructor_id

# -------------------------------------------------------
# Enrollment Events
# -------------------------------------------------------
student_enrolled = Signal()       # enrollment_id, student_id, course_id
student_unenrolled = Signal()     # enrollment_id, student_id, course_id

# -------------------------------------------------------
# Assessment Events
# -------------------------------------------------------
assessment_submitted = Signal()   # submission_id, user_id, assessment_id
score_calculated = Signal()       # submission_id, user_id, course_id, assessment_id, score, passed

# -------------------------------------------------------
# Progress Events
# -------------------------------------------------------
lesson_completed = Signal()       # user_id, lesson_id, course_id
course_completed = Signal()       # user_id, course_id
