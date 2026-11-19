"""Seed DEMO catalog data (categories, demo instructors, courses).

Every course and instructor created here has is_demo=True and is shown with a "Demo"
badge in the UI. Demo instructors have an unusable password hash and cannot sign in.

Usage (from backend/):
    python -m app.scripts.seed_demo          # create missing demo data
    python -m app.scripts.seed_demo --reset  # delete demo data, then recreate
"""

import argparse
import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import SessionLocal, engine
from app.models import (
    Answer,
    Assignment,
    Category,
    Course,
    CourseLevel,
    CourseStatus,
    CourseTranslation,
    Lesson,
    LessonTranslation,
    LessonType,
    Module,
    Question,
    QuestionType,
    Quiz,
    Role,
    RoleName,
    User,
    UserProfile,
)
from app.scripts.demo_content import CONTENT
from app.scripts.demo_videos import DEMO_VIDEOS, youtube_url

UNUSABLE_PASSWORD = "!demo-account-no-login"  # noqa: S105 — not a valid hash, login impossible

T, V, Q, A = LessonType.TEXT, LessonType.VIDEO, LessonType.QUIZ, LessonType.ASSIGNMENT

CATEGORIES = [
    ("python", "Python", "Python", "python"),
    ("web-development", "Web Development", "Web-разработка", "globe"),
    ("csharp-dotnet", "C# / .NET", "C# / .NET", "braces"),
    ("databases-sql", "Дерекқор / SQL", "Базы данных / SQL", "database"),
    ("artificial-intelligence", "Жасанды интеллект", "Искусственный интеллект", "brain"),
    ("it-fundamentals", "IT негіздері", "Основы IT", "cpu"),
]

INSTRUCTORS = [
    ("demo.aigerim@studlab.local", "Айгерім Сейітова", "Python & Data Science"),
    ("demo.daniyar@studlab.local", "Данияр Омаров", "Full-stack Web / .NET"),
    ("demo.madina@studlab.local", "Мадина Ахметова", "Databases & IT Fundamentals"),
]

# (slug, category, instructor_idx, level, price, featured, kk{...}, ru{...}, modules)
# modules: [(kk, ru, [(kk, ru, type, minutes, preview), ...]), ...]
COURSES = [
    {
        "slug": "python-basics",
        "category": "python",
        "instructor": 0,
        "level": CourseLevel.BEGINNER,
        "price": "0",
        "featured": True,
        "kk": {
            "title": "Python негіздері",
            "short": "Бағдарламалауды нөлден бастап Python тілінде үйреніңіз.",
            "description": "Курс бағдарламалауды бұрын көрмеген адамдарға арналған. "
            "Айнымалылардан бастап функцияларға дейін қадам-қадаммен өтіп, "
            "әр тақырыптан кейін практикалық тапсырма орындайсыз.",
            "outcomes": [
                "Python-да айнымалылар мен деректер типтерін қолдану",
                "Шарттар мен циклдар арқылы логика құру",
                "Функциялар жазу және кодты бөліктерге бөлу",
                "Тізімдермен және сөздіктермен жұмыс істеу",
            ],
            "requirements": ["Компьютер және интернет", "Алдын ала білім қажет емес"],
        },
        "ru": {
            "title": "Основы Python",
            "short": "Изучите программирование с нуля на языке Python.",
            "description": "Курс для тех, кто никогда не программировал. "
            "Шаг за шагом пройдёте путь от переменных до функций "
            "и после каждой темы выполните практическое задание.",
            "outcomes": [
                "Использовать переменные и типы данных в Python",
                "Строить логику с помощью условий и циклов",
                "Писать функции и разбивать код на части",
                "Работать со списками и словарями",
            ],
            "requirements": ["Компьютер и интернет", "Предварительные знания не нужны"],
        },
        "modules": [
            (
                "Кіріспе",
                "Введение",
                [
                    ("Python деген не?", "Что такое Python?", V, 8, True),
                    ("Ортаны орнату", "Установка окружения", T, 12, True),
                    ("Алғашқы бағдарлама", "Первая программа", A, 15, False),
                ],
            ),
            (
                "Айнымалылар және шарттар",
                "Переменные и условия",
                [
                    ("Айнымалылар мен типтер", "Переменные и типы", V, 14, False),
                    ("if / elif / else", "if / elif / else", T, 12, False),
                    ("Тест: негізгі синтаксис", "Тест: базовый синтаксис", Q, 10, False),
                ],
            ),
            (
                "Циклдар және функциялар",
                "Циклы и функции",
                [
                    ("for және while", "for и while", V, 16, False),
                    ("Функциялар", "Функции", T, 18, False),
                    ("Шағын жоба: калькулятор", "Мини-проект: калькулятор", A, 30, False),
                ],
            ),
        ],
    },
    {
        "slug": "web-html-css-js",
        "category": "web-development",
        "instructor": 1,
        "level": CourseLevel.BEGINNER,
        "price": "0",
        "featured": True,
        "kk": {
            "title": "Веб-әзірлеу: HTML, CSS, JavaScript",
            "short": "Алғашқы веб-сайтыңызды нөлден жасап, интернетке шығарыңыз.",
            "description": "HTML арқылы бет құрылымын, CSS арқылы дизайнды, "
            "JavaScript арқылы интерактивтілікті үйренесіз. "
            "Курс соңында өзіңіздің портфолио сайтыңыз дайын болады.",
            "outcomes": [
                "Семантикалық HTML белгілеуін жазу",
                "Flexbox және Grid арқылы адаптивті макет жасау",
                "JavaScript-пен DOM-ды басқару",
                "Сайтты хостингке жариялау",
            ],
            "requirements": ["Компьютерді сенімді пайдалану", "Мәтіндік редактор"],
        },
        "ru": {
            "title": "Веб-разработка: HTML, CSS, JavaScript",
            "short": "Создайте свой первый сайт с нуля и опубликуйте его в интернете.",
            "description": "Вы изучите структуру страницы на HTML, дизайн на CSS "
            "и интерактивность на JavaScript. "
            "К концу курса у вас будет собственный сайт-портфолио.",
            "outcomes": [
                "Писать семантическую HTML-разметку",
                "Делать адаптивные макеты с Flexbox и Grid",
                "Управлять DOM с помощью JavaScript",
                "Публиковать сайт на хостинге",
            ],
            "requirements": ["Уверенное владение компьютером", "Текстовый редактор"],
        },
        "modules": [
            (
                "HTML",
                "HTML",
                [
                    ("Веб қалай жұмыс істейді", "Как работает веб", V, 10, True),
                    ("Тегтер және құрылым", "Теги и структура", T, 15, True),
                    ("Формалар", "Формы", T, 12, False),
                ],
            ),
            (
                "CSS",
                "CSS",
                [
                    ("Селекторлар және түстер", "Селекторы и цвета", V, 14, False),
                    ("Flexbox және Grid", "Flexbox и Grid", T, 20, False),
                    ("Адаптивті дизайн", "Адаптивный дизайн", A, 25, False),
                ],
            ),
            (
                "JavaScript",
                "JavaScript",
                [
                    ("JS негіздері", "Основы JS", V, 18, False),
                    ("DOM және оқиғалар", "DOM и события", T, 20, False),
                    ("Тест: веб негіздері", "Тест: основы веба", Q, 10, False),
                ],
            ),
        ],
    },
    {
        "slug": "csharp-dotnet-start",
        "category": "csharp-dotnet",
        "instructor": 1,
        "level": CourseLevel.INTERMEDIATE,
        "price": "0",
        "featured": True,
        "kk": {
            "title": "C# және .NET: бастапқы деңгейден жобаға дейін",
            "short": "C# тілінде ООП-ты меңгеріп, ASP.NET Core-да API жасаңыз.",
            "description": "Курс C# синтаксисін, объектіге бағытталған бағдарламалауды "
            "және ASP.NET Core арқылы веб-API жасауды қамтиды. "
            "Әр модуль нақты жобаның бір бөлігін құрайды.",
            "outcomes": [
                "C# синтаксисі мен типтер жүйесін түсіну",
                "Класстар, интерфейстер және мұрагерлік",
                "LINQ арқылы деректерді өңдеу",
                "ASP.NET Core-да REST API жасау",
            ],
            "requirements": [
                "Кез келген тілде бағдарламалау негіздері",
                "Visual Studio немесе VS Code",
            ],
        },
        "ru": {
            "title": "C# и .NET: от основ до проекта",
            "short": "Освойте ООП на C# и создайте API на ASP.NET Core.",
            "description": "Курс охватывает синтаксис C#, объектно-ориентированное "
            "программирование и создание веб-API на ASP.NET Core. "
            "Каждый модуль — часть реального проекта.",
            "outcomes": [
                "Понимать синтаксис и систему типов C#",
                "Классы, интерфейсы и наследование",
                "Обработка данных с помощью LINQ",
                "Создание REST API на ASP.NET Core",
            ],
            "requirements": ["Основы программирования на любом языке", "Visual Studio или VS Code"],
        },
        "modules": [
            (
                "C# синтаксисі",
                "Синтаксис C#",
                [
                    ("Типтер және айнымалылар", "Типы и переменные", V, 15, True),
                    ("Әдістер", "Методы", T, 15, False),
                    ("Тест: синтаксис", "Тест: синтаксис", Q, 10, False),
                ],
            ),
            (
                "ООП",
                "ООП",
                [
                    ("Класстар мен объектілер", "Классы и объекты", V, 20, False),
                    ("Интерфейстер", "Интерфейсы", T, 18, False),
                    ("LINQ", "LINQ", T, 20, False),
                ],
            ),
            (
                "ASP.NET Core",
                "ASP.NET Core",
                [
                    ("Алғашқы API", "Первый API", V, 25, False),
                    ("Entity Framework Core", "Entity Framework Core", T, 25, False),
                    ("Жоба: Todo API", "Проект: Todo API", A, 45, False),
                ],
            ),
        ],
    },
    {
        "slug": "sql-postgresql",
        "category": "databases-sql",
        "instructor": 2,
        "level": CourseLevel.BEGINNER,
        "price": "0",
        "featured": True,
        "kk": {
            "title": "SQL және PostgreSQL",
            "short": "Дерекқордан деректерді алу, сүзу және біріктіруді үйреніңіз.",
            "description": "Реляциялық дерекқорлардың негізгі ұғымдарынан бастап "
            "күрделі JOIN және агрегация сұраныстарына дейін. "
            "Барлық мысалдар PostgreSQL-де орындалады.",
            "outcomes": [
                "SELECT, WHERE, ORDER BY сұраныстарын жазу",
                "JOIN арқылы кестелерді біріктіру",
                "GROUP BY және агрегат функциялар",
                "Кестелер мен индекстерді жобалау",
            ],
            "requirements": ["Алдын ала білім қажет емес"],
        },
        "ru": {
            "title": "SQL и PostgreSQL",
            "short": "Научитесь получать, фильтровать и объединять данные из базы.",
            "description": "От базовых понятий реляционных баз данных "
            "до сложных запросов с JOIN и агрегацией. "
            "Все примеры выполняются в PostgreSQL.",
            "outcomes": [
                "Писать запросы SELECT, WHERE, ORDER BY",
                "Объединять таблицы с помощью JOIN",
                "GROUP BY и агрегатные функции",
                "Проектировать таблицы и индексы",
            ],
            "requirements": ["Предварительные знания не нужны"],
        },
        "modules": [
            (
                "Дерекқор негіздері",
                "Основы баз данных",
                [
                    ("Реляциялық модель", "Реляционная модель", V, 10, True),
                    ("PostgreSQL орнату", "Установка PostgreSQL", T, 12, False),
                    ("Алғашқы SELECT", "Первый SELECT", T, 14, False),
                ],
            ),
            (
                "Сұраныстар",
                "Запросы",
                [
                    ("Сүзу және сұрыптау", "Фильтрация и сортировка", V, 15, False),
                    ("JOIN", "JOIN", T, 20, False),
                    ("Тест: сұраныстар", "Тест: запросы", Q, 10, False),
                ],
            ),
            (
                "Жобалау",
                "Проектирование",
                [
                    ("Нормализация", "Нормализация", V, 18, False),
                    ("Индекстер", "Индексы", T, 15, False),
                    ("Жоба: кітапхана дерекқоры", "Проект: база библиотеки", A, 35, False),
                ],
            ),
        ],
    },
    {
        "slug": "ai-machine-learning-intro",
        "category": "artificial-intelligence",
        "instructor": 0,
        "level": CourseLevel.INTERMEDIATE,
        "price": "0",
        "featured": True,
        "kk": {
            "title": "Жасанды интеллект және машиналық оқыту",
            "short": "ML негіздерін түсініп, Python-да алғашқы модельдерді үйретіңіз.",
            "description": "Курс машиналық оқытудың негізгі идеяларын түсіндіреді: "
            "деректерді дайындау, модельді үйрету және бағалау. "
            "Практика scikit-learn кітапханасында жүреді.",
            "outcomes": [
                "ML есептерінің түрлерін ажырату",
                "pandas арқылы деректерді дайындау",
                "Регрессия және классификация модельдерін үйрету",
                "Модель сапасын метрикалармен бағалау",
            ],
            "requirements": ["Python негіздері", "Мектеп математикасы"],
        },
        "ru": {
            "title": "Искусственный интеллект и машинное обучение",
            "short": "Поймите основы ML и обучите первые модели на Python.",
            "description": "Курс объясняет ключевые идеи машинного обучения: "
            "подготовку данных, обучение и оценку моделей. "
            "Практика проходит в библиотеке scikit-learn.",
            "outcomes": [
                "Различать типы задач ML",
                "Готовить данные с помощью pandas",
                "Обучать модели регрессии и классификации",
                "Оценивать качество модели метриками",
            ],
            "requirements": ["Основы Python", "Школьная математика"],
        },
        "modules": [
            (
                "ЖИ-ге кіріспе",
                "Введение в ИИ",
                [
                    ("ЖИ, ML және DL", "ИИ, ML и DL", V, 12, True),
                    ("Деректер — ML негізі", "Данные — основа ML", T, 15, False),
                    ("Тест: негізгі ұғымдар", "Тест: основные понятия", Q, 10, False),
                ],
            ),
            (
                "Деректермен жұмыс",
                "Работа с данными",
                [
                    ("pandas негіздері", "Основы pandas", V, 20, False),
                    ("Деректерді тазалау", "Очистка данных", T, 18, False),
                    ("Визуализация", "Визуализация", T, 15, False),
                ],
            ),
            (
                "Модельдер",
                "Модели",
                [
                    ("Сызықтық регрессия", "Линейная регрессия", V, 22, False),
                    ("Классификация", "Классификация", T, 22, False),
                    ("Жоба: үй бағасын болжау", "Проект: прогноз цен на жильё", A, 45, False),
                ],
            ),
        ],
    },
    {
        "slug": "it-fundamentals",
        "category": "it-fundamentals",
        "instructor": 2,
        "level": CourseLevel.BEGINNER,
        "price": "0",
        "featured": True,
        "kk": {
            "title": "IT негіздері",
            "short": "Компьютер, желі және интернет қалай жұмыс істейтінін түсініңіз.",
            "description": "IT саласына алғашқы қадам: аппараттық және бағдарламалық "
            "қамтама, операциялық жүйелер, желілер және киберқауіпсіздік негіздері.",
            "outcomes": [
                "Компьютердің негізгі компоненттерін түсіну",
                "Операциялық жүйе және файлдық жүйе",
                "Желілер мен интернеттің жұмыс принципі",
                "Қауіпсіздіктің негізгі ережелері",
            ],
            "requirements": ["Алдын ала білім қажет емес"],
        },
        "ru": {
            "title": "Основы IT",
            "short": "Разберитесь, как работают компьютер, сети и интернет.",
            "description": "Первый шаг в IT: аппаратное и программное обеспечение, "
            "операционные системы, сети и основы кибербезопасности.",
            "outcomes": [
                "Понимать основные компоненты компьютера",
                "Операционная и файловая система",
                "Принцип работы сетей и интернета",
                "Базовые правила безопасности",
            ],
            "requirements": ["Предварительные знания не нужны"],
        },
        "modules": [
            (
                "Компьютер",
                "Компьютер",
                [
                    ("Аппараттық қамтама", "Аппаратное обеспечение", V, 10, True),
                    ("Операциялық жүйелер", "Операционные системы", T, 12, False),
                    ("Командалық жол", "Командная строка", T, 15, False),
                ],
            ),
            (
                "Желілер",
                "Сети",
                [
                    ("IP, DNS, HTTP", "IP, DNS, HTTP", V, 15, False),
                    ("Браузер қалай жұмыс істейді", "Как работает браузер", T, 12, False),
                    ("Тест: желілер", "Тест: сети", Q, 10, False),
                ],
            ),
            (
                "Қауіпсіздік",
                "Безопасность",
                [
                    ("Құпиясөздер және 2FA", "Пароли и 2FA", V, 10, False),
                    ("Фишингті тану", "Распознавание фишинга", T, 10, False),
                    ("Тапсырма: қауіпсіздік аудиті", "Задание: аудит безопасности", A, 20, False),
                ],
            ),
        ],
    },
    {
        "slug": "python-oop",
        "category": "python",
        "instructor": 0,
        "level": CourseLevel.INTERMEDIATE,
        "price": "0",
        "featured": False,
        "kk": {
            "title": "Python: объектіге бағытталған бағдарламалау",
            "short": "Класстар, мұрагерлік және таза код принциптері.",
            "description": "Python негіздерін білетіндерге арналған келесі қадам. "
            "ООП принциптерін, ерекше әдістерді және жоба құрылымын үйренесіз.",
            "outcomes": [
                "Класстар мен объектілерді жобалау",
                "Мұрагерлік және полиморфизм",
                "Ерекше (dunder) әдістер",
                "Модульдер мен пакеттер",
            ],
            "requirements": ["Python негіздері курсы немесе баламалы білім"],
        },
        "ru": {
            "title": "Python: объектно-ориентированное программирование",
            "short": "Классы, наследование и принципы чистого кода.",
            "description": "Следующий шаг для тех, кто знает основы Python. "
            "Изучите принципы ООП, специальные методы и структуру проекта.",
            "outcomes": [
                "Проектировать классы и объекты",
                "Наследование и полиморфизм",
                "Специальные (dunder) методы",
                "Модули и пакеты",
            ],
            "requirements": ["Курс «Основы Python» или аналогичные знания"],
        },
        "modules": [
            (
                "Класстар",
                "Классы",
                [
                    ("Класс және объект", "Класс и объект", V, 15, True),
                    ("Атрибуттар және әдістер", "Атрибуты и методы", T, 15, False),
                    ("Тест: класстар", "Тест: классы", Q, 10, False),
                ],
            ),
            (
                "ООП принциптері",
                "Принципы ООП",
                [
                    ("Мұрагерлік", "Наследование", V, 18, False),
                    ("Полиморфизм", "Полиморфизм", T, 15, False),
                    ("Инкапсуляция", "Инкапсуляция", T, 12, False),
                ],
            ),
            (
                "Жоба құрылымы",
                "Структура проекта",
                [
                    ("Модульдер мен пакеттер", "Модули и пакеты", V, 15, False),
                    ("Dunder әдістер", "Dunder-методы", T, 15, False),
                    ("Жоба: кітапхана жүйесі", "Проект: система библиотеки", A, 40, False),
                ],
            ),
        ],
    },
    {
        "slug": "react-nextjs",
        "category": "web-development",
        "instructor": 1,
        "level": CourseLevel.ADVANCED,
        "price": "0",
        "featured": False,
        "kk": {
            "title": "React және Next.js",
            "short": "Заманауи веб-қосымшаларды React пен Next.js-те құрыңыз.",
            "description": "Компоненттер, күй басқару, серверлік рендеринг және "
            "маршруттау. Курс соңында толыққанды Next.js қосымшасын жариялайсыз.",
            "outcomes": [
                "React компоненттері мен hook-тары",
                "Next.js App Router және серверлік компоненттер",
                "API-мен жұмыс және деректерді кэштеу",
                "TypeScript-пен типтелген код",
            ],
            "requirements": ["JavaScript-ті сенімді білу", "HTML және CSS"],
        },
        "ru": {
            "title": "React и Next.js",
            "short": "Создавайте современные веб-приложения на React и Next.js.",
            "description": "Компоненты, управление состоянием, серверный рендеринг "
            "и маршрутизация. В конце курса опубликуете полноценное приложение на Next.js.",
            "outcomes": [
                "Компоненты и хуки React",
                "Next.js App Router и серверные компоненты",
                "Работа с API и кэширование данных",
                "Типизированный код на TypeScript",
            ],
            "requirements": ["Уверенное знание JavaScript", "HTML и CSS"],
        },
        "modules": [
            (
                "React",
                "React",
                [
                    ("Компоненттер және props", "Компоненты и props", V, 18, True),
                    ("useState және useEffect", "useState и useEffect", T, 20, False),
                    ("Тест: React", "Тест: React", Q, 10, False),
                ],
            ),
            (
                "Next.js",
                "Next.js",
                [
                    ("App Router", "App Router", V, 20, False),
                    ("Серверлік компоненттер", "Серверные компоненты", T, 22, False),
                    ("Деректерді алу", "Получение данных", T, 20, False),
                ],
            ),
            (
                "Жоба",
                "Проект",
                [
                    ("TypeScript", "TypeScript", V, 18, False),
                    ("Аутентификация", "Аутентификация", T, 22, False),
                    ("Жоба: блог платформасы", "Проект: блог-платформа", A, 60, False),
                ],
            ),
        ],
    },
]


async def _reset(session: AsyncSession) -> None:
    await session.execute(delete(Course).where(Course.is_demo.is_(True)))
    await session.execute(delete(User).where(User.is_demo.is_(True)))
    await session.flush()


SECTION_TITLES = [
    ("Теория", "Теория"),
    ("Видеосабақтар", "Видеоуроки"),
    ("Тесттер және практикалық тапсырмалар", "Тесты и практические задания"),
]


def _reading_minutes(text: str) -> int:
    return max(5, round(len(text.split()) / 130))


def _lesson(position: int, type_: LessonType, title: str, minutes: int, **extra: object) -> Lesson:
    content = str(extra.pop("content", ""))
    return Lesson(
        position=position,
        type=type_,
        duration_minutes=minutes,
        translations=[LessonTranslation(locale="ru", title=title, content_md=content)],
        **extra,
    )


def build_sections(data: dict[str, object]) -> list[Module]:
    """Course content in three sections: theory → video lessons → tests & practice."""
    slug = str(data["slug"])
    content = CONTENT[slug]
    theory_mod, video_mod, practice_mod = (
        Module(position=i, title_kk=kk, title_ru=ru) for i, (kk, ru) in enumerate(SECTION_TITLES, 1)
    )

    # 1. Theory articles
    for pos, (title, body) in enumerate(content["theory"], start=1):
        theory_mod.lessons.append(
            _lesson(
                pos, LessonType.TEXT, title, _reading_minutes(body), content=body, is_preview=True
            )
        )

    # 2. Video lessons (titles come from the original outline, videos from demo_videos.py)
    pos = 0
    for m_pos, (_m_kk, _m_ru, lessons) in enumerate(data["modules"], start=1):  # type: ignore[arg-type]
        for l_pos, (_l_kk, l_ru, *_rest) in enumerate(lessons, start=1):
            video = DEMO_VIDEOS.get(f"{slug}/{m_pos}/{l_pos}")
            if video is None:
                continue
            video_id, minutes, author = video
            pos += 1
            video_mod.lessons.append(
                _lesson(
                    pos,
                    LessonType.VIDEO,
                    l_ru,
                    minutes,
                    video_url=youtube_url(video_id),
                    video_author=author,
                    is_preview=True,
                )
            )

    # 3. Quiz + practical tasks
    quiz_data = content["quiz"]
    quiz_lesson = _lesson(1, LessonType.QUIZ, quiz_data["title"], 10)
    quiz = Quiz(pass_percent=70)
    for q_pos, q in enumerate(quiz_data["questions"], start=1):
        question = Question(
            position=q_pos,
            type=QuestionType(q["type"]),
            text=q["text"],
            points=1,
            explanation=q.get("explanation", ""),
        )
        if q["type"] == "text":
            options = [(a, True) for a in q["accepted"]]
        else:
            options = q["options"]
        for a_pos, (text, correct) in enumerate(options, start=1):
            question.answers.append(Answer(position=a_pos, text=text, is_correct=correct))
        quiz.questions.append(question)
    quiz_lesson.quiz = quiz  # type: ignore[attr-defined]
    practice_mod.lessons.append(quiz_lesson)

    for t_pos, task in enumerate(content["tasks"], start=2):
        lesson = _lesson(
            t_pos, LessonType.ASSIGNMENT, task["title"], 30, content=task["description"]
        )
        lesson.assignment = Assignment(  # type: ignore[attr-defined]
            description_md=task["description"],
            expected_md=task["expected"],
            criteria=task["criteria"],
            answer_format=task["format"],
        )
        practice_mod.lessons.append(lesson)

    return [theory_mod, video_mod, practice_mod]


async def seed(reset: bool = False) -> None:
    async with SessionLocal() as session:
        if reset:
            await _reset(session)

        categories: dict[str, Category] = {}
        for i, (slug, kk, ru, icon) in enumerate(CATEGORIES):
            cat = await session.scalar(select(Category).where(Category.slug == slug))
            if cat is None:
                cat = Category(slug=slug, name_kk=kk, name_ru=ru, icon=icon, sort_order=i)
                session.add(cat)
            categories[slug] = cat

        role = await session.scalar(select(Role).where(Role.name == RoleName.INSTRUCTOR))
        if role is None:
            raise RuntimeError("Roles missing — run `alembic upgrade head` first")

        instructors: list[User] = []
        for email, name, headline in INSTRUCTORS:
            user = await session.scalar(select(User).where(User.email == email))
            if user is None:
                user = User(
                    email=email,
                    password_hash=UNUSABLE_PASSWORD,
                    full_name=name,
                    role_id=role.id,
                    is_demo=True,
                    profile=UserProfile(headline=headline),
                )
                session.add(user)
            instructors.append(user)
        await session.flush()

        now = datetime.now(UTC)
        created = 0
        for i, data in enumerate(COURSES):
            if await session.scalar(select(Course.id).where(Course.slug == data["slug"])):
                continue
            course = Course(
                slug=data["slug"],
                category=categories[data["category"]],
                instructor=instructors[data["instructor"]],
                level=data["level"],
                status=CourseStatus.PUBLISHED,
                price=Decimal(data["price"]),
                is_featured=data["featured"],
                is_demo=True,
                published_at=now - timedelta(days=len(COURSES) - i),
            )
            for loc in ("kk", "ru"):
                t = data[loc]
                course.translations.append(
                    CourseTranslation(
                        locale=loc,
                        title=t["title"],
                        short_description=t["short"],
                        description=t["description"],
                        outcomes=t["outcomes"],
                        requirements=t["requirements"],
                    )
                )
            course.modules.extend(build_sections(data))
            session.add(course)
            created += 1

        await session.commit()
        print(f"Demo seed done: {created} course(s) created.")
    await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true", help="delete demo data first")
    asyncio.run(seed(reset=parser.parse_args().reset))


if __name__ == "__main__":
    main()
