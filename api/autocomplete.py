# api/autocomplete.py
from dal import autocomplete
from .models import City

class CityAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = City.objects.all()
        state_id = self.forwarded.get('state', None)
        if state_id:
            qs = qs.filter(state_id=state_id)
        return qs
