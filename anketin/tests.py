import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Soru

def create_question(soru_metni, days):
    """
    Belirtilen `soru_metni` ve `days` (gün) sapması ile bir soru oluşturur
    (geçmişte yayımlananlar için negatif, gelecekte yayımlanacaklar için pozitif).
    """
    zaman = timezone.now() + datetime.timedelta(days=days)
    return Soru.objects.create(soru_metni=soru_metni, yayinlanma_tarihi=zaman)

class SoruIndexViewTests(TestCase):
    def test_no_questions(self):
        """Herhangi bir soru yoksa uygun mesaj gösterilir."""
        response = self.client.get(reverse("anketin:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Henüz Anket Yok")
        self.assertQuerySetEqual(response.context["son_sorular"], [])

    def test_past_question(self):
        """Geçmişte yayımlanan sorular index sayfasında gösterilir."""
        soru = create_question(soru_metni="Geçmiş soru.", days=-30)
        response = self.client.get(reverse("anketin:index"))
        self.assertQuerySetEqual(
            response.context["son_sorular"],
            [soru],
        )

    def test_future_question(self):
        """Gelecekte yayımlanacak sorular index sayfasında gösterilmez."""
        create_question(soru_metni="Gelecek soru.", days=30)
        response = self.client.get(reverse("anketin:index"))
        self.assertContains(response, "Henüz Anket Yok")
        self.assertQuerySetEqual(response.context["son_sorular"], [])

    def test_future_question_and_past_question(self):
        """Hem geçmiş hem gelecek soru varsa, sadece geçmiş sorular gösterilir."""
        soru = create_question(soru_metni="Geçmiş soru.", days=-30)
        create_question(soru_metni="Gelecek soru.", days=30)
        response = self.client.get(reverse("anketin:index"))
        self.assertQuerySetEqual(
            response.context["son_sorular"],
            [soru],
        )

    def test_two_past_questions(self):
        """Index sayfası birden çok soruyu gösterebilir."""
        soru1 = create_question(soru_metni="Geçmiş soru 1.", days=-30)
        soru2 = create_question(soru_metni="Geçmiş soru 2.", days=-5)
        response = self.client.get(reverse("anketin:index"))
        self.assertQuerySetEqual(
            response.context["son_sorular"],
            [soru2, soru1],
        )

class SoruDetailViewTests(TestCase):
    def test_future_question(self):
        """
        Gelecekte yayımlanacak bir sorunun detail görünümü
        404 (Böyle bir sayfa yok) döndürür.
        """
        gelecekteki_soru = create_question(soru_metni="Gelecek soru.", days=5)
        url = reverse("anketin:detail", args=(gelecekteki_soru.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        Geçmişte yayımlanan bir sorunun detail görünümü
        soru metnini gösterir.
        """
        gecmis_soru = create_question(soru_metni="Geçmiş soru.", days=-5)
        url = reverse("anketin:detail", args=(gecmis_soru.id,))
        response = self.client.get(url)
        self.assertContains(response, gecmis_soru.soru_metni)

class SoruModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently(), yayinlanma_tarihi gelecekte olan
        sorular için False döndürmelidir.
        """
        zaman = timezone.now() + datetime.timedelta(days=30)
        gelecekteki_soru = Soru(yayinlanma_tarihi=zaman)
        self.assertIs(gelecekteki_soru.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently(), yayinlanma_tarihi 1 günden daha eski
        olan sorular için False döndürmelidir.
        """
        zaman = timezone.now() - datetime.timedelta(days=1, seconds=1)
        eski_soru = Soru(yayinlanma_tarihi=zaman)
        self.assertIs(eski_soru.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently(), yayinlanma_tarihi son 1 gün içinde
        olan sorular için True döndürmelidir.
        """
        zaman = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        yeni_soru = Soru(yayinlanma_tarihi=zaman)
        self.assertIs(yeni_soru.was_published_recently(), True)
