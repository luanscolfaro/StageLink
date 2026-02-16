from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Gig, GigApplication


User = get_user_model()


class GigFlowTests(TestCase):
    def setUp(self):
        self.contractor = User.objects.create_user(
            username="contractor1",
            password="testpass123",
            account_type="contractor",
        )
        self.other_contractor = User.objects.create_user(
            username="contractor2",
            password="testpass123",
            account_type="contractor",
        )
        self.musician = User.objects.create_user(
            username="musician1",
            password="testpass123",
            account_type="musician",
        )
        self.other_musician = User.objects.create_user(
            username="musician2",
            password="testpass123",
            account_type="musician",
        )

    def _create_gig(self, **kwargs):
        defaults = {
            "owner": self.contractor,
            "title": "Gig Teste",
            "description": "Descrição do gig",
            "city": "Sao Paulo",
            "venue": "Casa de Shows",
            "event_date": timezone.localdate() + timedelta(days=10),
            "pay_type": Gig.PayType.NEGOTIABLE,
            "pay_currency": "BRL",
            "status": Gig.Status.OPEN,
        }
        defaults.update(kwargs)
        gig = Gig.objects.create(**defaults)
        return gig

    def test_contractor_can_create_gig(self):
        self.client.force_login(self.contractor)
        response = self.client.post(
            reverse("gigs:create"),
            data={
                "title": "Festival de Verão",
                "description": "Preciso de banda para festival.",
                "city": "Recife",
                "venue": "Marco Zero",
                "event_date": (timezone.localdate() + timedelta(days=15)).isoformat(),
                "pay_type": Gig.PayType.FIXED,
                "pay_amount": "1500.00",
                "pay_currency": "BRL",
                "instruments_needed": "guitar, drums",
                "genres": "rock, pop",
                "tags_input": "festival, cover",
                "status": Gig.Status.OPEN,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Gig.objects.filter(
                owner=self.contractor,
                title="Festival de Verão",
                city="Recife",
            ).exists()
        )

    def test_musician_can_apply_and_cannot_apply_twice(self):
        gig = self._create_gig()
        self.client.force_login(self.musician)

        apply_url = reverse("gigs:apply", kwargs={"identifier": gig.slug})
        first_response = self.client.post(
            apply_url,
            data={"message": "Tenho experiência com este repertório."},
        )
        second_response = self.client.post(
            apply_url,
            data={"message": "Tentando aplicar novamente."},
        )

        self.assertEqual(first_response.status_code, 302)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(
            GigApplication.objects.filter(gig=gig, musician=self.musician).count(),
            1,
        )

    def test_contractor_can_accept_and_reject_application_on_own_gig(self):
        gig = self._create_gig()
        app_one = GigApplication.objects.create(
            gig=gig,
            musician=self.musician,
            message="Quero participar.",
        )
        app_two = GigApplication.objects.create(
            gig=gig,
            musician=self.other_musician,
            message="Tenho equipamento próprio.",
        )

        self.client.force_login(self.contractor)
        accept_url = reverse(
            "gigs:application_decision",
            kwargs={"gig_id": gig.id, "application_id": app_one.id, "action": "accept"},
        )
        reject_url = reverse(
            "gigs:application_decision",
            kwargs={"gig_id": gig.id, "application_id": app_two.id, "action": "reject"},
        )

        accept_response = self.client.post(accept_url)
        reject_response = self.client.post(reject_url)
        app_one.refresh_from_db()
        app_two.refresh_from_db()

        self.assertEqual(accept_response.status_code, 302)
        self.assertEqual(reject_response.status_code, 302)
        self.assertEqual(app_one.status, GigApplication.Status.ACCEPTED)
        self.assertEqual(app_two.status, GigApplication.Status.REJECTED)

    def test_non_owner_cannot_accept_or_reject_application(self):
        gig = self._create_gig()
        application = GigApplication.objects.create(
            gig=gig,
            musician=self.musician,
            message="Tenho disponibilidade.",
        )

        self.client.force_login(self.other_contractor)
        decision_url = reverse(
            "gigs:application_decision",
            kwargs={
                "gig_id": gig.id,
                "application_id": application.id,
                "action": "accept",
            },
        )
        response = self.client.post(decision_url)
        application.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(application.status, GigApplication.Status.PENDING)

    def test_city_and_upcoming_filter(self):
        Gig.objects.create(
            owner=self.contractor,
            title="Show Futuro SP",
            description="Evento em SP no futuro",
            city="Sao Paulo",
            event_date=timezone.localdate() + timedelta(days=5),
            pay_type=Gig.PayType.NEGOTIABLE,
            pay_currency="BRL",
            status=Gig.Status.OPEN,
        )
        Gig.objects.create(
            owner=self.contractor,
            title="Show Passado SP",
            description="Evento passado em SP",
            city="Sao Paulo",
            event_date=timezone.localdate() - timedelta(days=2),
            pay_type=Gig.PayType.NEGOTIABLE,
            pay_currency="BRL",
            status=Gig.Status.OPEN,
        )
        Gig.objects.create(
            owner=self.contractor,
            title="Show Futuro RJ",
            description="Evento no Rio",
            city="Rio de Janeiro",
            event_date=timezone.localdate() + timedelta(days=6),
            pay_type=Gig.PayType.NEGOTIABLE,
            pay_currency="BRL",
            status=Gig.Status.OPEN,
        )

        response = self.client.get(reverse("gigs:list"), data={"city": "Sao Paulo"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Show Futuro SP")
        self.assertNotContains(response, "Show Passado SP")
        self.assertNotContains(response, "Show Futuro RJ")
