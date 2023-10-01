import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        if Ingredient.objects.exists():
            print("Данные уже загружены...выход!")
            return
        print("Загрузка Ingredients данных")

        try:
            file_path = "foodgram/data/ingredients.csv"
            print(file_path)
            with open(file_path) as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    db = Ingredient(
                        name=row["name"],
                        measurement_unit=row["measurement_unit"]
                    )
                    db.save()
                print("Ingredients импортированы.")
        except FileNotFoundError:
            print("CSV file не найден.")
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")
