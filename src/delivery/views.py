from rest_framework.response import Response
from rest_framework.views import APIView
import re

from delivery.services import (get_all_warehouse_types_dict,
                               get_warehouses_by_city_ref,
                               search_nova_poshta_settlements)


class NovaPoshtaSettlementSearchView(APIView):
    def get(self, request):
        query = request.GET.get("query", "").split(" (")[0]
        if not query:
            return Response({"error": "Parameter 'query' is required."}, status=400) 
        if re.fullmatch(r"[A-Za-z0-9\s\-]+", query):
            return Response({"error": "Please enter the city name in Ukrainian (кирилицею)."}, status=400)
        
        try:
            settlements = search_nova_poshta_settlements(query)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        
        result = []
        for s in settlements:
            result.append({
            "name": s.get("Description", ""),
            "Oblast": s.get("AreaDescription", "обласний центр"),
            "Raion": s.get("RegionsDescription", "Відсутній"),
            "ref": s.get("Ref", "")
            })

        return Response(result)


class NovaPoshtaWarehousesView(APIView):
    def get(self, request):
        city_ref = request.GET.get("city_ref")
        if not city_ref:
            return Response({"error": "city_ref is required"}, status=400)

        try:
            warehouses = get_warehouses_by_city_ref(city_ref)
            warehouse_types = get_all_warehouse_types_dict()
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        result = []
        for w in warehouses:
            desc = w.get("Description", "")
            type_ref = w.get("TypeOfWarehouse")
            result.append({
                "number": w.get("Number", ""),
                "address": w.get("ShortAddress", desc or "—"),
                "type": warehouse_types.get(type_ref, "Невідомо")
            })

        return Response(result)
    