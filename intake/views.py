from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required

from .forms import OptionFormSet, QuestionForm
from .models import Collection, Question
from .services import get_valid_invitation


@staff_member_required
def collection_list(request):
    collections = Collection.objects.order_by("-created_at")

    return render(
        request,
        "intake/collection_list.html",
        {
            "collections": collections,
        },
    )


@staff_member_required
def collection_questions(request, collection_id):
    collection = get_object_or_404(
        Collection,
        pk=collection_id,
    )

    questions = (
        Question.objects
        .filter(
            invitation__collection=collection,
            status=Question.Status.SUBMITTED,
        )
        .select_related(
            "invitation",
            "invitation__collection",
        )
        .prefetch_related("options")
        .order_by(
            "invitation__discipline__name",
            "invitation__teacher__name",
            "id",
        )
    )

    return render(
        request,
        "intake/collection_questions.html",
        {
            "collection": collection,
            "questions": questions,
        },
    )


def invitation_dashboard(request, token):
    invitation = get_valid_invitation(token)

    questions = invitation.questions.order_by(
        "-updated_at",
    )

    submitted_count = questions.filter(
        status=Question.Status.SUBMITTED,
    ).count()

    context = {
        "invitation": invitation,
        "questions": questions,
        "submitted_count": submitted_count,
    }

    return render(
        request,
        "intake/invitation_dashboard.html",
        context,
    )


def question_create(request, token):
    invitation = get_valid_invitation(token)

    question = Question(invitation=invitation)

    if request.method == "POST":
        form = QuestionForm(
            request.POST,
            request.FILES,
            instance=question,
        )

        formset = OptionFormSet(
            request.POST,
            request.FILES,
            instance=question,
        )

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                question = form.save(commit=False)
                question.invitation = invitation

                if "submit" in request.POST:
                    question.status = Question.Status.SUBMITTED
                    question.submitted_at = timezone.now()

                question.save()

                formset.instance = question
                formset.save()

            return redirect(
                "intake:invitation-dashboard",
                token=invitation.token,
            )

    else:
        form = QuestionForm(instance=question)
        formset = OptionFormSet(instance=question)

        for position, option_form in enumerate(
            formset.forms,
            start=1,
        ):
            option_form.initial["position"] = position

    return render(
        request,
        "intake/question_form.html",
        {
            "invitation": invitation,
            "question": question,
            "form": form,
            "formset": formset,
        },
    )


def question_edit(request, token, question_id):
    invitation = get_valid_invitation(token)

    question = get_object_or_404(
        Question,
        pk=question_id,
        invitation=invitation,
    )

    if question.status == Question.Status.SUBMITTED:
        raise PermissionDenied(
            "Submitted questions can no longer be edited."
        )

    if request.method == "POST":
        form = QuestionForm(
            request.POST,
            request.FILES,
            instance=question,
        )

        formset = OptionFormSet(
            request.POST,
            request.FILES,
            instance=question,
        )

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                question = form.save(commit=False)

                if "submit" in request.POST:
                    question.status = Question.Status.SUBMITTED
                    question.submitted_at = timezone.now()

                question.save()
                formset.save()

            return redirect(
                "intake:invitation-dashboard",
                token=invitation.token,
            )

    else:
        form = QuestionForm(instance=question)

        formset = OptionFormSet(
            instance=question,
            queryset=question.options.all(),
        )

    return render(
        request,
        "intake/question_form.html",
        {
            "invitation": invitation,
            "question": question,
            "form": form,
            "formset": formset,
        },
    )