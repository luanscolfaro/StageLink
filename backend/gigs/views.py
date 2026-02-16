from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView

from .forms import GigApplicationForm, GigFilterForm, GigForm
from .models import Gig, GigApplication


def is_musician(user):
    return user.is_authenticated and getattr(user, "account_type", "") == "musician"


def is_contractor(user):
    return user.is_authenticated and getattr(user, "account_type", "") == "contractor"


def get_gig_by_identifier(identifier):
    queryset = Gig.objects.select_related("owner").prefetch_related("tags")
    if str(identifier).isdigit():
        return get_object_or_404(queryset, pk=int(identifier))
    return get_object_or_404(queryset, slug=identifier)


class ContractorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return is_contractor(self.request.user)


class MusicianRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return is_musician(self.request.user)


class GigListView(ListView):
    model = Gig
    template_name = "gigs/gig_list.html"
    context_object_name = "gigs"
    paginate_by = 10

    def get_queryset(self):
        queryset = Gig.objects.select_related("owner").prefetch_related("tags")
        self.filter_form = GigFilterForm(self.request.GET or None)

        if not self.filter_form.is_valid():
            return queryset.none()

        cleaned = self.filter_form.cleaned_data
        query = cleaned.get("q")
        city = cleaned.get("city")
        instruments = cleaned.get("instruments") or []
        genres = cleaned.get("genres") or []
        pay_type = cleaned.get("pay_type")
        min_pay = cleaned.get("min_pay")
        status = cleaned.get("status")
        if "status" not in self.request.GET:
            status = Gig.Status.OPEN
        ordering = cleaned.get("ordering") or "event_date_asc"

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(tags__name__icontains=query)
            )

        if city:
            queryset = queryset.filter(city__icontains=city)

        if status:
            queryset = queryset.filter(status=status)

        start_date, end_date = self.filter_form.get_date_window()
        if start_date:
            queryset = queryset.filter(event_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(event_date__lte=end_date)

        if instruments:
            instruments_filter = Q()
            for item in instruments:
                instruments_filter |= Q(instruments_needed__icontains=item)
            queryset = queryset.filter(instruments_filter)

        if genres:
            genres_filter = Q()
            for item in genres:
                genres_filter |= Q(genres__icontains=item)
            queryset = queryset.filter(genres_filter)

        if pay_type:
            queryset = queryset.filter(pay_type=pay_type)

        if min_pay is not None:
            queryset = queryset.filter(
                pay_type=Gig.PayType.FIXED,
                pay_amount__gte=min_pay,
            )

        if ordering == "newest":
            queryset = queryset.order_by("-created_at")
        else:
            queryset = queryset.order_by("event_date", "-created_at")

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = getattr(self, "filter_form", GigFilterForm())
        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        context["querystring"] = query_params.urlencode()
        return context


class GigDetailView(DetailView):
    model = Gig
    template_name = "gigs/gig_detail.html"
    context_object_name = "gig"

    def get_object(self, queryset=None):
        return get_gig_by_identifier(self.kwargs["identifier"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gig = context["gig"]
        user = self.request.user

        my_application = None
        if is_musician(user):
            my_application = GigApplication.objects.filter(
                gig=gig,
                musician=user,
            ).first()

        context["my_application"] = my_application
        context["can_apply"] = (
            is_musician(user)
            and gig.status == Gig.Status.OPEN
            and my_application is None
        )
        context["can_manage"] = user.is_authenticated and user == gig.owner

        if context["can_manage"]:
            context["applications"] = gig.applications.select_related("musician")
        else:
            context["applications"] = GigApplication.objects.none()

        return context


class GigCreateView(ContractorRequiredMixin, CreateView):
    model = Gig
    form_class = GigForm
    template_name = "gigs/gig_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("gigs:detail", kwargs={"identifier": self.object.slug})


class GigUpdateView(ContractorRequiredMixin, UpdateView):
    model = Gig
    form_class = GigForm
    template_name = "gigs/gig_form.html"
    pk_url_kwarg = "gig_id"

    def get_queryset(self):
        return Gig.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse("gigs:detail", kwargs={"identifier": self.object.slug})


class GigStatusUpdateView(ContractorRequiredMixin, View):
    valid_statuses = {Gig.Status.CLOSED, Gig.Status.CANCELLED}

    def post(self, request, gig_id, new_status):
        if new_status not in self.valid_statuses:
            raise Http404("Invalid status transition.")

        gig = get_object_or_404(Gig, pk=gig_id, owner=request.user)
        gig.status = new_status
        gig.save()
        return redirect("gigs:detail", identifier=gig.slug)


class GigApplicationCreateView(MusicianRequiredMixin, FormView):
    template_name = "gigs/application_form.html"
    form_class = GigApplicationForm

    def dispatch(self, request, *args, **kwargs):
        self.gig = get_gig_by_identifier(kwargs["identifier"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["gig"] = self.gig
        kwargs["musician"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("gigs:detail", kwargs={"identifier": self.gig.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["gig"] = self.gig
        return context


class GigApplicationWithdrawView(MusicianRequiredMixin, View):
    def post(self, request, application_id):
        application = get_object_or_404(
            GigApplication,
            pk=application_id,
            musician=request.user,
        )
        application.status = GigApplication.Status.WITHDRAWN
        application.save()

        next_url = request.POST.get("next") or request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
        ):
            return redirect(next_url)

        return redirect("gigs:my_applications")


class MyApplicationsView(MusicianRequiredMixin, ListView):
    model = GigApplication
    template_name = "gigs/my_applications.html"
    context_object_name = "applications"
    paginate_by = 10

    def get_queryset(self):
        queryset = GigApplication.objects.select_related("gig").filter(
            musician=self.request.user
        )
        status = self.request.GET.get("status")
        if status in dict(GigApplication.Status.choices):
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = GigApplication.Status.choices
        context["current_status"] = self.request.GET.get("status", "")
        return context


class ManageGigsView(ContractorRequiredMixin, ListView):
    model = Gig
    template_name = "gigs/manage_gigs.html"
    context_object_name = "gigs"
    paginate_by = 10

    def get_queryset(self):
        return Gig.objects.filter(owner=self.request.user).order_by("-created_at")


class ManageGigApplicationsView(ContractorRequiredMixin, ListView):
    model = GigApplication
    template_name = "gigs/manage_applications.html"
    context_object_name = "applications"
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        self.gig = get_object_or_404(Gig, pk=kwargs["gig_id"], owner=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.gig.applications.select_related("musician")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["gig"] = self.gig
        return context


class GigApplicationDecisionView(ContractorRequiredMixin, View):
    decision_map = {
        "accept": GigApplication.Status.ACCEPTED,
        "reject": GigApplication.Status.REJECTED,
    }

    def post(self, request, gig_id, application_id, action):
        decision = self.decision_map.get(action)
        if decision is None:
            raise Http404("Invalid action.")

        gig = get_object_or_404(Gig, pk=gig_id, owner=request.user)
        application = get_object_or_404(GigApplication, pk=application_id, gig=gig)
        application.status = decision
        application.save()

        return redirect("gigs:manage_applications", gig_id=gig.id)
