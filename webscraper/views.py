from datetime import date
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from .models import Webscraper
from .scraper import scraper
from time import strftime


class IndexView(generic.ListView):
    template_name = "webscraper/results.html"
    context_object_name = "items"

    def get_queryset(self):

        return Webscraper.objects.all()[::50]


class ItemDetailView(generic.DetailView):
    model = Webscraper
    template_name = "webscraper/item_detail.html"
    context_object_name = "item"
    # thanks to Buhran khalid https://stackoverflow.com/questions/26570841/showing-a-list-of-objects-alongside-a-django-detailview
    def get_context_data(self, *args, **kwargs):
        context = super(ItemDetailView, self).get_context_data(*args, **kwargs)
        # the kwarg is the slug passed into the url in this case pk, filter returns a queryset hence [0]
        precontext = Webscraper.objects.filter(pk=self.kwargs["pk"])[0]
        context["item_history"] = Webscraper.objects.filter(item_name=precontext)
        return context


def search(request):
    return render(request, "webscraper/search.html")


def webscraper(request):
    ### TO DO
    # Webscraper.objects.filter(item_name__icontains="braeburn")
    # use above query as a basis to group stuff together with similar name
    ###
    # can definetly do this better
    if request.method == "GET":
        todays_date = strftime("%Y-%m-%d")
        search_term = request.GET.get("search_bar")
        search_results = Webscraper.objects.filter(
            item_searched=search_term, date_searched=todays_date
        )
        # prevents non admin from causing a selenium search and reduce odds of detection
        # and ip ban. need to set up admin page
        if not request.user.is_superuser:
            results = Webscraper.objects.filter(
                item_name__icontains=search_term, date_searched=todays_date
            ) | Webscraper.objects.filter(
                item_searched=search_term, date_searched=todays_date
            )
            context = {"items": results}
            return render(request, "webscraper/results.html", context)

        elif search_results.count() == 0:
            scraper(search_term)
            search_results = Webscraper.objects.filter(
                item_searched=search_term, date_searched=todays_date
            )
            context = {"items": search_results.order_by("item_name")}
            return render(request, "webscraper/results.html", context)

        else:
            return render(request, "webscraper/results.html", {"items": search_results})
