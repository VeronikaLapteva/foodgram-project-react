from csv import DictReader

from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Выгрузка данных из ingredients.csv"

    def handle(self, *args, **options):
        if Ingredient.objects.exists():
            print("Данные уже загружены!")
            return
        print("Загрузка Ingredient данных")

        try:
            for row in DictReader(open("foodgram/data/ingredients.csv")):
                ingredients = Ingredient(
                    name=row['name'],
                    measurement_unit=row['measurement_unit'])
                ingredients.save()
                print("Ingredients импортированы.")
        except FileNotFoundError:
            print("CSV file не найден.")
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")
