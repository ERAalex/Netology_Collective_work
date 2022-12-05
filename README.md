<h1 align="center">Hi there, we are Alex, Aleksandra, Sergei 
<img src="https://github.com/blackcater/blackcater/raw/main/images/Hi.gif" height="32"/></h1>
<h3 align="center">Computer science students</h3>



[![Typing SVG](https://readme-typing-svg.herokuapp.com?color=%2336BCF7&lines=Python+developers+from+Russia)](https://git.io/typing-svg)

# VKfinderBot

## Описание

Чат-бот поможет вам найти людей из социальной сети ВКонтекте по выбранным параметрам:
* **возраст**
* **город**
* **пол**

А так же отсортирует полученную выборку пользователей исходя из сопадений с вашими интересами, которые вы указали на своей странице ВКонтакте
Бот связан с базой данных (**PostgreSQL**), что позволяет хранить информацию о пользователях, сохранять выбранные ими анкеты, удалять из выбранных или помещать анкеты в бан-лист, чтобы больеш не видеть в выдаче. 
Так же реализованы сессии пользователей в базе данных, каждый пользователь может находиться на разных уровнях взаимодействия с ботом и ничего при этом не должно даже упасть.

*бот написан в рамках учебной программы начинающими питонистами, так что будьте готовы ко всему, заглядывая внутрь.*

## Инструкция
### :running:
1. Перед началом использования склонируйте данный репозиторий себе на устройство
```pytnhon
git clone git@github.com:ERAalex/Netology_Collective_work.git
```
## 	:toolbox:
2. Далее установите все используемые библиотеки
```python
pip install -r requirements.txt
```
### :key: 
3. Заполните авторизационные переменные в файле **settings.ini**:
```python
[VKONTAKTE]
token_user = 
token_community = 
[DATABASE]
username = 
password =
```
> в переменную **token_user** кладем access token [как получить?](https://dzen.ru/media/kakprosto/kak-poluchit-accesstoken-vkontakte-5d72243d06cc4600ad8cb5f3 "Хорошоя инструкция")

> в переменную **token_communit** кладем токен сообщества [как создать сообщество в ВК?](https://dzen.ru/media/propromotion/kak-sozdat-gruppu-vkontakte-poshagovaia-instrukciia-5cb5d73aeb4c5d00b3cb39d7 "Еще одна хорошая интструкция")

> переменные в DATABASE заполняем тем же, чем вы логинитесь в **postrges**
### :running:
4. Запустите файл ```python main.py```
---------------------------------------

<!-- Contact -->
## :handshake: Contact

Use this section to mention useful resources and libraries that you have used in your projects.

 - [Sergei Mochalov](https://github.com/n0iz3on3)
 - [Alex Espinosa](https://github.com/ERAalex)
 - [Aleksandra](https://github.com/TsaregorodtsevaA)


