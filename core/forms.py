from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.html import strip_tags
import nh3

from .models import Anotacao, EventoCalendario, Materia, Tarefa

TAGS_ANOTACAO = {
    "b", "blockquote", "br", "div", "em", "font", "i", "li", "ol",
    "p", "span", "strong", "u", "ul",
}
ATRIBUTOS_ANOTACAO = {"font": {"face"}}


def limpar_html_anotacao(conteudo):
    return nh3.clean(
        conteudo or "",
        tags=TAGS_ANOTACAO,
        attributes=ATRIBUTOS_ANOTACAO,
    )


class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ["nome", "descricao", "completo"]


class MateriaForm(forms.ModelForm):
    cor = forms.CharField(
        max_length=7,
        validators=[RegexValidator(r"^#[0-9A-Fa-f]{6}$", "Escolha uma cor válida.")],
        widget=forms.TextInput(attrs={"type": "color"}),
    )

    class Meta:
        model = Materia
        fields = ["nome", "cor"]


class AnotacaoForm(forms.ModelForm):
    conteudo = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Anotacao
        fields = ["titulo", "conteudo"]

    def clean_conteudo(self):
        conteudo = limpar_html_anotacao(self.cleaned_data.get("conteudo", ""))
        if not strip_tags(conteudo).strip():
            raise ValidationError("Escreva o conteúdo da anotação.")
        return conteudo


class EventoCalendarioForm(forms.ModelForm):
    class Meta:
        model = EventoCalendario
        fields = ["titulo", "data", "horario", "tipo", "materia", "descricao"]
        widgets = {
            "data": forms.DateInput(attrs={"type": "date"}),
            "horario": forms.TimeInput(attrs={"type": "time"}),
            "descricao": forms.Textarea(attrs={"rows": 3, "maxlength": 1000}),
        }

    def __init__(self, *args, usuario, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["materia"].queryset = Materia.objects.filter(usuario=usuario)
        self.fields["materia"].required = False