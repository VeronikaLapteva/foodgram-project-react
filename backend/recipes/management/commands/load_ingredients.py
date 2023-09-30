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
            for row in DictReader(open("/data/ingredients.csv")):
                ingredient = Ingredient(id=row['id'], name=row['name'],
                                        slug=row['slug'])
                ingredient.save()
                print(f"Ingredient'{ingredient.name}' импортирован.")
        except FileNotFoundError:
            print("CSV file не найден.")
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")
