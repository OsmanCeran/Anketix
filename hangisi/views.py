from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import Secenek, Soru

class IndexView(generic.ListView):
    template_name = "hangisi/index.html"
    context_object_name = "son_sorular"

    def get_queryset(self):
        """
        Gelecekte yayımlanacak olanları (yayinlanma_tarihi>şimdi) hariç tutarak
        son yayımlanan 5 soruyu döndürür.
        """
        return Soru.objects.filter(yayinlanma_tarihi__lte=timezone.now()).order_by(
            "-yayinlanma_tarihi"
        )[:5]

class GrafiklerView(generic.ListView):
    template_name = "hangisi/grafikler.html"
    context_object_name = "sorular"

    def get_queryset(self):
        """
        Tüm yayımlanmış soruları döndür. Grafikler için kullanılacak.
        """
        return Soru.objects.filter(yayinlanma_tarihi__lte=timezone.now()).order_by("-yayinlanma_tarihi")

class DetailView(generic.DetailView):
    model = Soru
    template_name = "hangisi/detail.html"

    def get_queryset(self):
        """
        Henüz yayımlanmamış soruları hariç tutar.
        """
        return Soru.objects.filter(yayinlanma_tarihi__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Soru
    template_name = "hangisi/results.html"

def vote(request, soru_id):
    soru = get_object_or_404(Soru, pk=soru_id)
    try:
        secilen_secenek = soru.secenek_set.get(pk=request.POST["choice"])
    except (KeyError, Secenek.DoesNotExist):
        return render(
            request,
            "hangisi/detail.html",
            {
                "soru": soru,
                "error_message": "Bir seçim yapmadınız.",
            },
        )
    else:
        secilen_secenek.oylar = F("oylar") + 1
        secilen_secenek.save()
        return HttpResponseRedirect(reverse("anketix:results", args=(soru.id,)))

def anket_ekle(request):
    if request.method == "POST":
        soru_metni = request.POST.get("soru_metni", "").strip()
        secenekler = request.POST.getlist("secenek")

        # Boş olan seçenekleri filtrele
        gecerli_secenekler = [s.strip() for s in secenekler if s.strip()]

        if not soru_metni:
            return render(request, "hangisi/anket_ekle.html", {
                "error_message": "Lütfen bir soru girin."
            })
            
        if len(gecerli_secenekler) < 2:
            return render(request, "hangisi/anket_ekle.html", {
                "error_message": "En az 2 geçerli seçenek girmelisiniz.",
                "soru_metni": soru_metni
            })

        # Soruyu oluştur
        yeni_soru = Soru.objects.create(
            soru_metni=soru_metni,
            yayinlanma_tarihi=timezone.now()
        )

        # Seçenekleri oluştur
        for secenek_metni in gecerli_secenekler:
            yeni_soru.secenek_set.create(secenek_metni=secenek_metni)

        return HttpResponseRedirect(reverse("anketix:index"))

    # GET Request
    return render(request, "hangisi/anket_ekle.html")
