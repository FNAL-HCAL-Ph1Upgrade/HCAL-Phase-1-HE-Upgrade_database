from django.shortcuts import render
from django.views import generic

from .models import CalibrationUnit, CuLocation

# Create your views here.

from django.utils import timezone
from django.http import HttpResponse, Http404
from card_db.settings import MEDIA_ROOT 


class CatalogView(generic.ListView):
    """ This displays a list of all calibration units """
    
    template_name = 'calibration_units/catalog.html'
    context_object_name = 'cu_list'
    def get_queryset(self):
        return CalibrationUnit.objects.all().order_by('cu_number')

def catalog(request):
    """ This displays a list of all calibration units """

    cus = CalibrationUnit.objects.all().order_by('cu_number')
    count = len(cus)

    return render(request, 'calibration_units/catalog.html', {'cu_list': cus,
                                                              'total_count': count})

def detail(request, cu_number):
    """ This displays details about a calibration unit """
    try:
        calUnit = CalibrationUnit.objects.get(cu_number=cu_number)
    except CalibrationUnit.DoesNotExist:
        raise Http404("Calibration Unit number " + str(cu_number) + " does not exist")

    if(request.POST.get('comment_add')):
        comment = ""
        if not calUnit.comments == "":
            comment += "\n"
        comment += str(timezone.now().date()) + " " + str(timezone.now().hour) + "." + str(timezone.now().minute) + ": " + request.POST.get('comment')
        calUnit.comments += comment
        calUnit.save()
    
    if(request.POST.get('location_add')):
        if len(CuLocation.objects.filter(cu=calUnit)) < 10:
            CuLocation.objects.create(geo_loc=request.POST.get("location"), cu=calUnit)

    locations = CuLocation.objects.filter(cu=calUnit)
    
    return render(request, 'calibration_units/detail.html', {'cu': calUnit,
                                                             'locations' : locations})
