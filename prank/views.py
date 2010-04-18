from django.shortcuts import get_object_or_404, render_to_response
from django import http
from newdominion.prank.models import *

# Create your views here.
def index(request):
  return render_to_response('prank.xhtml',{'categories':CATEGORY_CHOICES})

def submit(request):
  if request.POST:
    print request.POST
    link = Link(link=request.POST['link'],category=int(request.POST['category'])-1)
    link.save()
    return render_to_response('submittedprank.xhtml',
                              {'link':link.id+12543,
                               'category':CATEGORY_CHOICES[link.category][1]})
  else:
    print "huh?"

def prank(request,category_id,link_id):
  link_id = int(link_id) - 12543
  print str(link_id)
  link = get_object_or_404(Link,id=link_id)
  if link.link.split(':')[0] != "http":
    actual = 'http://'+link.link
  else:
    actual = link.link
  
  return http.HttpResponseRedirect(actual)
