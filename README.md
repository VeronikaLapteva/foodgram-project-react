# Проект Продуктовый помощник
Проект Продуктовый помощник позволяет регистрироваться на сайте, входить под своим аккаунтом, добавлять, редактировать и удалять и рецепты, есть возможность добавлять рецепты в корзину, которая собирает и суммируте информацию для списка покупок, а также просматривать записи других пользователей, подписываться на них и добавлять в корзину чужие рецепты. Список покупок есть возможность сохранить и в дальнейшем распечатать.

## Технологии проекта
Python 3.9, Django3, Nginx, Gunicorn, Django REST framework, Certbot, Docker

## Как запустить проект на сервере:
 - Клонируем проект https://github.com/VeronikaLapteva/foodgram-project-react.git
 - Подключаемся к удаленному серверу и создаем на нем папку под названием foodgram
 - Устанавливаем Nginx
   ```
   sudo apt install nginx -y
   sudo systemctl start nginx
   ```
  - Через редактор Nano открываем файл конфигурации веб-сервера и вписываеми необходимые настройки:
   ```
   sudo nano /etc/nginx/sites-enabled/default
   ```
 - Проверияем корректность настроек Nginx:
   ```
   sudo nginx -t
   ```
 - Перезапускаем Nginx:
   ```
   sudo service nginx reload
   ```
 - Устанавливаем Cerbot и получаем SSL-сертификат
   ```
   sudo apt install snapd
   sudo certbot --nginx
   ```
- Копируем файлы docker-compose.production.yml и .env (создаем и заполняем по примеру показанному в файле .env.example) в папку проекта foodgram
- Запускаем Docker Compose на сервере в режиме демона
  ```
  sudo docker compose -f docker-compose.production.yml up -d
  ```
- Проверяем все ли контейнеры запущены
  ```
  sudo docker compose -f docker-compose.yml ps
   ```
- Выполните миграции, соберите статические файлы бэкенда и скопируйте их в /backend_static/static/:
  ```
  sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
  sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
  sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/ 
  ```


## Автор
* [Veronika_Lapteva](https://github.com/VeronikaLapteva)  
