from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


# Custom User model

# Custom User model
class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone_number', 'first_name', 'last_name']

    def __str__(self):
        return self.username

# Student model
class Student(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    track_record = models.TextField(blank=True)  # Track record based on quiz results
    cart = models.ManyToManyField('Course', related_name='students_in_cart', blank=True)
    feedback = models.TextField(blank=True)  # Feedback on the courses
    grades = models.JSONField(default=dict)  # Store grades for quizzes, assignments, and exams
    certificate_photo = models.ImageField(upload_to='certificates/student_photos/', null=True, blank=True)


    def __str__(self):
        return self.user.username
    

    def all_assignments_graded(self, course):
        assignments = self.assignments.filter(course=course)
        return all(a.status == 'graded' for a in assignments)
    def exam_taken_and_graded(self, course):
        exam = course.exam
        return exam.status == 'graded'
    
    def calculate_final_grade(self, course):
        # Example calculation
        assignments = self.assignments.filter(course=course)
        total_assignment_grade = sum(a.grade for a in assignments if a.grade is not None)
        num_assignments = assignments.count()
        assignment_grade = total_assignment_grade / num_assignments if num_assignments > 0 else 0

        exam = course.exam
        exam_grade = self.grades.get(f"exam_{exam.id}", 0)

        quiz = course.quiz
        quiz_grade = self.grades.get(f"quiz_{quiz.id}", 0)

        final_grade = 0.5 * (assignment_grade) + 0.25 * quiz_grade + 0.25 * exam_grade
        return final_grade


# Instructor model
class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    verification_code = models.CharField(max_length=6, blank=True, null=True)


    def __str__(self):
        return f"{self.user.username} - Instructor"
    

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    
# Course model
class Course(models.Model):
    category = models.ForeignKey(Category, related_name='courses', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField()
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)


    def __str__(self):
        return self.title

    def clean(self):
        if self.lessons.count() >= 10:
            raise ValidationError('A course cannot have more than 10 lessons.')


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Lesson(models.Model):
    course = models.OneToOneField(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    video = models.FileField(upload_to='lesson_videos/')
    ppt_file = models.FileField(upload_to='lesson_ppt_files/')

    def __str__(self):
        return f"{self.title} - {self.course.title}"

    def save(self, *args, **kwargs):
        self.course.clean()  # Validate the course before saving the lesson
        super().save(*args, **kwargs)
# Enrollment model
class Enrollment(models.Model):
    student = models.ForeignKey(Student, related_name='enrollments', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='enrollments', on_delete=models.CASCADE)
    date_enrolled = models.DateTimeField(auto_now_add=True)
    is_in_cart = models.BooleanField(default=True)  # indicates if the course is in the cart or purchased

    def __str__(self):
        return f"{self.student.user.username} enrolled in {self.course.title}"

# Quiz model

class Quiz(models.Model):
    Lesson = models.OneToOneField('Lesson', related_name='quiz', on_delete=models.CASCADE)

    def __str__(self):
        return f"Quiz for {self.Lesson.title}"

from django.db import models

class Question(models.Model):
    CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ]

    quiz = models.ForeignKey('Quiz', related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    choice_a = models.CharField(max_length=255)
    choice_b = models.CharField(max_length=255)
    choice_c = models.CharField(max_length=255)
    choice_d = models.CharField(max_length=255)
    correct_choice = models.CharField(max_length=1, choices=CHOICES)

    def __str__(self):
        return f"Question: {self.text}"

    


# QuizResult model
class QuizResult(models.Model):
    student = models.ForeignKey(Student, related_name='quiz_results', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, related_name='quiz_results', on_delete=models.CASCADE)
    score = models.IntegerField()

    def __str__(self):
        return f"{self.student.user.username} - {self.quiz.title} - Score: {self.score}"

# Assignment model
class Assignment(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
        ('pending', 'Pending'),
    ]
    student = models.ForeignKey('Student', related_name='assignments', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', related_name='assignments', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    submission_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='submitted')
    file = models.FileField(upload_to='assignments/')
    grade = models.FloatField(null=True, blank=True)  # To store the grade given by the instructor

    def __str__(self):
        return f"Assignment: {self.title} for {self.student.username}"


# AssignmentSubmission model
class AssignmentSubmission(models.Model):
    student = models.ForeignKey(Student, related_name='assignments', on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, related_name='submissions', on_delete=models.CASCADE)
    content = models.TextField()
    grade = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.assignment.title} - Grade: {self.grade}"


class Exam(models.Model):
    STATUS_CHOICES = [
        ('not_taken', 'Not Taken'),
        ('taken', 'Taken'),
        ('graded', 'Graded'),
    ]
    course = models.OneToOneField('Course', related_name='exam', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    exam_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='not_taken')


    def __str__(self):
        return f"Exam: {self.title} for {self.course.title}"


# Feedback model
class Feedback(models.Model):
    student = models.ForeignKey(Student, related_name='feedbacks', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='feedbacks', on_delete=models.CASCADE)
    feedback_text = models.TextField()
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.student.user.username} for {self.course.title}"

# Grade model
class Grade(models.Model):
    student = models.ForeignKey(Student, related_name='grades', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='grades', on_delete=models.CASCADE)
    final_grade = models.DecimalField(max_digits=5, decimal_places=2)  # grade as a percentage

    def __str__(self):
        return f"{self.student.user.username} - {self.course.title} - Final Grade: {self.final_grade}"


User = get_user_model()

#Payment model
class Payment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference_number = models.CharField(max_length=100, unique=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment {self.reference_number} by {self.student.username}"

#Cart model
class Cart(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    courses = models.ManyToManyField(Course, related_name='carts')

    def __str__(self):
        return f"Cart of {self.student.username}"
from django.db import models

class Certificate(models.Model):
    student = models.OneToOneField('Student', on_delete=models.CASCADE, related_name='certificate')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='certificates')
    description = models.TextField()
    student_photo = models.ImageField(upload_to='certificates/student_photos/')
    company_logo = models.ImageField(upload_to='certificates/company_logos/')
    issued_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Certificate for {self.student.user.username} in {self.course.title}"







