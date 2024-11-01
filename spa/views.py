from django.shortcuts import render

from django.views.generic import View

# Create your views here.

class HTMXView(View) :
    def html_name(self):
        return "index"
    
    def get(self, request, *args, **kwargs):
        if request.htmx:
            return render(request, f"{self.html_name()}.html")
        else :
            return render(request, f"{self.html_name()}_f.html")

class IndexView(HTMXView):
    pass

class DiscoverView(HTMXView):
    def html_name(self):
        return "discover"