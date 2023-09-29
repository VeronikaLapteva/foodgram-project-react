# Проект Продуктовый помощник
Проект Продуктовый помощник позволяет регистрироваться на сайте ***https://lbeebox.ddnsking.com***, входить под своим аккаунтом, добавлять, редактировать и удалять и рецепты, есть возможность доюавлять рецепты в корзину, которая собирает и суммируте информацию для списка покупок, а также просматривать записи других пользователей, подписываться на них и добавлять в корзину чужие рецепты.

## Технологии проекта
Python 3.9, Django3, Nginx, Gunicorn, React, Django REST framework, Certbot, Docker

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
 - Устанавливаем Cerbot и получаем SSL-сертификат
   ```
   sudo apt install snapd
   sudo certbot --nginx
   ```
- Копируем файлы docker-compose.production.yml и .env (создаем и заполняем по примеру показанному в файле .env.example) в папку проекта foodgram
- Запускаем прооет на сервере в контейнерах
  ```
  sudo docker compose -f docker-compose.yml up -d
  ```
- Проверяем все ли контейнеры запущены
  ```
  sudo docker compose -f docker-compose.yml ps
   ```
- Проверяем доступность приложения в браузере по ссылке  ***https://lbeebox.ddnsking.com***, регистрируемся и добавляем новые рецепты.

## Автор
Лаптева Вероника  
