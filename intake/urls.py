from django.urls import path

from . import views


app_name = "intake"


urlpatterns = [
    path(
        "manage/collections/",
        views.collection_list,
        name="collection-list",
    ),
    path(
        "manage/collections/<int:collection_id>/questions/",
        views.collection_questions,
        name="collection-questions",
    ),
    path(
        "invite/<uuid:token>/",
        views.invitation_dashboard,
        name="invitation-dashboard",
    ),
    path(
        "invite/<uuid:token>/questions/new/",
        views.question_create,
        name="question-create",
    ),
    path(
        "invite/<uuid:token>/questions/<int:question_id>/edit/",
        views.question_edit,
        name="question-edit",
    ),
]