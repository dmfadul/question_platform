import uuid
from django.db import models


class Teacher(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Collection(models.Model):
    title = models.CharField(max_length=255)
    instructions = models.TextField(blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def career(self):
        # NEXT VERSION: This should be a ForeignKey to a Career model,
        # but for now we just return the first 3 letters of the title.
        return self.title[:3].upper()

    def __str__(self):
        return self.title


class Discipline(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Invitation(models.Model):
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name='invitations'
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.PROTECT,
        related_name='invitations'
    )

    discipline = models.ForeignKey(
        Discipline,
        on_delete=models.PROTECT,
        related_name='invitations'
    )

    expected_questions = models.PositiveSmallIntegerField(default=1)

    token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    is_active = models.BooleanField(default=True)
    last_accessed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    email_sent_at = models.DateTimeField(null=True, blank=True)
    email_error = models.TextField(blank=True)


    def __str__(self):
        return (
            f"{self.teacher.name} — "
            f"{self.discipline.name} — "
            f"{self.collection.title}"
        )
    
    def number_of_questions(self):
        # in the next version, this should be replaced with a column
        return self.expected_questions // 2


class Question(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Rascunho'
        SUBMITTED = 'submitted', 'Enviada'
        PUBLISHED = 'published', 'Publicada'
        ARCHIVED = 'archived', 'Arquivada'

    invitation = models.ForeignKey(
        Invitation,
        on_delete=models.CASCADE,
        related_name='questions'
    )

    body = models.TextField(blank=True)
    image = models.ImageField(upload_to='question_images/%Y/%m/', blank=True)

    teacher_notes = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Question {self.pk or 'new'} - {self.invitation}"


class Option(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options'
    )

    text = models.TextField(blank=True)

    image = models.ImageField(
        upload_to='option_images/%Y/%m/',
        blank=True
    )

    is_correct = models.BooleanField(default=False)
    position = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['position']
        constraints = [
            models.UniqueConstraint(
                fields=['question', 'position'],
                name='unique_option_position_per_question'
            )
        ]

    def __str__(self):
        return f"Option {self.position} for Question {self.question_id}"
    
    @property
    def letter(self):
        return chr(ord("A") + self.position - 1)