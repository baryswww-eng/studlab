"""Russian learning content for the demo courses: theory, quiz, practical tasks.

Each course is shown in three sections, in this order:
  1. «Теория»                      — articles below (lesson type TEXT)
  2. «Видеоуроки»                  — YouTube lessons from demo_videos.py (type VIDEO)
  3. «Тесты и практические задания» — QUIZ below + practical TASKS (type ASSIGNMENT)

Question formats:
  {"type": "single" | "multiple", "text": ..., "options": [(text, is_correct), ...], "explanation": ...}
  {"type": "text", "text": ..., "accepted": [answers...], "explanation": ...}
Task "criteria" are hidden from students and given to the AI reviewer.
"""

from typing import Any

CONTENT: dict[str, dict[str, Any]] = {
    # ------------------------------------------------------------------ Python basics
    "python-basics": {
        "theory": [
            (
                "Python: первая программа, переменные и типы данных",
                """## Что такое Python

**Python** — простой и популярный язык программирования. На нём пишут сайты, анализируют данные, создают нейросети и автоматизируют рутину. Код на Python читается почти как английский текст.

## Первая программа

```python
print("Привет, мир!")
```

Функция `print()` выводит текст на экран. Текст пишется в кавычках — это **строка**.

## Переменные

Переменная — это имя, под которым хранится значение. Значение присваивается знаком `=`:

```python
name = "Айгерим"
age = 16
print(name, age)   # Айгерим 16
```

Имя переменной пишут латиницей, без пробелов, не начиная с цифры: `user_name`, `total2`.

## Основные типы данных

| Тип | Пример | Что хранит |
|---|---|---|
| `int` | `42` | целое число |
| `float` | `3.14` | дробное число |
| `str` | `"текст"` | строку |
| `bool` | `True`, `False` | логическое значение |

Узнать тип можно функцией `type()`: `type(3.14)` вернёт `float`.

## Ввод данных и преобразование типов

```python
age = int(input("Сколько тебе лет? "))
print("Через год тебе будет", age + 1)
```

`input()` всегда возвращает строку, поэтому для вычислений её переводят в число через `int()` или `float()`.

## Арифметика

`+  -  *  /` — обычные действия, `//` — целочисленное деление, `%` — остаток, `**` — степень. Например, `7 // 2 == 3`, `7 % 2 == 1`, `2 ** 3 == 8`.
""",
            ),
            (
                "Условия: if, elif, else",
                """## Зачем нужны условия

Программа часто должна выбирать, что делать. Для этого есть оператор `if`.

```python
temperature = 25
if temperature > 20:
    print("Тепло, можно гулять")
else:
    print("Возьми куртку")
```

**Важно:** код внутри условия пишется с **отступом в 4 пробела**. В Python отступы — часть синтаксиса.

## Несколько вариантов — elif

```python
score = 78
if score >= 90:
    grade = "5"
elif score >= 70:
    grade = "4"
elif score >= 50:
    grade = "3"
else:
    grade = "2"
print("Оценка:", grade)
```

Проверки идут сверху вниз; выполняется первая подходящая ветка.

## Операторы сравнения

`==` равно, `!=` не равно, `>`, `<`, `>=`, `<=`.

Не путайте `=` (присваивание) и `==` (сравнение).

## Логические операторы

- `and` — истина, если верны **оба** условия;
- `or` — истина, если верно **хотя бы одно**;
- `not` — отрицание.

```python
age = 15
has_ticket = True
if age >= 12 and has_ticket:
    print("Проходите")
```

## Чётное или нечётное

```python
n = int(input())
if n % 2 == 0:
    print("чётное")
else:
    print("нечётное")
```
""",
            ),
            (
                "Циклы и функции",
                """## Цикл for

`for` повторяет действия для каждого элемента последовательности. Часто используют `range()`:

```python
for i in range(1, 6):
    print(i)        # 1 2 3 4 5
```

`range(1, 6)` даёт числа от 1 **до 5** — правая граница не включается.

## Цикл while

`while` повторяет действия, пока условие истинно:

```python
count = 3
while count > 0:
    print(count)
    count -= 1
print("Старт!")
```

Следите, чтобы условие когда-нибудь стало ложным, иначе цикл будет бесконечным.

`break` — досрочно выйти из цикла, `continue` — перейти к следующему шагу.

## Функции

Функция — именованный блок кода, который можно вызывать много раз.

```python
def greet(name):
    return "Привет, " + name + "!"

print(greet("Данияр"))
```

- `def` объявляет функцию;
- `name` — **параметр**;
- `return` возвращает результат.

## Пример: сумма чисел списка

```python
def total(numbers):
    s = 0
    for x in numbers:
        s += x
    return s

print(total([3, 5, 7]))   # 15
```

## Списки — коротко

Список хранит несколько значений: `marks = [5, 4, 5]`. Элементы нумеруются с нуля: `marks[0]` — первый. `len(marks)` — длина, `marks.append(3)` — добавить элемент.
""",
            ),
        ],
        "quiz": {
            "title": "Тест: основы Python",
            "questions": [
                {
                    "type": "single",
                    "text": "Что выведет `print(7 // 2)`?",
                    "options": [("3.5", False), ("3", True), ("4", False), ("1", False)],
                    "explanation": "`//` — целочисленное деление, дробная часть отбрасывается.",
                },
                {
                    "type": "single",
                    "text": "Какой тип вернёт `input()`?",
                    "options": [("int", False), ("str", True), ("float", False), ("bool", False)],
                    "explanation": "`input()` всегда возвращает строку; число получают через `int()`.",
                },
                {
                    "type": "multiple",
                    "text": "Какие имена переменных допустимы в Python?",
                    "options": [
                        ("user_name", True),
                        ("2name", False),
                        ("total2", True),
                        ("my name", False),
                    ],
                    "explanation": "Имя не может начинаться с цифры и содержать пробелы.",
                },
                {
                    "type": "single",
                    "text": "Какие числа даст `range(1, 4)`?",
                    "options": [("1, 2, 3, 4", False), ("1, 2, 3", True), ("0, 1, 2, 3", False)],
                    "explanation": "Правая граница в `range` не включается.",
                },
                {
                    "type": "text",
                    "text": "Каким ключевым словом объявляется функция в Python?",
                    "accepted": ["def"],
                    "explanation": "Функция объявляется так: `def имя(параметры):`.",
                },
                {
                    "type": "text",
                    "text": "Чему равно `10 % 3`? Введите число.",
                    "accepted": ["1"],
                    "explanation": "`%` — остаток от деления: 10 = 3·3 + 1.",
                },
            ],
        },
        "tasks": [
            {
                "title": "Практика: чётное или нечётное",
                "description": "Напишите программу, которая просит пользователя ввести целое число и выводит `чётное` или `нечётное`.",
                "expected": "Ввод `7` → вывод `нечётное`; ввод `10` → вывод `чётное`.",
                "criteria": "Используется input() и int(); проверка через % 2; используется if/else; вывод слов «чётное»/«нечётное». Синтаксис Python 3 корректен.",
                "format": "code",
            },
            {
                "title": "Практика: калькулятор суммы",
                "description": "Напишите функцию `total(numbers)`, которая принимает список чисел и возвращает их сумму, **не используя** встроенную `sum()`. Покажите пример вызова.",
                "expected": "`total([3, 5, 7])` возвращает `15`, `total([])` возвращает `0`.",
                "criteria": "Объявлена функция total с параметром; сумма считается циклом for/while без sum(); есть return; пустой список даёт 0; есть пример вызова с print.",
                "format": "code",
            },
        ],
    },
    # ------------------------------------------------------------------ Web: HTML/CSS/JS
    "web-html-css-js": {
        "theory": [
            (
                "HTML: структура веб-страницы",
                """## Как устроен сайт

Браузер получает с сервера **HTML** (структура), **CSS** (оформление) и **JavaScript** (поведение) и собирает из них страницу.

## Минимальная страница

```html
<!DOCTYPE html>
<html lang="ru">
  <head>
    <meta charset="UTF-8">
    <title>Моя страница</title>
  </head>
  <body>
    <h1>Привет!</h1>
    <p>Это мой первый сайт.</p>
  </body>
</html>
```

- `<head>` — служебная информация (кодировка, заголовок вкладки);
- `<body>` — то, что видит пользователь.

## Основные теги

| Тег | Назначение |
|---|---|
| `<h1>`…`<h6>` | заголовки |
| `<p>` | абзац |
| `<a href="...">` | ссылка |
| `<img src="..." alt="...">` | картинка (атрибут `alt` обязателен для доступности) |
| `<ul>`, `<ol>`, `<li>` | списки |
| `<div>`, `<span>` | блочный и строчный контейнер |

## Семантика

Семантические теги объясняют смысл блоков: `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<footer>`. Они помогают поисковикам и экранным дикторам.

## Формы

```html
<form>
  <label for="email">Email</label>
  <input id="email" type="email" required>
  <button type="submit">Отправить</button>
</form>
```

Атрибут `for` у `<label>` связывает подпись с полем — по клику на подпись курсор попадает в поле.
""",
            ),
            (
                "CSS: оформление и раскладка",
                """## Как подключить CSS

```html
<link rel="stylesheet" href="style.css">
```

## Правило CSS

```css
h1 {
  color: #7856ff;
  font-size: 32px;
}
```

`h1` — **селектор** (кого оформляем), внутри фигурных скобок — свойства и значения.

## Селекторы

- `p` — все абзацы;
- `.card` — элементы с классом `card` (`<div class="card">`);
- `#logo` — элемент с `id="logo"`;
- `nav a` — ссылки внутри `nav`.

## Блочная модель

Каждый элемент — прямоугольник: **content → padding → border → margin**. Удобно задать `box-sizing: border-box;`, чтобы ширина включала отступы и рамку.

## Flexbox — раскладка в строку или столбец

```css
.menu {
  display: flex;
  justify-content: space-between; /* по горизонтали */
  align-items: center;            /* по вертикали */
  gap: 16px;
}
```

## Grid — раскладка сеткой

```css
.gallery {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}
```

## Адаптивность

Медиазапросы меняют стили на разных экранах:

```css
@media (max-width: 600px) {
  .gallery { grid-template-columns: 1fr; }
}
```
""",
            ),
            (
                "JavaScript: переменные, функции и DOM",
                """## Подключение

```html
<script src="script.js"></script>
```

## Переменные и типы

```js
const name = "Аружан";   // нельзя переприсвоить
let count = 0;           // можно менять
count = count + 1;
```

Типы: `number`, `string`, `boolean`, `null`, `undefined`, `object`, `array`.

## Функции

```js
function sum(a, b) {
  return a + b;
}
const double = (x) => x * 2; // стрелочная функция
```

## Условия и циклы

```js
if (count > 10) {
  console.log("Много");
}
for (let i = 0; i < 3; i++) {
  console.log(i);
}
```

## DOM — управление страницей

DOM — это дерево элементов страницы, доступное из JavaScript.

```js
const title = document.querySelector("h1");
title.textContent = "Новый заголовок";
title.classList.add("active");
```

## События

```js
const button = document.querySelector("#like");
let likes = 0;
button.addEventListener("click", () => {
  likes++;
  button.textContent = `❤ ${likes}`;
});
```

`addEventListener` подписывается на событие (`click`, `input`, `submit` …) и вызывает функцию, когда оно происходит.
""",
            ),
        ],
        "quiz": {
            "title": "Тест: основы веба",
            "questions": [
                {
                    "type": "single",
                    "text": "Какой тег создаёт ссылку?",
                    "options": [
                        ("<link>", False),
                        ("<a>", True),
                        ("<href>", False),
                        ("<url>", False),
                    ],
                    "explanation": 'Ссылка — `<a href="адрес">текст</a>`; `<link>` подключает файлы в `<head>`.',
                },
                {
                    "type": "multiple",
                    "text": "Какие теги являются семантическими?",
                    "options": [
                        ("<header>", True),
                        ("<div>", False),
                        ("<nav>", True),
                        ("<footer>", True),
                    ],
                    "explanation": "`<div>` — универсальный контейнер без смысла.",
                },
                {
                    "type": "single",
                    "text": "Какой селектор выберет элементы с классом `card`?",
                    "options": [
                        ("#card", False),
                        (".card", True),
                        ("card", False),
                        ("*card", False),
                    ],
                    "explanation": "Классы выбираются точкой, id — решёткой.",
                },
                {
                    "type": "single",
                    "text": "Какое свойство включает Flexbox?",
                    "options": [
                        ("display: flex", True),
                        ("flex: on", False),
                        ("position: flex", False),
                    ],
                    "explanation": "Flex-контейнер создаётся свойством `display: flex`.",
                },
                {
                    "type": "single",
                    "text": "Чем `const` отличается от `let`?",
                    "options": [
                        ("const нельзя переприсвоить", True),
                        ("const работает быстрее", False),
                        ("let нельзя изменять", False),
                    ],
                    "explanation": "Переменную `const` нельзя переприсвоить, `let` — можно.",
                },
                {
                    "type": "text",
                    "text": "Какой метод подписывает элемент на событие? (только имя метода)",
                    "accepted": ["addEventListener", "addEventListener()"],
                    "explanation": "`element.addEventListener('click', handler)`.",
                },
            ],
        },
        "tasks": [
            {
                "title": "Практика: карточка профиля",
                "description": "Сверстайте HTML + CSS карточку профиля: фото (`<img>` с `alt`), имя в заголовке, короткое описание и кнопку «Подписаться». Карточка по центру страницы, со скруглёнными углами и тенью.",
                "expected": "Один HTML-файл со стилями в `<style>` или отдельный CSS. Карточка аккуратно выглядит на телефоне.",
                "criteria": "Корректная HTML-структура; есть img с alt, заголовок, абзац, button; CSS: border-radius, box-shadow, центрирование (flex/grid/margin auto); желательно семантика и адаптивность.",
                "format": "code",
            },
            {
                "title": "Практика: счётчик кликов",
                "description": "Сделайте кнопку и число на странице. По клику на кнопку число увеличивается на 1, вторая кнопка «Сброс» обнуляет счётчик. Используйте `addEventListener`.",
                "expected": "HTML с двумя кнопками и элементом для числа + JavaScript.",
                "criteria": "Используются querySelector/getElementById и addEventListener; счётчик хранится в переменной let; обновляется textContent; кнопка сброса обнуляет; нет inline onclick (допустимо, но хуже).",
                "format": "code",
            },
        ],
    },
    # ------------------------------------------------------------------ C# / .NET
    "csharp-dotnet-start": {
        "theory": [
            (
                "C#: синтаксис, типы и методы",
                """## Что такое C# и .NET

**C#** — строго типизированный язык от Microsoft. Программы на нём работают на платформе **.NET**: это сайты и API (ASP.NET Core), игры (Unity), десктоп-приложения.

## Первая программа

```csharp
Console.WriteLine("Привет, C#!");
```

Создать и запустить проект: `dotnet new console -n Hello`, затем `dotnet run`.

## Переменные и типы

```csharp
int age = 17;
double price = 99.5;
string name = "Данияр";
bool isStudent = true;
var city = "Алматы"; // тип выведен автоматически: string
```

Тип переменной задаётся один раз и не меняется — это **строгая типизация**.

## Условия и циклы

```csharp
if (age >= 18) Console.WriteLine("Взрослый");
else Console.WriteLine("Подросток");

for (int i = 0; i < 3; i++) Console.WriteLine(i);

foreach (var n in new[] { 1, 2, 3 }) Console.WriteLine(n);
```

## Методы

```csharp
static int Sum(int a, int b)
{
    return a + b;
}

Console.WriteLine(Sum(2, 3)); // 5
```

У метода есть **тип возвращаемого значения** (`int`), имя и параметры с типами. Если метод ничего не возвращает — `void`.

## Строки

Интерполяция: `$"Меня зовут {name}, мне {age}"`.
""",
            ),
            (
                "ООП: классы, объекты, интерфейсы, LINQ",
                """## Класс и объект

**Класс** — шаблон, **объект** — конкретный экземпляр.

```csharp
public class Student
{
    public string Name { get; set; }
    public int Grade { get; set; }

    public Student(string name, int grade)
    {
        Name = name;
        Grade = grade;
    }

    public string Describe() => $"{Name}, {Grade} класс";
}

var s = new Student("Аружан", 10);
Console.WriteLine(s.Describe());
```

`Name { get; set; }` — **свойство**; конструктор задаёт начальные значения.

## Четыре принципа ООП

- **Инкапсуляция** — скрываем детали (`private`), открываем только нужное (`public`);
- **Наследование** — `class Teacher : Person` получает поля и методы `Person`;
- **Полиморфизм** — один интерфейс, разные реализации (`virtual` / `override`);
- **Абстракция** — выделяем главное, скрывая лишнее.

## Интерфейсы

```csharp
public interface IShape { double Area(); }

public class Circle : IShape
{
    public double R { get; init; }
    public double Area() => Math.PI * R * R;
}
```

Интерфейс задаёт «контракт»: какие методы должны быть у класса.

## LINQ — запросы к коллекциям

```csharp
var numbers = new List<int> { 5, 8, 2, 9 };
var even = numbers.Where(n => n % 2 == 0).ToList();   // [8, 2]
var sorted = numbers.OrderBy(n => n);                 // 2 5 8 9
var total = numbers.Sum();                            // 24
```
""",
            ),
            (
                "ASP.NET Core: первый Web API",
                """## Что такое Web API

Web API принимает HTTP-запросы и возвращает данные (обычно JSON). Так frontend и мобильные приложения общаются с сервером.

## Создание проекта

```bash
dotnet new webapi -n TodoApi
cd TodoApi
dotnet run
```

## Minimal API

```csharp
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

var todos = new List<Todo>();

app.MapGet("/todos", () => todos);
app.MapPost("/todos", (Todo todo) =>
{
    todos.Add(todo);
    return Results.Created($"/todos/{todo.Id}", todo);
});

app.Run();

record Todo(int Id, string Title, bool Done);
```

## HTTP-методы

| Метод | Действие |
|---|---|
| `GET` | получить данные |
| `POST` | создать |
| `PUT` / `PATCH` | изменить |
| `DELETE` | удалить |

## Коды ответов

`200 OK`, `201 Created`, `400 Bad Request`, `404 Not Found`, `500 Internal Server Error`.

## Entity Framework Core

EF Core — ORM: работает с базой данных через C#-классы.

```csharp
public class AppDb : DbContext
{
    public AppDb(DbContextOptions<AppDb> o) : base(o) {}
    public DbSet<Todo> Todos => Set<Todo>();
}
```

Миграции создают таблицы: `dotnet ef migrations add Init`, затем `dotnet ef database update`.
""",
            ),
        ],
        "quiz": {
            "title": "Тест: C# и .NET",
            "questions": [
                {
                    "type": "single",
                    "text": "Какой тип хранит целое число?",
                    "options": [
                        ("double", False),
                        ("int", True),
                        ("string", False),
                        ("bool", False),
                    ],
                    "explanation": "`int` — 32-битное целое число.",
                },
                {
                    "type": "single",
                    "text": "Что означает `void` у метода?",
                    "options": [
                        ("метод ничего не возвращает", True),
                        ("метод приватный", False),
                        ("метод статический", False),
                    ],
                    "explanation": "`void` — отсутствие возвращаемого значения.",
                },
                {
                    "type": "multiple",
                    "text": "Какие из пунктов — принципы ООП?",
                    "options": [
                        ("Инкапсуляция", True),
                        ("Наследование", True),
                        ("Компиляция", False),
                        ("Полиморфизм", True),
                    ],
                    "explanation": "Принципы ООП: инкапсуляция, наследование, полиморфизм, абстракция.",
                },
                {
                    "type": "single",
                    "text": "Что вернёт `new List<int>{1,2,3,4}.Where(n => n % 2 == 0)`?",
                    "options": [("1, 3", False), ("2, 4", True), ("4", False)],
                    "explanation": "`Where` оставляет элементы, для которых условие истинно — чётные.",
                },
                {
                    "type": "single",
                    "text": "Какой HTTP-метод используется для создания ресурса?",
                    "options": [("GET", False), ("POST", True), ("DELETE", False)],
                    "explanation": "POST создаёт новый ресурс, обычно возвращая 201 Created.",
                },
                {
                    "type": "text",
                    "text": "Какой командой запускают .NET-проект из папки проекта? (dotnet …)",
                    "accepted": ["dotnet run", "run"],
                    "explanation": "`dotnet run` собирает и запускает проект.",
                },
            ],
        },
        "tasks": [
            {
                "title": "Практика: класс BankAccount",
                "description": "Напишите класс `BankAccount` со свойствами `Owner` и `Balance` (только чтение снаружи), методами `Deposit(decimal amount)` и `Withdraw(decimal amount)`. Нельзя снять больше, чем есть, и нельзя вносить отрицательные суммы.",
                "expected": "Класс + пример использования в `Main`/top-level коде.",
                "criteria": "Инкапсуляция: Balance с private set; проверки amount > 0 и достаточного баланса (исключение или bool); тип decimal для денег; корректный синтаксис C#; пример вызова.",
                "format": "code",
            },
            {
                "title": "Практика: LINQ-запросы",
                "description": "Есть список студентов `List<Student>` с полями `Name` и `Score`. С помощью LINQ: 1) выберите студентов с баллом ≥ 70, 2) отсортируйте по убыванию балла, 3) посчитайте средний балл всех студентов.",
                "expected": "Код с объявлением класса/record, списком из 4–5 студентов и тремя запросами.",
                "criteria": "Используются Where, OrderByDescending, Average; правильные лямбды; вывод результатов; синтаксис C# корректен.",
                "format": "code",
            },
        ],
    },
    # ------------------------------------------------------------------ SQL
    "sql-postgresql": {
        "theory": [
            (
                "Реляционные базы данных и SELECT",
                """## Что такое реляционная база данных

Данные хранятся в **таблицах**: строки — записи, столбцы — поля. Таблицы связываются между собой через ключи. **PostgreSQL** — одна из самых популярных бесплатных СУБД.

## Пример таблицы `students`

| id | name | city | score |
|---|---|---|---|
| 1 | Айгерим | Алматы | 92 |
| 2 | Данияр | Астана | 75 |
| 3 | Мадина | Алматы | 64 |

- **Первичный ключ** (`PRIMARY KEY`) — уникальный идентификатор строки (`id`).
- **Внешний ключ** (`FOREIGN KEY`) — ссылка на строку другой таблицы.

## Создание таблицы

```sql
CREATE TABLE students (
    id    SERIAL PRIMARY KEY,
    name  TEXT NOT NULL,
    city  TEXT,
    score INTEGER CHECK (score BETWEEN 0 AND 100)
);
```

## Добавление данных

```sql
INSERT INTO students (name, city, score)
VALUES ('Айгерим', 'Алматы', 92);
```

## Выборка — SELECT

```sql
SELECT name, score FROM students;   -- нужные столбцы
SELECT * FROM students;             -- все столбцы
```

## Изменение и удаление

```sql
UPDATE students SET score = 80 WHERE id = 2;
DELETE FROM students WHERE id = 3;
```

**Внимание:** `UPDATE` и `DELETE` без `WHERE` изменят **все** строки таблицы.
""",
            ),
            (
                "Фильтрация, сортировка, агрегаты и JOIN",
                """## WHERE — фильтрация

```sql
SELECT name FROM students WHERE city = 'Алматы' AND score >= 70;
SELECT name FROM students WHERE name LIKE 'А%';     -- начинается на «А»
SELECT name FROM students WHERE score BETWEEN 60 AND 80;
```

## ORDER BY и LIMIT

```sql
SELECT name, score FROM students
ORDER BY score DESC     -- по убыванию
LIMIT 3;                -- первые 3
```

## Агрегатные функции

`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`:

```sql
SELECT COUNT(*) FROM students;
SELECT AVG(score) FROM students;
```

## GROUP BY и HAVING

```sql
SELECT city, AVG(score) AS avg_score
FROM students
GROUP BY city
HAVING AVG(score) > 70;
```

`WHERE` фильтрует строки **до** группировки, `HAVING` — группы **после**.

## JOIN — объединение таблиц

Таблица `courses(id, title)` и `enrollments(student_id, course_id)`:

```sql
SELECT s.name, c.title
FROM enrollments e
JOIN students s ON s.id = e.student_id
JOIN courses  c ON c.id = e.course_id;
```

- `INNER JOIN` — только совпадающие строки;
- `LEFT JOIN` — все строки левой таблицы, даже без пары (поля справа будут `NULL`).
""",
            ),
            (
                "Проектирование: нормализация и индексы",
                """## Зачем проектировать

Плохо спроектированная база дублирует данные и порождает ошибки. Цель — каждый факт хранить **в одном месте**.

## Нормальные формы

- **1НФ** — в каждой ячейке одно значение (не «Python, SQL» в одном поле).
- **2НФ** — каждое неключевое поле зависит от **всего** первичного ключа.
- **3НФ** — неключевые поля не зависят друг от друга (город школы храним в таблице школ, а не у каждого ученика).

## Пример: было → стало

Было: `orders(id, customer_name, customer_phone, product)` — данные клиента повторяются в каждом заказе.

Стало:

```sql
CREATE TABLE customers (id SERIAL PRIMARY KEY, name TEXT, phone TEXT);
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    product TEXT
);
```

## Связи

- **Один ко многим**: один клиент — много заказов (внешний ключ в `orders`).
- **Многие ко многим**: студенты ↔ курсы — через промежуточную таблицу `enrollments`.

## Индексы

Индекс ускоряет поиск, как алфавитный указатель в книге:

```sql
CREATE INDEX idx_students_city ON students(city);
```

Индексы ускоряют `WHERE`, `JOIN` и `ORDER BY`, но замедляют `INSERT`/`UPDATE` и занимают место. Первичный ключ и `UNIQUE` индексируются автоматически.
""",
            ),
        ],
        "quiz": {
            "title": "Тест: SQL и PostgreSQL",
            "questions": [
                {
                    "type": "single",
                    "text": "Какой оператор выбирает данные из таблицы?",
                    "options": [
                        ("GET", False),
                        ("SELECT", True),
                        ("FETCH", False),
                        ("SHOW", False),
                    ],
                    "explanation": "Выборка данных — `SELECT ... FROM ...`.",
                },
                {
                    "type": "single",
                    "text": "Что сделает `DELETE FROM students;` без WHERE?",
                    "options": [
                        ("Удалит все строки", True),
                        ("Удалит таблицу", False),
                        ("Выдаст ошибку", False),
                    ],
                    "explanation": "Без `WHERE` удаляются все строки; таблицу удаляет `DROP TABLE`.",
                },
                {
                    "type": "multiple",
                    "text": "Какие функции являются агрегатными?",
                    "options": [("COUNT", True), ("AVG", True), ("WHERE", False), ("MAX", True)],
                    "explanation": "`WHERE` — условие фильтрации, а не функция.",
                },
                {
                    "type": "single",
                    "text": "Чем HAVING отличается от WHERE?",
                    "options": [
                        ("HAVING фильтрует группы после GROUP BY", True),
                        ("HAVING работает быстрее", False),
                        ("Ничем", False),
                    ],
                    "explanation": "`WHERE` — строки до группировки, `HAVING` — группы после.",
                },
                {
                    "type": "single",
                    "text": "Какой JOIN вернёт все строки левой таблицы, даже без совпадений?",
                    "options": [("INNER JOIN", False), ("LEFT JOIN", True), ("CROSS JOIN", False)],
                    "explanation": "`LEFT JOIN` сохраняет все строки левой таблицы.",
                },
                {
                    "type": "text",
                    "text": "Каким ключевым словом сортируют результат? (два слова)",
                    "accepted": ["order by"],
                    "explanation": "Сортировка — `ORDER BY столбец [ASC|DESC]`.",
                },
            ],
        },
        "tasks": [
            {
                "title": "Практика: база библиотеки",
                "description": "Спроектируйте таблицы для библиотеки: книги, авторы, читатели и выдачи книг (кто, какую книгу, когда взял и вернул). Напишите `CREATE TABLE` с первичными и внешними ключами.",
                "expected": "4 таблицы, связи через внешние ключи, разумные типы и ограничения NOT NULL.",
                "criteria": "Есть таблицы books, authors, readers, loans (названия могут отличаться); PRIMARY KEY в каждой; FOREIGN KEY из loans на books и readers, из books на authors (или таблица связи многие-ко-многим); даты выдачи/возврата; NOT NULL где нужно; синтаксис PostgreSQL.",
                "format": "code",
            },
            {
                "title": "Практика: аналитические запросы",
                "description": "Для таблицы `students(id, name, city, score)` напишите запросы: 1) топ-3 студента по баллу; 2) средний балл по каждому городу; 3) города, где средний балл выше 70.",
                "expected": "Три SQL-запроса с комментариями.",
                "criteria": "1) ORDER BY score DESC LIMIT 3; 2) GROUP BY city с AVG; 3) GROUP BY + HAVING AVG(score) > 70; синтаксис корректен.",
                "format": "code",
            },
        ],
    },
    # ------------------------------------------------------------------ AI / ML
    "ai-machine-learning-intro": {
        "theory": [
            (
                "ИИ, машинное обучение и данные",
                """## ИИ, ML и DL — в чём разница

- **Искусственный интеллект (ИИ)** — общее название систем, которые решают «интеллектуальные» задачи: распознают речь, переводят, играют.
- **Машинное обучение (ML)** — часть ИИ: алгоритм **учится на примерах**, а не следует жёстко прописанным правилам.
- **Глубокое обучение (DL)** — часть ML на основе нейронных сетей со многими слоями (распознавание изображений, ChatGPT).

## Типы задач ML

| Тип | Пример |
|---|---|
| **Регрессия** | предсказать число: цену квартиры |
| **Классификация** | предсказать класс: спам / не спам |
| **Кластеризация** | разбить клиентов на группы без готовых ответов |

Регрессия и классификация — **обучение с учителем** (есть правильные ответы), кластеризация — **без учителя**.

## Данные — основа ML

Данные обычно представляют таблицей: строки — **объекты**, столбцы — **признаки** (features), а то, что предсказываем, — **целевая переменная** (target).

| площадь | комнаты | район | **цена** |
|---|---|---|---|
| 54 | 2 | центр | 32 млн |

## Обучающая и тестовая выборки

Данные делят на две части: на **обучающей** модель учится, на **тестовой** проверяем её на новых примерах. Если модель отлично работает на обучающих данных и плохо на тестовых — это **переобучение**.

## Этапы проекта

1. Постановка задачи → 2. сбор данных → 3. очистка → 4. выбор и обучение модели → 5. оценка качества → 6. использование.
""",
            ),
            (
                "Работа с данными: pandas и визуализация",
                """## pandas

**pandas** — библиотека Python для работы с таблицами.

```python
import pandas as pd

df = pd.read_csv("flats.csv")
print(df.head())        # первые 5 строк
print(df.shape)         # (строки, столбцы)
print(df.describe())    # статистика по числовым столбцам
```

`DataFrame` — таблица, `Series` — один столбец: `df["price"]`.

## Выборка и фильтрация

```python
cheap = df[df["price"] < 30_000_000]
df[["area", "price"]]            # несколько столбцов
df.sort_values("price", ascending=False)
df.groupby("district")["price"].mean()
```

## Очистка данных

```python
df.isna().sum()                  # сколько пропусков в каждом столбце
df = df.dropna(subset=["price"]) # удалить строки без цены
df["rooms"] = df["rooms"].fillna(df["rooms"].median())
df = df.drop_duplicates()
```

Категориальные признаки переводят в числа: `pd.get_dummies(df, columns=["district"])`.

## Визуализация (matplotlib)

```python
import matplotlib.pyplot as plt

plt.scatter(df["area"], df["price"])
plt.xlabel("Площадь, м²")
plt.ylabel("Цена")
plt.title("Цена квартиры от площади")
plt.show()
```

Графики помогают увидеть зависимости, выбросы и ошибки в данных до обучения модели.
""",
            ),
            (
                "Модели: линейная регрессия и классификация",
                """## Линейная регрессия

Предсказывает число по формуле `y = w₁x₁ + w₂x₂ + … + b`. Обучение подбирает веса `w`, чтобы ошибка была минимальной.

```python
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

X = df[["area", "rooms"]]
y = df["price"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)            # обучение
pred = model.predict(X_test)           # предсказание
print(mean_absolute_error(y_test, pred))
```

**MAE** — средняя абсолютная ошибка: на сколько в среднем ошибается модель.

## Классификация

Предсказывает класс. Пример — логистическая регрессия:

```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

clf = LogisticRegression(max_iter=1000)
clf.fit(X_train, y_train)
print(accuracy_score(y_test, clf.predict(X_test)))
```

## Метрики классификации

- **Accuracy** — доля правильных ответов;
- **Precision** — из предсказанных «положительных» сколько верных;
- **Recall** — какую долю настоящих «положительных» модель нашла.

При несбалансированных классах (например, 1% мошеннических операций) accuracy обманчива — смотрят на precision и recall.

## Общая схема scikit-learn

`model = Модель()` → `model.fit(X_train, y_train)` → `model.predict(X_test)` → метрика.
""",
            ),
        ],
        "quiz": {
            "title": "Тест: основы машинного обучения",
            "questions": [
                {
                    "type": "single",
                    "text": "Предсказание цены квартиры — это задача…",
                    "options": [
                        ("классификации", False),
                        ("регрессии", True),
                        ("кластеризации", False),
                    ],
                    "explanation": "Цена — число, значит это регрессия.",
                },
                {
                    "type": "single",
                    "text": "Модель отлично работает на обучающих данных и плохо на новых. Это…",
                    "options": [
                        ("переобучение", True),
                        ("недообучение", False),
                        ("нормализация", False),
                    ],
                    "explanation": "Переобучение — модель «запомнила» примеры вместо закономерностей.",
                },
                {
                    "type": "multiple",
                    "text": "Какие задачи относятся к обучению с учителем?",
                    "options": [
                        ("регрессия", True),
                        ("классификация", True),
                        ("кластеризация", False),
                    ],
                    "explanation": "Кластеризация не использует правильные ответы.",
                },
                {
                    "type": "single",
                    "text": "Какой метод в scikit-learn обучает модель?",
                    "options": [
                        ("train()", False),
                        ("fit()", True),
                        ("learn()", False),
                        ("predict()", False),
                    ],
                    "explanation": "`fit(X, y)` обучает, `predict(X)` предсказывает.",
                },
                {
                    "type": "single",
                    "text": "Что делает `df.isna().sum()`?",
                    "options": [
                        ("считает пропуски по столбцам", True),
                        ("удаляет пропуски", False),
                        ("суммирует все числа", False),
                    ],
                    "explanation": "`isna()` отмечает пропуски, `sum()` считает их по столбцам.",
                },
                {
                    "type": "text",
                    "text": "Как называется библиотека Python для работы с таблицами (DataFrame)?",
                    "accepted": ["pandas"],
                    "explanation": "pandas: `import pandas as pd`.",
                },
            ],
        },
        "tasks": [
            {
                "title": "Практика: анализ таблицы с pandas",
                "description": "Есть файл `students.csv` со столбцами `name, city, math, physics`. Напишите код на pandas, который: загружает файл, выводит количество пропусков, заполняет пропуски медианой, добавляет столбец `avg` (среднее двух предметов) и выводит средний `avg` по каждому городу.",
                "expected": "Код на Python с pandas, по шагам с комментариями.",
                "criteria": "read_csv; isna().sum(); fillna медианой для math/physics; новый столбец avg как среднее; groupby('city')['avg'].mean(); корректный синтаксис.",
                "format": "code",
            },
            {
                "title": "Практика: первая модель регрессии",
                "description": "По таблице квартир (`area`, `rooms`, `price`) обучите линейную регрессию на scikit-learn: разделите данные на обучающую и тестовую выборки (80/20), обучите модель, посчитайте MAE на тесте и объясните своими словами, что означает полученное число.",
                "expected": "Код + 2–3 предложения объяснения.",
                "criteria": "train_test_split с test_size=0.2; LinearRegression().fit на train; predict на test; mean_absolute_error; текстовое объяснение MAE как средней ошибки в единицах цены.",
                "format": "code",
            },
        ],
    },
    # ------------------------------------------------------------------ IT fundamentals
    "it-fundamentals": {
        "theory": [
            (
                "Как устроен компьютер и операционная система",
                """## Основные компоненты

| Компонент | Роль |
|---|---|
| **Процессор (CPU)** | выполняет команды программ |
| **Оперативная память (RAM)** | быстрая временная память для работающих программ; очищается при выключении |
| **Накопитель (SSD/HDD)** | постоянное хранение файлов |
| **Видеокарта (GPU)** | вывод изображения и параллельные вычисления (игры, нейросети) |
| **Материнская плата** | соединяет все компоненты |

Чем больше RAM, тем больше программ и вкладок работает одновременно без замедления. SSD работает в разы быстрее HDD.

## Как хранится информация

Компьютер работает с **битами** (0 и 1). 8 бит = 1 **байт**. 1 КБ ≈ 1000 байт, 1 МБ ≈ 1000 КБ, 1 ГБ ≈ 1000 МБ.

## Операционная система

ОС (Windows, macOS, Linux, Android) — главная программа, которая:

- управляет процессором, памятью и устройствами;
- запускает приложения;
- хранит файлы в **файловой системе** (папки и файлы, пути вроде `C:\\Users\\Ivan\\Documents`).

## Командная строка

Командная строка позволяет управлять компьютером текстовыми командами.

| Действие | Windows (cmd/PowerShell) | Linux/macOS |
|---|---|---|
| где я | `cd` / `pwd` (PowerShell) | `pwd` |
| список файлов | `dir` | `ls` |
| перейти в папку | `cd папка` | `cd папка` |
| создать папку | `mkdir имя` | `mkdir имя` |
""",
            ),
            (
                "Сети и интернет: IP, DNS, HTTP",
                """## Что такое сеть

Сеть — компьютеры, соединённые для обмена данными. **Интернет** — сеть сетей по всему миру.

## IP-адрес

У каждого устройства в сети есть **IP-адрес**, например `142.250.74.46` (IPv4) или длиннее в IPv6. По нему данные находят получателя — как почтовый адрес.

## DNS

Людям удобнее имена, а не цифры. **DNS** переводит доменное имя (`google.com`) в IP-адрес. Это «телефонная книга интернета».

## Что происходит, когда вы открываете сайт

1. Вы вводите `https://example.com`.
2. Браузер спрашивает у DNS IP-адрес домена.
3. Браузер устанавливает соединение с сервером (для HTTPS — защищённое, с шифрованием).
4. Отправляет **HTTP-запрос** `GET /`.
5. Сервер отвечает: код статуса + HTML.
6. Браузер загружает CSS, JS, картинки и отображает страницу.

## HTTP и HTTPS

**HTTP** — протокол обмена между браузером и сервером. **HTTPS** — то же самое, но с шифрованием: данные нельзя прочитать по пути. Значок замка в адресной строке означает HTTPS.

## Коды ответов

- `200` — всё хорошо;
- `301/302` — перенаправление;
- `404` — страница не найдена;
- `500` — ошибка на сервере.
""",
            ),
            (
                "Кибербезопасность: пароли, 2FA, фишинг",
                """## Надёжный пароль

- длина **от 12 символов**;
- не слова из словаря и не даты рождения;
- **разный пароль для каждого сервиса** — если один сайт взломают, остальные аккаунты останутся в безопасности;
- храните пароли в **менеджере паролей** (Bitwarden, 1Password, встроенный в браузер).

Хороший приём — фраза из нескольких случайных слов: `кот-река-лампа-2026`.

## Двухфакторная аутентификация (2FA)

Кроме пароля нужен второй фактор:

- код из приложения (Google Authenticator) или SMS;
- ключ доступа (passkey) или физический ключ.

Даже если пароль украдут, без второго фактора войти не получится. Включайте 2FA для почты и соцсетей в первую очередь.

## Фишинг

Фишинг — попытка выманить пароль или деньги, притворившись доверенной организацией.

Признаки:

- срочность и угрозы («аккаунт заблокируют через час»);
- адрес сайта похож, но отличается: `g00gle.com`, `kaspi-bonus.top`;
- просьба ввести пароль, код из SMS или данные карты;
- неожиданные вложения и ссылки.

**Правило:** не переходите по ссылке из письма — откройте сайт сами, набрав адрес. Никому не сообщайте коды из SMS.

## Базовая гигиена

Обновляйте ОС и программы, скачивайте приложения только из официальных источников, делайте резервные копии важных файлов.
""",
            ),
        ],
        "quiz": {
            "title": "Тест: основы IT",
            "questions": [
                {
                    "type": "single",
                    "text": "Какая память очищается при выключении компьютера?",
                    "options": [("SSD", False), ("RAM", True), ("HDD", False)],
                    "explanation": "Оперативная память (RAM) энергозависима.",
                },
                {
                    "type": "single",
                    "text": "Что делает DNS?",
                    "options": [
                        ("Переводит доменное имя в IP-адрес", True),
                        ("Шифрует данные", False),
                        ("Хранит сайты", False),
                    ],
                    "explanation": "DNS — «телефонная книга»: имя → IP-адрес.",
                },
                {
                    "type": "single",
                    "text": "Что означает код ответа 404?",
                    "options": [
                        ("Ошибка сервера", False),
                        ("Страница не найдена", True),
                        ("Всё хорошо", False),
                    ],
                    "explanation": "404 Not Found — ресурс не найден.",
                },
                {
                    "type": "multiple",
                    "text": "Какие признаки указывают на фишинг?",
                    "options": [
                        ("Срочность и угрозы", True),
                        ("Просьба ввести код из SMS", True),
                        ("Адрес сайта с подменёнными буквами", True),
                        ("Письмо от друга, которого вы ждали, без ссылок", False),
                    ],
                    "explanation": "Срочность, просьба кодов и поддельные адреса — классические признаки.",
                },
                {
                    "type": "single",
                    "text": "Сколько бит в одном байте?",
                    "options": [("4", False), ("8", True), ("16", False)],
                    "explanation": "1 байт = 8 бит.",
                },
                {
                    "type": "text",
                    "text": "Как называется защищённая версия протокола HTTP?",
                    "accepted": ["https"],
                    "explanation": "HTTPS — HTTP с шифрованием (TLS).",
                },
            ],
        },
        "tasks": [
            {
                "title": "Практика: путь запроса в браузере",
                "description": "Опишите своими словами по шагам, что происходит от момента, когда вы ввели в браузере `https://stepik.org`, до появления страницы. Упомяните DNS, IP-адрес, HTTPS, HTTP-запрос и ответ сервера.",
                "expected": "5–8 пронумерованных шагов простым языком.",
                "criteria": "Упомянуты: DNS-запрос и получение IP; установка соединения/TLS для HTTPS; HTTP GET-запрос; ответ сервера с кодом статуса и HTML; загрузка CSS/JS/картинок и отрисовка. Порядок логичный.",
                "format": "text",
            },
            {
                "title": "Практика: аудит своей безопасности",
                "description": "Составьте личный план безопасности: 1) как вы будете создавать и хранить пароли; 2) для каких 3 сервисов включите 2FA и каким способом; 3) три правила, как распознать фишинговое сообщение. **Не пишите настоящие пароли!**",
                "expected": "Три раздела с конкретными пунктами.",
                "criteria": "Уникальные длинные пароли и менеджер паролей; 2FA для почты/соцсетей с конкретным способом (приложение/ключ предпочтительнее SMS); признаки фишинга (срочность, поддельный домен, просьба кодов/паролей). Нет реальных паролей.",
                "format": "text",
            },
        ],
    },
    # ------------------------------------------------------------------ Python OOP
    "python-oop": {
        "theory": [
            (
                "Классы и объекты в Python",
                """## Зачем ООП

Объектно-ориентированное программирование описывает программу как набор **объектов**, у каждого есть **данные** (атрибуты) и **поведение** (методы). Это удобно для больших проектов.

## Класс и объект

```python
class Student:
    school = "STUD LAB"          # атрибут класса — общий для всех

    def __init__(self, name, grade):
        self.name = name         # атрибуты объекта
        self.grade = grade

    def describe(self):
        return f"{self.name}, {self.grade} класс"

a = Student("Аружан", 10)
b = Student("Айбек", 9)
print(a.describe())   # Аружан, 10 класс
print(b.school)       # STUD LAB
```

- `class` объявляет класс;
- `__init__` — **конструктор**, вызывается при создании объекта;
- `self` — ссылка на текущий объект; передаётся автоматически.

## Атрибуты класса и объекта

Атрибут объекта (`self.name`) у каждого свой. Атрибут класса (`school`) общий: если изменить `Student.school`, изменится у всех.

## Методы

Обычный метод получает `self`. Есть также:

```python
class Mathx:
    @staticmethod
    def square(x):          # не нужен ни self, ни cls
        return x * x

    @classmethod
    def info(cls):          # получает сам класс
        return cls.__name__
```
""",
            ),
            (
                "Наследование, полиморфизм, инкапсуляция",
                """## Наследование

Дочерний класс получает атрибуты и методы родителя и может их расширять.

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."

class Dog(Animal):
    def speak(self):
        return "Гав!"

class Cat(Animal):
    def speak(self):
        return "Мяу!"
```

`super()` вызывает метод родителя:

```python
class Puppy(Dog):
    def __init__(self, name, age):
        super().__init__(name)
        self.age = age
```

## Полиморфизм

Один и тот же вызов работает по-разному для разных объектов:

```python
for pet in [Dog("Рекс"), Cat("Мурка")]:
    print(pet.name, pet.speak())
```

## Инкапсуляция

Скрываем внутреннее устройство и даём безопасный доступ. В Python по соглашению:

- `_balance` — «внутренний» атрибут, снаружи трогать не стоит;
- `__balance` — имя искажается (name mangling), доступ снаружи затруднён.

Свойства (`@property`) позволяют проверять значения:

```python
class Account:
    def __init__(self):
        self._balance = 0

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Сумма должна быть положительной")
        self._balance += amount
```
""",
            ),
            (
                "Магические методы, модули и пакеты",
                """## Магические (dunder) методы

Методы с двойными подчёркиваниями задают поведение объектов во встроенных операциях.

```python
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):          # v1 + v2
        return Vector(self.x + other.x, self.y + other.y)

    def __eq__(self, other):           # v1 == v2
        return (self.x, self.y) == (other.x, other.y)

    def __len__(self):                 # len(v)
        return 2

    def __str__(self):                 # print(v)
        return f"Vector({self.x}, {self.y})"

print(Vector(1, 2) + Vector(3, 4))     # Vector(4, 6)
```

- `__str__` — понятное представление для `print`;
- `__repr__` — техническое представление для разработчика.

## Модули

Модуль — это файл `.py`. Код из другого модуля подключают через `import`:

```python
# utils.py
def greet(name):
    return f"Привет, {name}"

# main.py
from utils import greet
print(greet("Мадина"))
```

## Пакеты

Пакет — папка с модулями (обычно с файлом `__init__.py`):

```text
school/
├── __init__.py
├── students.py
└── courses.py
```

`from school.students import Student`.

## if __name__ == "__main__"

Код внутри этого блока выполняется, только если файл запущен напрямую, а не импортирован.
""",
            ),
        ],
        "quiz": {
            "title": "Тест: ООП в Python",
            "questions": [
                {
                    "type": "single",
                    "text": "Как называется метод-конструктор в Python?",
                    "options": [
                        ("__new__", False),
                        ("__init__", True),
                        ("constructor", False),
                        ("__start__", False),
                    ],
                    "explanation": "`__init__` вызывается при создании объекта.",
                },
                {
                    "type": "single",
                    "text": "Что такое `self`?",
                    "options": [
                        ("ссылка на текущий объект", True),
                        ("ключевое слово для импорта", False),
                        ("имя класса", False),
                    ],
                    "explanation": "`self` — первый параметр метода, текущий экземпляр.",
                },
                {
                    "type": "single",
                    "text": "Какой метод вызывается при `print(obj)`?",
                    "options": [("__str__", True), ("__len__", False), ("__add__", False)],
                    "explanation": "`print` использует `__str__` (или `__repr__`, если `__str__` нет).",
                },
                {
                    "type": "multiple",
                    "text": "Что верно о наследовании?",
                    "options": [
                        ("Дочерний класс получает методы родителя", True),
                        ("super() вызывает метод родителя", True),
                        ("Дочерний класс не может переопределять методы", False),
                    ],
                    "explanation": "Методы можно переопределять — это основа полиморфизма.",
                },
                {
                    "type": "single",
                    "text": "Какой декоратор превращает метод в свойство?",
                    "options": [
                        ("@staticmethod", False),
                        ("@property", True),
                        ("@classmethod", False),
                    ],
                    "explanation": "`@property` позволяет обращаться к методу как к атрибуту.",
                },
                {
                    "type": "text",
                    "text": "Какой магический метод отвечает за операцию `a + b`?",
                    "accepted": ["__add__", "add"],
                    "explanation": "Оператор `+` вызывает `__add__`.",
                },
            ],
        },
        "tasks": [
            {
                "title": "Практика: иерархия фигур",
                "description": "Создайте базовый класс `Shape` с методом `area()`, и наследников `Rectangle(width, height)` и `Circle(radius)`, которые переопределяют `area()`. Добавьте `__str__`. Выведите площади списка фигур в цикле.",
                "expected": "Классы + цикл по списку `[Rectangle(3, 4), Circle(1)]` с выводом площади.",
                "criteria": "Наследование от Shape; переопределение area; использование math.pi для круга; __init__ с self; __str__; полиморфный цикл; корректный Python.",
                "format": "code",
            },
            {
                "title": "Практика: банковский счёт с инкапсуляцией",
                "description": "Напишите класс `BankAccount` с защищённым балансом, свойством `balance` только для чтения, методами `deposit` и `withdraw` (с проверками) и `__str__`. Покажите обработку ошибки при снятии слишком большой суммы через `try/except`.",
                "expected": "Класс + пример использования с `try/except`.",
                "criteria": "Атрибут _balance или __balance; @property balance без setter; проверки суммы > 0 и достаточности средств с raise ValueError; try/except в примере; __str__.",
                "format": "code",
            },
        ],
    },
    # ------------------------------------------------------------------ React / Next.js
    "react-nextjs": {
        "theory": [
            (
                "React: компоненты, props и состояние",
                """## Что такое React

**React** — библиотека для создания интерфейсов из **компонентов**. Компонент — функция, которая возвращает разметку (JSX).

```jsx
function Greeting({ name }) {
  return <h1>Привет, {name}!</h1>;
}

export default function App() {
  return <Greeting name="Аружан" />;
}
```

## JSX

JSX похож на HTML, но это JavaScript: выражения пишутся в `{}`, вместо `class` — `className`, у тегов обязательно закрытие (`<img />`).

## Props

**Props** — входные параметры компонента, передаются сверху вниз и **не изменяются** внутри компонента.

## Состояние — useState

```jsx
import { useState } from "react";

function Counter() {
  const [count, setCount] = useState(0);
  return (
    <button onClick={() => setCount(count + 1)}>
      Нажато: {count}
    </button>
  );
}
```

При вызове `setCount` React перерисовывает компонент с новым значением.

## Списки

```jsx
<ul>
  {courses.map((c) => <li key={c.id}>{c.title}</li>)}
</ul>
```

Атрибут `key` должен быть уникальным — так React понимает, какие элементы изменились.

## Эффекты — useEffect

```jsx
useEffect(() => {
  document.title = `Нажато ${count}`;
}, [count]); // выполнится, когда изменится count
```

Пустой массив зависимостей `[]` — эффект выполнится один раз после первого рендера.
""",
            ),
            (
                "Next.js: App Router и серверные компоненты",
                """## Зачем Next.js

**Next.js** — фреймворк на основе React: маршрутизация по файлам, серверный рендеринг, оптимизация изображений и шрифтов, API-маршруты.

## App Router — маршруты из папок

```text
app/
├── layout.tsx          → общий каркас
├── page.tsx            → /
├── courses/
│   ├── page.tsx        → /courses
│   └── [slug]/
│       └── page.tsx    → /courses/python-basics
```

Папка `[slug]` — **динамический сегмент**. В Next.js 15+ параметры асинхронные:

```tsx
export default async function Page({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return <h1>Курс: {slug}</h1>;
}
```

## Серверные и клиентские компоненты

- По умолчанию компоненты **серверные**: выполняются на сервере, могут читать данные напрямую, не попадают в JS-бандл браузера.
- **Клиентские** (`"use client"` в начале файла) нужны для интерактивности: `useState`, обработчики кликов.

## Получение данных

```tsx
export default async function CoursesPage() {
  const res = await fetch("https://api.example.com/courses", {
    next: { revalidate: 60 },   // кэш на 60 секунд
  });
  const courses = await res.json();
  return <ul>{courses.map((c) => <li key={c.id}>{c.title}</li>)}</ul>;
}
```

## Специальные файлы

`loading.tsx` — скелетон при загрузке, `error.tsx` — экран ошибки, `not-found.tsx` — страница 404.
""",
            ),
            (
                "TypeScript и аутентификация в веб-приложениях",
                """## TypeScript

TypeScript — JavaScript с типами: ошибки находятся **до запуска** программы.

```ts
type Course = {
  id: number;
  title: string;
  isFree: boolean;
  tags?: string[];          // необязательное поле
};

function formatTitle(course: Course): string {
  return course.isFree ? `${course.title} (бесплатно)` : course.title;
}
```

Типизация props в React:

```tsx
function CourseCard({ course }: { course: Course }) {
  return <h3>{formatTitle(course)}</h3>;
}
```

Избегайте `any` — он отключает проверку типов.

## Аутентификация: основные понятия

- **Аутентификация** — кто вы (вход по паролю).
- **Авторизация** — что вам разрешено (роли и права).

## Как хранить сессию

Надёжный вариант — **HttpOnly-cookie**, которую ставит сервер после входа: JavaScript не может её прочитать, поэтому XSS-атака не украдёт токен. Флаги `Secure` (только HTTPS) и `SameSite=Lax` защищают от перехвата и CSRF.

Хранить токены в `localStorage` рискованно: любой внедрённый скрипт их прочитает.

## Пароли

Сервер никогда не хранит пароль в открытом виде — только **хеш** (bcrypt, Argon2). При входе хешируется введённый пароль и сравнивается с сохранённым.

## Защита страниц

Проверка прав в интерфейсе — только для удобства. **Настоящая проверка всегда на сервере**: каждый запрос к API проверяет, вошёл ли пользователь и есть ли у него доступ.
""",
            ),
        ],
        "quiz": {
            "title": "Тест: React и Next.js",
            "questions": [
                {
                    "type": "single",
                    "text": "Какой хук хранит состояние компонента?",
                    "options": [
                        ("useEffect", False),
                        ("useState", True),
                        ("useRef", False),
                        ("useMemo", False),
                    ],
                    "explanation": "`useState` возвращает значение и функцию для его изменения.",
                },
                {
                    "type": "single",
                    "text": "Можно ли изменять props внутри компонента?",
                    "options": [
                        ("Нет, props только для чтения", True),
                        ("Да, напрямую", False),
                        ("Только в useEffect", False),
                    ],
                    "explanation": "Props неизменяемы; для изменяемых данных используют состояние.",
                },
                {
                    "type": "single",
                    "text": "Какой путь создаст файл `app/courses/[slug]/page.tsx`?",
                    "options": [("/courses", False), ("/courses/:slug", True), ("/[slug]", False)],
                    "explanation": "`[slug]` — динамический сегмент URL.",
                },
                {
                    "type": "multiple",
                    "text": "Что нужно, чтобы использовать useState в Next.js App Router?",
                    "options": [
                        ('Директива "use client" в файле', True),
                        ("Компонент должен быть клиентским", True),
                        ("Файл должен называться client.tsx", False),
                    ],
                    "explanation": "Хуки состояния работают только в клиентских компонентах.",
                },
                {
                    "type": "single",
                    "text": "Где безопаснее всего хранить токен сессии?",
                    "options": [
                        ("В HttpOnly-cookie", True),
                        ("В localStorage", False),
                        ("В глобальной переменной window", False),
                    ],
                    "explanation": "HttpOnly-cookie недоступна JavaScript, значит XSS её не украдёт.",
                },
                {
                    "type": "text",
                    "text": "Какой атрибут обязателен у элементов списка в React (`.map`)?",
                    "accepted": ["key"],
                    "explanation": "`key` помогает React отслеживать элементы списка.",
                },
            ],
        },
        "tasks": [
            {
                "title": "Практика: список задач на React",
                "description": "Сделайте компонент `TodoList`: поле ввода, кнопка «Добавить», список задач. По клику на задачу она зачёркивается (выполнена), кнопка × удаляет задачу. Используйте `useState`.",
                "expected": "Код компонента на React (JSX или TSX).",
                "criteria": "useState для массива задач и текста ввода; добавление без мутации (spread/concat); map с уникальным key; переключение done; удаление через filter; контролируемый input.",
                "format": "code",
            },
            {
                "title": "Практика: страница курса в Next.js",
                "description": "Напишите серверный компонент `app/courses/[slug]/page.tsx`, который получает `slug` из `params`, загружает курс через `fetch` с `https://api.example.com/courses/{slug}` и показывает название и описание. Если курс не найден (404) — вызовите `notFound()`. Добавьте типы TypeScript.",
                "expected": "Код страницы на TSX.",
                "criteria": 'Асинхронный серверный компонент; await params; fetch с проверкой res.ok/статуса 404 → notFound(); тип Course; без "use client"; корректный TSX.',
                "format": "code",
            },
        ],
    },
}
