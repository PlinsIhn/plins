import json
from django.core.management.base import BaseCommand
from vendeur.models import Adresse  # remplace par ton app

class Command(BaseCommand):
    help = "Importe les adresses de Madagascar depuis un fichier JSON imbriqué"

    def handle(self, *args, **kwargs):
        file_path = 'vendeur/madagascar_adresse.json'  # adapte le chemin si besoin

        with open(file_path, encoding='utf-8') as f:
            data = json.load(f)

        created = 0
        # On ignore la première clé "Region", "District", etc. → elles ne contiennent pas de vraies données
        count = 0
        for region_name, districts in data.items():
            if region_name in ["Region", "District", "Commune"]:
                continue

            for district_name, communes in districts.items():
                for commune_name, fokontany_list in communes.items():
                    for item in fokontany_list:
                        region = item.get("region")
                        district = item.get("district")
                        commune = item.get("commune")
                        fokontany = item.get("fokontany")

                        _, created = Adresse.objects.get_or_create(
                            region=region,
                            district=district,
                            commune=commune,
                            fokontany=fokontany
                        )
                        if created:
                            count += 1
                            if count % 5 == 0:
                                print(f"{count} adresses importées...")

        print(f"Import terminé. Total : {count} adresses importées.")
