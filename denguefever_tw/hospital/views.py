from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

import shortuuid
import json

from hospital.models import Hospital


@csrf_exempt
@require_POST
def hospital_insert(request):
    database = request.POST.get('database', '')
    hospital_id = shortuuid.uuid()
    name = request.POST.get('name', '')
    address = request.POST.get('address', '')
    phone = request.POST.get('phone', '')
    opening_hours = request.POST.get('opening_hours', '')
    lng = request.POST.get('lng', '')
    lat = request.POST.get('lat', '')

    hospital = Hospital(
        hospital_id=hospital_id,
        name=name,
        address=address,
        phone=phone,
        opening_hours=opening_hours,
        lng=lng,
        lat=lat)
    hospital.save(using=database)
    return HttpResponse(status=200)


def get_nearby_hospital(lng, lat, *, database='tainan', limit=3):
    point = Point(_to_float(lng), _to_float(lat), srid=4326)
    hospital_set = (
        Hospital.objects.using(database)
                .annotate(distance=Distance('location', point))
                .filter(location__distance_lte=(point, D(km=5)))
                .order_by('distance')[:limit]
    )

    EXCLUDED_FIELDS = ['hospital_id', 'location', 'objects']
    response_data = [model_to_dict(hospital, exclude=EXCLUDED_FIELDS)
                     for hospital in hospital_set]
    return response_data


def _to_float(f):
    try:
        return float(f)
    except ValueError:
        return -1


@require_GET
def hospital_nearby(request):
    if not request.user.is_authenticated():
        return HttpResponse(status=405)

    database = request.GET.get('database', '')
    lng = request.GET.get('lng', '')
    lat = request.GET.get('lat', '')

    if not all([database, lng, lat]):
        return HttpResponse(status=406)

    point = Point(_to_float(lng), _to_float(lat), srid=4326)
    hospital_set = (
        Hospital.objects.using(database)
                .annotate(distance=Distance('location', point))
                .filter(location__distance_lte=(point, D(km=5)))
                .order_by('distance')
    )

    EXCLUDED_FIELDS = ['hospital_id', 'location', 'objects']
    response_data = list()
    for hospital in hospital_set:
        response_data_tmp = model_to_dict(hospital, exclude=EXCLUDED_FIELDS)
        response_data_tmp['distance'] = str(hospital.distance)
        response_data.append(response_data_tmp)
    return HttpResponse(json.dumps(response_data), status=200, content_type='application/json')
