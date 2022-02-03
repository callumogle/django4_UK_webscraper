from datetime import date
from plotly.offline import plot
import plotly.graph_objects as go
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

        # thanks to https://albertrtk.github.io/2021/01/24/Graph-on-a-web-page-with-Plotly-and-Django.html
        # for helping me make these graphs

        # not sure how to do this in list comprehension
        # x = [i for i.date_searched ]

        x = []
        
        if len(context["item_history"]) > 1:
            for i in context['item_history']:
                x.append(i.date_searched)
            y1 = []
            for i in context['item_history']:
                y1.append(i.item_price)
            graph = go.Scatter(x=x, y=y1, mode='lines+markers', name='Line y1')
            
            layout = {
            'title': 'Item Price History',
            'xaxis_title': 'Date',
            'yaxis_title': 'Item price (£)',
            'height': 420,
            'width': 560,
            }
            
            context['graph'] = plot({'data': graph, 'layout': layout}, 
                        output_type='div')
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
