from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, FormView, TemplateView, UpdateView
from rest_framework import generics, permissions

from .forms import (
    ContractorProfileForm,
    MusicianProfileForm,
    ProfileForm,
    RolesForm,
    SignupForm,
)
from .models import Profile, Role
from .permissions import ContractorRequiredMixin, MusicianRequiredMixin
from .serializers import RegisterSerializer, UserMeSerializer
from .services import (
    create_user_with_profile,
    ensure_profile_for_user,
    ensure_subprofiles_for_roles,
    set_profile_roles,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveAPIView):
    serializer_class = UserMeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        ensure_profile_for_user(self.request.user)
        return self.request.user


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("accounts:dashboard")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = create_user_with_profile(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password1"],
            email=form.cleaned_data.get("email", ""),
            first_name=form.cleaned_data.get("first_name", ""),
            last_name=form.cleaned_data.get("last_name", ""),
            phone=form.cleaned_data.get("phone", ""),
            city=form.cleaned_data.get("city", ""),
            state=form.cleaned_data.get("state", ""),
            display_name=form.cleaned_data.get("display_name", ""),
            bio=form.cleaned_data.get("bio", ""),
            is_public=form.cleaned_data.get("is_public", True),
            role_keys=form.selected_role_keys(),
        )
        login(self.request, self.object)
        return redirect(self.get_success_url())


class AccountLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class AccountLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = ensure_profile_for_user(self.request.user)
        context["profile"] = profile
        context["role_keys"] = profile.role_keys()
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    template_name = "accounts/profile_edit.html"
    success_url = reverse_lazy("accounts:dashboard")

    def get_object(self, queryset=None):
        return ensure_profile_for_user(self.request.user)


class RolesEditView(LoginRequiredMixin, FormView):
    form_class = RolesForm
    template_name = "accounts/roles_edit.html"
    success_url = reverse_lazy("accounts:dashboard")

    def get_initial(self):
        profile = ensure_profile_for_user(self.request.user)
        return {
            "musician": profile.has_role(Role.Key.MUSICIAN),
            "contractor": profile.has_role(Role.Key.CONTRACTOR),
        }

    def form_valid(self, form):
        profile = ensure_profile_for_user(self.request.user)
        set_profile_roles(profile, form.selected_role_keys())
        ensure_subprofiles_for_roles(profile)
        return super().form_valid(form)


class MusicianProfileEditView(LoginRequiredMixin, MusicianRequiredMixin, UpdateView):
    form_class = MusicianProfileForm
    template_name = "accounts/musician_edit.html"
    success_url = reverse_lazy("accounts:dashboard")

    def get_object(self, queryset=None):
        profile = ensure_profile_for_user(self.request.user)
        ensure_subprofiles_for_roles(profile)
        return profile.musician_profile


class ContractorProfileEditView(LoginRequiredMixin, ContractorRequiredMixin, UpdateView):
    form_class = ContractorProfileForm
    template_name = "accounts/contractor_edit.html"
    success_url = reverse_lazy("accounts:dashboard")

    def get_object(self, queryset=None):
        profile = ensure_profile_for_user(self.request.user)
        ensure_subprofiles_for_roles(profile)
        return profile.contractor_profile


class PublicProfileView(DetailView):
    model = Profile
    template_name = "accounts/public_profile.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        profile = (
            Profile.objects.select_related("user")
            .prefetch_related("roles")
            .filter(user__username=self.kwargs["username"])
            .first()
        )
        if profile is None:
            raise Http404("Usuario nao encontrado")

        if not profile.is_public:
            user = self.request.user
            is_owner = user.is_authenticated and user.pk == profile.user_id
            if not is_owner:
                raise Http404("Perfil privado")

        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = context["profile"]
        role_keys = profile.role_keys()
        context["role_keys"] = sorted(role_keys)

        context["show_musician"] = (
            Role.Key.MUSICIAN in role_keys and hasattr(profile, "musician_profile")
        )
        context["show_contractor"] = (
            Role.Key.CONTRACTOR in role_keys and hasattr(profile, "contractor_profile")
        )
        return context
