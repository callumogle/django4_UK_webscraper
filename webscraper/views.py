from datetime import date
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from .models import Webscraper
from .scraper import scraper
from time import strftime

class IndexView(generic.ListView):
    template_name = 'webscraper/index.html'
    context_object_name = "latest_search_results"
    
    def get_queryset(self):

        return Webscraper.objects.all()


class ItemDetailView(generic.DetailView):
    model = Webscraper
    template_name = 'webscraper/item_detail.html'
    # thanks to Buhran khalid https://stackoverflow.com/questions/26570841/showing-a-list-of-objects-alongside-a-django-detailview
    def get_context_data(self,*args,**kwargs):
        context = super(ItemDetailView,self).get_context_data(*args,**kwargs)
        precontext = Webscraper.objects.filter(pk=self.kwargs['pk'])[0]
        context['item_history'] = Webscraper.objects.filter(item_name=precontext)
        


def search(request):
    return render(request, 'webscraper/search.html')


def webscraper(request):
    # can definetly do this better
    if request.method == 'GET':
        todays_date = strftime("%Y-%m-%d")
        search_term = request.GET.get('search_bar')
        search_results = Webscraper.objects.filter(item_searched=search_term, date_searched=todays_date)
        if search_results.count() > 0:
            context = {"items" : search_results}
            return render(request,"webscraper/results.html", context)
            #return render(request,"webscraper/results.html",{"items" : search_results})
        else:
            scraper(search_term)
            search_results = Webscraper.objects.filter(item_searched=search_term, date_searched=todays_date)
            context = {{"items" : search_results}}
            return render(request,"webscraper/results.html", context)