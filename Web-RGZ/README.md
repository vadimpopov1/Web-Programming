# Web-RGZ - Видеохостинг Loomix

Loomix - это современная платформа для размещения и просмотра видео, разработанная как расчетно-графическая работа по веб-программированию.

## Основные возможности

- 📹 Загрузка и просмотр видео в формате MP4
- 🔐 Регистрация и аутентификация пользователей
- ✉️ Подтверждение email через код доступа
- 💬 Комментирование видео
- ❤️ Система лайков
- 🌍 Поддержка русского и английского языков
- 🔍 Поиск по видео и пользователям

## Технологии

- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: Python, Flask
- **База данных**: SQLite
- **Дополнительно**: 
  - Flask-SQLAlchemy (ORM)
  - Flask-WTF (формы)
  - Flask-Babel (интернационализация)
  - JWT (аутентификация)

## Установка и запуск

1. Клонируйте репозиторий:
```bash
   git clone https://github.com/vadimpopov1/Web-Programming.git
   cd Web-Programming/Web-RGZ
   ```
2. Установите зависимости:
```bash
  pip install -r requirements.txt
  ```
3. Запустите приложение:
```bash
  python main.py
  ```
## Структура проекта:
    Web-RGZ/
    ├── static/              # Статические файлы (CSS, JS, изображения)
    │   ├── uploads/         # Загруженные видео
    │   └── styles/          # Стили CSS
    ├── templates/           # HTML шаблоны
    ├── translations/        # Файлы перевода
    ├── main.py              # Основное приложение Flask
    ├── requirements.txt     # Зависимости Python
    └── videos.db            # База данных SQLite
