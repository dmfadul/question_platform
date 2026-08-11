from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils.html import strip_tags
from .models import Option, Question


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = (
            "body",
            "image",
        )

        widgets = {
            "body": forms.Textarea(
                attrs={
                    "rows": 8,
                    "class": "tinymce-question",
                }
            ),
        }


    def clean(self):
        cleaned_data = super().clean()

        body = cleaned_data.get("body", "")
        plain_body = strip_tags(body).strip() if body else ""

        image = cleaned_data.get("image")
        existing_image = self.instance.image if self.instance.pk else None

        if not plain_body and not image and not existing_image:
            raise ValidationError(
                "A questão deve conter texto, uma imagem ou ambos."
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
                    "class": "tinymce-option",
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

            text = form.cleaned_data.get("text", "")
            plain_text = strip_tags(text).strip() if text else ""
            uploaded_image = form.cleaned_data.get("image")
            existing_image = (
                form.instance.image
                if form.instance.pk
                else None
            )

            has_content = bool(
                plain_text or uploaded_image or existing_image
            )

            if not has_content:
                if form.cleaned_data.get("is_correct"):
                    raise ValidationError(
                        "Uma opção em branco não pode ser marcada como correta."
                    )

                continue

            filled_options.append(form)

            if form.cleaned_data.get("is_correct"):
                correct_count += 1

        if len(filled_options) != 5:
            raise ValidationError(
                "Adicione exatamente cinco alternativas."
            )

        if correct_count != 1:
            raise ValidationError(
                "Marque exatamente uma alternativa como correta."
            )


OptionFormSet = inlineformset_factory(
    Question,
    Option,
    form=OptionForm,
    formset=BaseOptionFormSet,
    extra=5,
    min_num=5,
    max_num=5,
    validate_min=True,
    validate_max=True,
    can_delete=False,
)