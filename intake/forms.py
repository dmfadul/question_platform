from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import Option, Question


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = (
            "body",
            "image",
            "teacher_notes",
        )

        widgets = {
            "body": forms.Textarea(
                attrs={
                    "rows": 8,
                    "placeholder": "Enter the question...",
                }
            ),
            "teacher_notes": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": (
                        "Optional notes for the test organizer"
                    ),
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        body = cleaned_data.get("body", "").strip()
        image = cleaned_data.get("image")

        existing_image = self.instance.image if self.instance.pk else None

        if not body and not image and not existing_image:
            raise ValidationError(
                "The question must contain text, an image, or both."
            )

        return cleaned_data


class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = (
            "position",
            "text",
            "image",
            "is_correct",
        )

        widgets = {
            "position": forms.HiddenInput(),
            "text": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Option text",
                }
            ),
        }


class BaseOptionFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        filled_options = []
        correct_count = 0

        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue

            if form.cleaned_data.get("DELETE"):
                continue

            text = form.cleaned_data.get("text", "").strip()
            uploaded_image = form.cleaned_data.get("image")
            existing_image = (
                form.instance.image
                if form.instance.pk
                else None
            )

            has_content = bool(
                text or uploaded_image or existing_image
            )

            if not has_content:
                if form.cleaned_data.get("is_correct"):
                    raise ValidationError(
                        "A blank option cannot be marked as correct."
                    )

                continue

            filled_options.append(form)

            if form.cleaned_data.get("is_correct"):
                correct_count += 1

        if len(filled_options) < 2:
            raise ValidationError(
                "Add at least two alternatives."
            )

        if correct_count != 1:
            raise ValidationError(
                "Mark exactly one alternative as correct."
            )


OptionFormSet = inlineformset_factory(
    Question,
    Option,
    form=OptionForm,
    formset=BaseOptionFormSet,
    extra=5,
    min_num=2,
    max_num=8,
    validate_min=True,
    validate_max=True,
    can_delete=True,
)