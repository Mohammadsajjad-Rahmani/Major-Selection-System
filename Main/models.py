from django.db import models


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    practical_interest = models.IntegerField(default=0)  # علاقه عملی
    analytical_interest = models.IntegerField(default=0)  # علاقه تحلیلی
    artistic_interest = models.IntegerField(default=0)  # علاقه هنری
    social_interest = models.IntegerField(default=0)  # علاقه اجتماعی
    enterprising_interest = models.IntegerField(default=0)  # علاقه مدیریتی
    conventional_interest = models.IntegerField(default=0)  # علاقه سازمان‌دهی

    def __str__(self):
        return self.name


class FieldOfStudy(models.Model):
    name = models.CharField(max_length=100)  # نام رشته
    description = models.TextField()  # توضیحات رشته
    skills_required = models.TextField(default="")  # مهارت‌های موردنیاز
    career_paths = models.TextField(default="")  # مسیرهای شغلی مرتبط
    example_subjects = models.TextField(default="")  # مثال‌هایی از موضوعات این رشته
    difficulty_level = models.CharField(
        max_length=15, choices=[("Easy", "Easy"), ("Moderate", "Moderate"), ("Challenging", "Challenging")], default="Moderate"
    )  # سطح دشواری

    # Minimum interest levels for all categories
    min_practical_interest = models.IntegerField(default=0)
    min_analytical_interest = models.IntegerField(default=0)
    min_artistic_interest = models.IntegerField(default=0)
    min_social_interest = models.IntegerField(default=0)
    min_enterprising_interest = models.IntegerField(default=0)
    min_conventional_interest = models.IntegerField(default=0)
    min_scientific_interest = models.IntegerField(default=0)  # New scientific interest
    min_technical_interest = models.IntegerField(default=0)  # New technical interest

    def __str__(self):
        return self.name

class TestQuestion(models.Model):
    question_text = models.TextField()  # متن سوال
    interest_type = models.CharField(
        max_length=50,
        choices=[
            ('practical', 'Practical Interest'),
            ('analytical', 'Analytical Interest'),
            ('artistic', 'Artistic Interest'),
            ('social', 'Social Interest'),
            ('enterprising', 'Enterprising Interest'),
            ('conventional', 'Conventional Interest'),
            ('scientific', 'Scientific Interest'),  # علاقه علمی
            ('technical', 'Technical Interest'),  # علاقه فنی
        ]
    )
    weight = models.IntegerField(default=1)  # وزن هر سوال

    def __str__(self):
        return self.question_text
