<h1 align="center">FunPay Cardinal</h1>
<h4 align="center">Простой и эффективный бот для автоматизации FunPay</h4>

<h2 align="center">Перед началом настоятельно рекомендую залететь в наш <a href="https://t.me/funpay_cardinal">Telegram
чат (клик)</a>. Тут и поможем чем сможем и посидеть можно.</h2>

## :clipboard: **Содержание**

- [Возможности](#robot-возможности)
    - [FunPay](#shopping_cart-funpay)
    - [Уведомления и ПУ в Telegram](#left_speech_bubble-уведомления-и-пу-в-telegram)
    - [Дополнительные возможности](#gear-дополнительные-возможности)

- [Преимущества](#1st_place_medal-преимущества)
    - [Для пользователей](#grinning-для-пользователей)
    - [Для разработчиков](#computer-для-разработчиков)

- [Плагины](#electric_plug-плагины)
- [Установка](#arrow_down-установка)
    - [Windows](#large_blue_diamond-windows)
    - [Linux (Ubuntu)](#hotsprings-linux-ubuntu)
- [Установка плагинов](#electric_plug-установка-плагинов)
- [Мне нужна помощь](#question-мне-нужна-помощь)
- [Star it](#star-star-it)

## :robot: **Возможности**

### :shopping_cart: **FunPay**

- Автовыдача товаров.
- Автоподнятие лотов.
- Автоответ на заготовленные команды.
- Автовосстановление лотов после продажи.
- Автодеактивация лотов, если товары закончились.
- Вечный онлайн.
- Уведомления в телеграм.
- Полноценная ПУ в Telegram.

### :left_speech_bubble: **Уведомления и ПУ в Telegram**

- Возможность установки нескольких чатов для уведомлений.
- Уведомления о поднятии лотов.
- Уведомления о новых заказах.
- Уведомления о выдаче товара.
- Уведомления о новых сообщениях
- Возможность отвечать на сообщения прямо из Telegram.
- Возможность полностью настраивать автовыдачу / автоответчик и все остальные модули FPC.
- Возможность добавлять автовыдачу для лотов, получая лоты прямо с FunPay.

### :gear: **Дополнительные возможности**

- Использование переменных в тексте для автоответа / автовыдачи.
- Создание плагинов для кастомизации функционала без редактирования исходного кода самого Кардинала.

## :1st_place_medal: **Преимущества**

### :grinning: **Для пользователей**

- **Больше**, чем наличие самого нужного функционала.
- **Оптимизация**. _20 МБ свободного места на диске, до 50 МБ ОЗУ, доступ в интернет_ - все что нужно для работы.
- Возможность установить на **любую платформу**, которую поддерживает _Python: Windows, Linux, IOS, Android_ и т.д.
- Возможность установки плагинов дает **огромную вариативность** модификации стандартного функционала под самые разные
  нужды.
- Гибкие и при этом простые конфиги, написанные в INI-формате.
- Постоянные обновления, быстрое реагирования на баги / предложения о новом функционале.
- Полное управление через Telegram.

### :computer: **Для разработчиков**

- Выбран самый простой и при этом один из самых мощных языков для такого рода приложений - _Python_.
- Полная документация кода. Все классы / методы / функции имеют док-строки, type-хинты.
- Широкое использование ООП. Почти каждый эвент / сообщение / заказ и т.д. представляют собой экземпляр соответствующего
  класса, а не просто набор данных в JSON.
- Возможность легкого создания плагинов.
- Сконфигурированный логгер. Никаких принтов!
- Собственный Python-пакет FunPayAPI, который никак не привязан к FunPay Cardinal.
- Поддержка лично от меня :)

## :arrow_down: Установка

Арендовать виртуальный сервер можно на [FirstByte](https://firstbyte.ru/). Выбирайте Ubuntu 20+ версии,
остальные параметры не важны.

### :large_blue_diamond: Windows

1. Скачайте и установите [Python 3.11.0](https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe).
    1. При установке поставьте галочку у `Add python.exe to PATH` на первом экране установки.
2. Скачайте [FunPay Cardinal](https://github.com/chtowsappx/FunPayCardinal/archive/refs/heads/master.zip)
3. Перенести папку `FunPayCardinal-main` в нужное Вам место.
4. Перейдите в папку `FunPayCardinal-main`.
5. Запустите файл `Setup.bat`. Дождитесь окончания загрузки пакетов.
6. Закройте командную строку и запустите файл `Start.bat`.

### :hotsprings: Linux (Ubuntu)

1. Выполните команду:
   `wget https://raw.githubusercontent.com/chtowsappx/FunPayCardinal/main/install-fpc.sh -O install-fpc.sh && bash install-fpc.sh`
2. Следуйте инструкциям установщика.
   Данный скрипт автоматически установит всё необходимое и запустит бота как фоновый процесс.

#### Решение проблемы с кодировкой latin-1

Если вы сталкиваетесь с ошибками, связанными с кодировкой latin-1, выполните следующие шаги:

1. Выполните команду:  
   `sudo apt-get install language-pack-ru`
2. Выполните команду:  
   `sudo apt-get install language-pack-gnome-ru`
3. Выполните команду:  
   `sudo apt-get install language-pack-kde-ru`
4. Выполните команду:  
   `exit`
5. Подключитесь к серверу.
6. Выполните команду:  
   `sudo update-locale LANG=ru_RU.utf8`
7. Если возникает ошибка, вернитесь к шагу 4.
8. Повторите попытку установки скрипта:  
   `wget https://raw.githubusercontent.com/chtowsappx/FunPayCardinal/main/install-fpc.sh -O install-fpc.sh && bash install-fpc.sh`
9. Если снова возникает ошибка, вернитесь к шагу 4.

## :electric_plug: Установка плагинов

Не устанавливайте плагины из непроверенных источников. Через систему плагинов злоумышленники могут получить полный
доступ к Вашему устройству или аккаунту FunPay. Установка плагинов крайне проста.

1. Введите команду `/menu` в диалоге с ботом Telegram.
2. Нажмите кнопку `▶️ Далее`.
3. Нажмите кнопку `🧩 Плагины`.
4. Нажмите кнопку `➕ Добавить плагин`.
5. Отправьте или перешлите боту файл плагина.

## :question: Мне нужна помощь

Если у вас остались какие-либо вопросы, мы с радостью ответим на них в
нашем [Telegram чате](https://t.me/funpay_cardinal).

## :star: Star it

Если вам удобно пользоваться FunPay Cardinal, не забудьте поставить :star: звезду :star: данному проекту в правом
верхнем углу GitHub-страницы (нужно быть авторизованным в свой аккаунт) :)
