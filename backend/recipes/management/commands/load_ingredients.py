import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        if Ingredient.objects.exists():
            print("Данные уже загружены!")
            return
        print("Загрузка Ingredients данных")

        try:
            file_path = "foodgram/data/ingredients.csv"
            print(file_path)
            with open(file_path, encoding='utf-8') as file:
                reader = csv.reader(file)
                for name, measurement_unit in reader:
                    ingredient = Ingredient(name=name,
                                            measurement_unit=measurement_unit)
                    ingredient.save()
                print("Ingredients импортированы.")
        except FileNotFoundError:
            print("CSV file не найден.")
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")
