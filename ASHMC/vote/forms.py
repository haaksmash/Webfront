from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime
from django.utils.safestring import mark_safe

from .models import Ballot, Measure, Restrictions


class CandidateChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "{}".format(obj.cast())


class CandidateMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "{}".format(obj.cast())


class ListItemCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """Gets rid of the wrapping '<ul>' tags, leaving only the list items in the render."""
    def render(self, *args, **kwargs):
        output = super(ListItemCheckboxSelectMultiple, self).render(*args,
    **kwargs)
        return mark_safe(output.replace(u'<ul>', u'').replace(u'</ul>', ''))


class BallotForm(forms.Form):

    def __init__(self, ballot=None, *args, **kwargs):
        prefix = kwargs.pop('prefix', ballot.id)
        super(BallotForm, self).__init__(*args, prefix=prefix, **kwargs)
        self.ballot = ballot
        choices = ballot.candidate_set.all().exclude(is_write_in=True)

        if ballot.vote_type == Ballot.VOTE_TYPES.POPULARITY:
            self.fields['choice'] = CandidateChoiceField(
                widget=forms.RadioSelect,
                empty_label=None if not ballot.can_abstain else "I'm abstaining",
                queryset=choices,
                required=(not ballot.can_write_in and not ballot.can_abstain),
            )

        elif ballot.vote_type == Ballot.VOTE_TYPES.INOROUT:
            self.fields['choice'] = CandidateChoiceField(
                widget=forms.RadioSelect,
                empty_label=None if not ballot.can_abstain else "I'm abstaining",
                queryset=choices,
                required=(not ballot.can_abstain),
            )

        elif ballot.vote_type == Ballot.VOTE_TYPES.SELECT_X:
            self.fields['choice'] = CandidateMultipleChoiceField(
                queryset=choices,
                required=(not ballot.can_abstain),
                error_messages={
                    'required': "You have to choose at least one.",
                },
                widget=ListItemCheckboxSelectMultiple,
            )
            if ballot.can_abstain:
                self.fields['abstains'] = forms.BooleanField(
                    required=False,
                    initial=True,
                    label="I'm abstaining",
                    widget=forms.CheckboxInput(
                        attrs={
                            'class': 'abstains',
                        }
                    ),
                )

        elif ballot.vote_type == Ballot.VOTE_TYPES.PREFERENCE:
            for candidate in ballot.candidate_set.all():
                self.fields[str(candidate.cast())] = forms.IntegerField(
                    min_value=1,
                    # Have to do this here (rather than outside the for loop),
                    # because otherwise the fields don't validate properly. Bugger
                    # if I know why, though.
                    max_value=ballot.candidate_set.count(),
                    required=not ballot.is_irv,
                    label="{}".format(candidate.cast()),
                    widget=forms.TextInput(
                        attrs={
                            'class': 'preference',
                        }
                    ),
                )
                self.fields[str(candidate.cast())].candidate = candidate

        # write-ins don't make sense in a preference context.
        if ballot.can_write_in and ballot.vote_type != Ballot.VOTE_TYPES.PREFERENCE:
            self.fields['write_in_value'] = forms.CharField(
                max_length=50,
                required=False,
                widget=forms.TextInput(
                    attrs={
                        'placeholder': "or, write in here.",
                        'class': 'write_in',
                    })
            )

    def clean(self):
        cleaned_data = super(BallotForm, self).clean()
        # Ensure that the write-in can't be just whitespace.
        write_in = cleaned_data.get('write_in_value', None)

        if self.ballot.vote_type == Ballot.VOTE_TYPES.POPULARITY:
            choice = cleaned_data.get('choice', None)

            # A none choice would have been caught unless there's a write-in field
            if choice is None and not write_in:
                if not self.ballot.can_abstain:
                    raise forms.ValidationError(
                        "Must either select a candidate or write one in."
                    )

            if choice is not None and write_in:
                raise forms.ValidationError(
                    "Can't choose a candidate and write one in for the same ballot."
                )

            if write_in:
                if not write_in.strip():
                    raise forms.ValidationError(
                        "Can't write-in an empty candidate.",
                    )

        elif self.ballot.vote_type == Ballot.VOTE_TYPES.SELECT_X:
            cleaned_data.setdefault('choice', [])
            if self.ballot.can_abstain:
                if not cleaned_data['abstains'] and not cleaned_data['choice']:
                    raise forms.ValidationError("You must either abstain or choose at least one option.")
            if len(cleaned_data['choice']) > self.ballot.number_to_select:
                raise forms.ValidationError("You may only select up to {} candidate{}".format(
                        self.ballot.number_to_select,
                        '' if self.ballot.candidate_set.count() == 1 else 's',  # pluralize
                    )
                )

        elif self.ballot.vote_type == Ballot.VOTE_TYPES.PREFERENCE:
            rankings = set(cleaned_data.itervalues())
            print "CLEANED: ", cleaned_data

            if len(rankings) != len(cleaned_data):
                if not self.ballot.is_irv:
                    # IRV ballots do *not* require complete rankings;
                    # standard preferential ballots do.
                    raise forms.ValidationError(
                        "You must rank each option uniquely."
                    )

        return cleaned_data

BallotFormSet = forms.formsets.formset_factory(BallotForm, extra=0)


class CreateMeasureForm(forms.ModelForm):
    class Meta:
        model = Measure

    def __init__(self, *args, **kwargs):
        super(CreateMeasureForm, self).__init__(*args, **kwargs)
        self.fields['vote_start'].widget = AdminSplitDateTime()
        self.fields['vote_start'].widget.attrs['style'] = "padding:0.25em;text-align:center"
        self.fields['vote_start'].widget.attrs['size'] = 10
        self.fields['vote_end'].widget = AdminSplitDateTime()
        self.fields['vote_end'].widget.attrs['style'] = "padding:0.25em;text-align:center"
        self.fields['vote_end'].widget.attrs['size'] = 10

        self.fields['quorum'].widget.attrs['style'] = "width:50px"
        self.fields['summary'].widget.attrs['style'] = "width: 100%; height: 75px;"
        self.fields['summary'].widget.attrs['placeholder'] = "Measury summary goes here."
        self.fields['name'].widget.attrs['placeholder'] = "Measure Title"


class CreateRestrictionsForm(forms.ModelForm):
    class Meta:
        model = Restrictions
