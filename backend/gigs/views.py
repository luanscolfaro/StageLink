from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Gig, Application
from .serializers import GigSerializer, ApplicationSerializer
from .permissions import IsContractor, IsOwnerOrReadOnly


class GigViewSet(viewsets.ModelViewSet):
    serializer_class = GigSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Gig.objects.all()

        city = self.request.query_params.get("city")
        tag = self.request.query_params.get("tag")

        if city:
            qs = qs.filter(city__icontains=city)

        if tag:
            qs = qs.filter(tags__icontains=tag)

        return qs

    def get_permissions(self):
    # listar/detalhar: qualquer logado
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]

        # candidatar: músico logado (a validação final já está no apply)
        if self.action == "apply":
            return [permissions.IsAuthenticated()]

        # ver candidaturas: dono da vaga (a validação final já está no método applications)
        if self.action == "applications":
            return [permissions.IsAuthenticated()]

        # criar: só contratante
        if self.action == "create":
            return [permissions.IsAuthenticated(), IsContractor()]

        # editar/apagar: contratante dono
        return [permissions.IsAuthenticated(), IsContractor(), IsOwnerOrReadOnly()]


    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def apply(self, request, pk=None):
        gig = self.get_object()

        if request.user.account_type != "musician":
            return Response({"detail": "Apenas músicos podem se candidatar."}, status=403)

        message = request.data.get("message", "")

        app, created = Application.objects.get_or_create(
            gig=gig,
            applicant=request.user,
            defaults={"message": message}
        )
        if not created:
            return Response({"detail": "Você já se candidatou a esta vaga."}, status=400)

        return Response(ApplicationSerializer(app).data, status=201)

    @action(detail=True, methods=["get"])
    def applications(self, request, pk=None):
        gig = self.get_object()

        if request.user.id != gig.owner_id:
            return Response({"detail": "Apenas o dono da vaga pode ver candidaturas."}, status=403)

        apps = Application.objects.filter(gig=gig)
        return Response(ApplicationSerializer(apps, many=True).data)


class ApplicationManageViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        app = Application.objects.filter(id=pk).select_related("gig").first()
        if not app:
            return Response({"detail": "Candidatura não encontrada."}, status=404)

        if request.user.id != app.gig.owner_id:
            return Response({"detail": "Apenas o dono da vaga pode aceitar."}, status=403)

        app.status = "accepted"
        app.save(update_fields=["status"])
        return Response({"status": "accepted"})

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        app = Application.objects.filter(id=pk).select_related("gig").first()
        if not app:
            return Response({"detail": "Candidatura não encontrada."}, status=404)

        if request.user.id != app.gig.owner_id:
            return Response({"detail": "Apenas o dono da vaga pode recusar."}, status=403)

        app.status = "rejected"
        app.save(update_fields=["status"])
        return Response({"status": "rejected"})
