from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Collection,
    Discipline,
    Invitation,
    Option,
    Question,
    Teacher,
)


class OptionInline(admin.TabularInline):
    model = Option
    extra = 0


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "is_active",
        "created_at",
    )

    list_filter = ("is_active",)

    search_fields = (
        "name",
        "email",
    )

    readonly_fields = ("created_at",)

    ordering = ("name",)


@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "created_at",
    )

    search_fields = (
        "name",
        "code",
        "description",
    )

    readonly_fields = ("created_at",)

    ordering = ("name",)


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "deadline",
        "is_open",
        "submitted_questions_link",
        "created_at",
    )

    @admin.display(description="Questions")
    def submitted_questions_link(self, collection):
        if not collection.pk:
            return "-"

        url = reverse(
            "intake:collection-questions",
            args=[collection.pk],
        )

        return format_html(
            '<a href="{}">View questions</a>',
            url,
        )

    list_filter = ("is_open",)

    search_fields = (
        "title",
        "instructions",
    )

    readonly_fields = ("created_at",)

    ordering = ("-created_at",)


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = (
        "teacher",
        "discipline",
        "collection",
        "expected_questions",
        "submitted_count",
        "is_active",
        "email_sent_at",
        "invitation_link",
    )

    list_filter = (
        "collection",
        "discipline",
        "is_active",
        "email_sent_at",
    )

    search_fields = (
        "teacher__name",
        "teacher__email",
        "discipline__name",
        "discipline__code",
        "collection__title",
    )

    readonly_fields = (
        "token",
        "invitation_link",
        "last_accessed_at",
        "created_at",
        "email_sent_at",
        "email_error",
    )

    autocomplete_fields = (
        "teacher",
        "discipline",
        "collection",
    )

    list_select_related = (
        "teacher",
        "discipline",
        "collection",
    )

    ordering = (
        "-created_at",
    )

    @admin.display(description="Submitted")
    def submitted_count(self, invitation):
        return invitation.questions.filter(
            status=Question.Status.SUBMITTED,
        ).count()

    @admin.display(description="Invitation link")
    def invitation_link(self, invitation):
        if not invitation.pk:
            return "Save the invitation first."

        relative_url = reverse(
            "intake:invitation-dashboard",
            args=[invitation.token],
        )

        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            relative_url,
            relative_url,
        )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "teacher",
        "discipline",
        "collection",
        "status",
        "updated_at",
    )

    list_filter = (
        "status",
        "invitation__collection",
        "invitation__discipline",
    )

    search_fields = (
        "body",
        "teacher_notes",
        "invitation__teacher__name",
        "invitation__teacher__email",
        "invitation__discipline__name",
        "invitation__collection__title",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "submitted_at",
    )

    autocomplete_fields = ("invitation",)

    list_select_related = (
        "invitation",
        "invitation__teacher",
        "invitation__discipline",
        "invitation__collection",
    )

    ordering = ("-updated_at",)

    inlines = [OptionInline]

    @admin.display(description="Teacher")
    def teacher(self, question):
        return question.invitation.teacher

    @admin.display(description="Discipline")
    def discipline(self, question):
        return question.invitation.discipline

    @admin.display(description="Collection")
    def collection(self, question):
        return question.invitation.collection