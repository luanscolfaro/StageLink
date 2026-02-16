from datetime import date, timedelta

from django import forms
from django.core.exceptions import ValidationError

from .models import Gig, GigApplication, Tag


def parse_csv_values(raw_value):
    if not raw_value:
        return []
    return [item.strip().lower() for item in raw_value.split(",") if item.strip()]


class GigForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        label="Tags",
        help_text="Comma-separated tags (e.g. wedding, cover, bar)",
    )

    class Meta:
        model = Gig
        fields = [
            "title",
            "description",
            "city",
            "venue",
            "event_date",
            "pay_type",
            "pay_amount",
            "pay_currency",
            "instruments_needed",
            "genres",
            "tags_input",
            "status",
        ]
        widgets = {
            "event_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["tags_input"].initial = ", ".join(
                self.instance.tags.values_list("name", flat=True)
            )

    def clean_event_date(self):
        event_date = self.cleaned_data["event_date"]
        if event_date < date.today():
            raise ValidationError("Event date cannot be in the past.")
        return event_date

    def clean(self):
        cleaned_data = super().clean()
        pay_type = cleaned_data.get("pay_type")
        pay_amount = cleaned_data.get("pay_amount")

        if pay_type == Gig.PayType.FIXED and pay_amount is None:
            self.add_error(
                "pay_amount",
                "Pay amount is required when pay type is FIXED.",
            )
        elif pay_type != Gig.PayType.FIXED:
            cleaned_data["pay_amount"] = None

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=commit)
        tags = parse_csv_values(self.cleaned_data.get("tags_input", ""))

        if commit:
            tag_objects = [Tag.objects.get_or_create(name=tag_name)[0] for tag_name in tags]
            instance.tags.set(tag_objects)
        else:
            self._pending_tags = tags

        return instance

    def save_m2m(self):
        super().save_m2m()
        pending_tags = getattr(self, "_pending_tags", None)
        if pending_tags is not None:
            tag_objects = [
                Tag.objects.get_or_create(name=tag_name)[0]
                for tag_name in pending_tags
            ]
            self.instance.tags.set(tag_objects)


class GigFilterForm(forms.Form):
    DATE_RANGE_CHOICES = (
        ("upcoming", "Upcoming"),
        ("next_7_days", "Next 7 days"),
        ("next_30_days", "Next 30 days"),
        ("all", "All"),
    )
    ORDERING_CHOICES = (
        ("event_date_asc", "Closest event first"),
        ("newest", "Newest"),
    )
    STATUS_CHOICES = (("", "All"),) + tuple(Gig.Status.choices)

    q = forms.CharField(required=False, label="Search")
    city = forms.CharField(required=False)
    date_range = forms.ChoiceField(choices=DATE_RANGE_CHOICES, required=False)
    instruments = forms.MultipleChoiceField(required=False)
    genres = forms.MultipleChoiceField(required=False)
    pay_type = forms.ChoiceField(
        choices=(("", "All"),) + tuple(Gig.PayType.choices),
        required=False,
    )
    min_pay = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        max_digits=10,
    )
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
    ordering = forms.ChoiceField(choices=ORDERING_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data")
        if data is not None:
            mutable_data = data.copy()
            mutable_data.setdefault("date_range", "upcoming")
            mutable_data.setdefault("status", Gig.Status.OPEN)
            mutable_data.setdefault("ordering", "event_date_asc")
            kwargs["data"] = mutable_data

        super().__init__(*args, **kwargs)
        self.fields["instruments"].choices = self._build_choices("instruments_needed")
        self.fields["genres"].choices = self._build_choices("genres")

    def _build_choices(self, field_name):
        values = set()
        for raw in Gig.objects.exclude(**{field_name: ""}).values_list(field_name, flat=True):
            for item in parse_csv_values(raw):
                values.add(item)
        sorted_values = sorted(values)
        return [(value, value) for value in sorted_values]

    def get_date_window(self):
        today = date.today()
        date_range = self.cleaned_data.get("date_range") or "upcoming"
        if date_range == "next_7_days":
            return today, today + timedelta(days=7)
        if date_range == "next_30_days":
            return today, today + timedelta(days=30)
        if date_range == "upcoming":
            return today, None
        return None, None


class GigApplicationForm(forms.ModelForm):
    class Meta:
        model = GigApplication
        fields = ["message", "portfolio_url", "attachment"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        self.gig = kwargs.pop("gig")
        self.musician = kwargs.pop("musician")
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        if self.gig.status != Gig.Status.OPEN:
            raise ValidationError("This gig is not open for applications.")

        if getattr(self.musician, "account_type", None) != "musician":
            raise ValidationError("Only musicians can apply to gigs.")

        already_applied = GigApplication.objects.filter(
            gig=self.gig,
            musician=self.musician,
        ).exists()
        if already_applied:
            raise ValidationError("You have already applied to this gig.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.gig = self.gig
        instance.musician = self.musician
        if commit:
            instance.save()
        return instance
