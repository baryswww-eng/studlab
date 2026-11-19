"""Russian-language YouTube video lessons for the demo catalog.

Picked from YouTube search on 2026-11-19; every video was checked to allow
embedding (oEmbed returned 200). Key: "<course slug>/<module pos>/<lesson pos>".
Value: (YouTube video id, duration in minutes rounded up, channel name).
Videos belong to their authors; the lesson page credits the channel and links
to YouTube.
"""

DEMO_VIDEOS: dict[str, tuple[str, int, str]] = {
    "python-basics/1/1": ("34Rp6KVGIEM", 6, "Школа itProger / Программирование"),
    "python-basics/1/2": ("HLrLz4CJtrY", 8, "/coderoffka - Изучение Python c нуля"),
    "python-basics/2/1": ("DZvNZ9l9NT4", 22, "Школа itProger / Программирование"),
    "python-basics/2/2": ("SUDNfS_0X-Q", 24, "Школа itProger / Программирование"),
    "python-basics/3/1": ("vMD6-jzgDvI", 16, "Школа itProger / Программирование"),
    "python-basics/3/2": ("6K5v4--G__U", 23, "Школа itProger / Программирование"),
    "web-html-css-js/1/1": ("YzAj6cYqHEs", 7, "Redem Studio"),
    "web-html-css-js/1/2": ("SKRydSA2bYA", 17, "Сергей Дмитриевский"),
    "web-html-css-js/1/3": ("_in4LAdxAUA", 5, "Александр Ламков — Friendly Frontend"),
    "web-html-css-js/2/1": ("GctszxSvbeQ", 16, "Александр Ламков — Friendly Frontend"),
    "web-html-css-js/2/2": ("YG8Vhz1pAsU", 17, "Александр Ламков — Friendly Frontend"),
    "web-html-css-js/3/1": ("QBWWplFkdzw", 57, "Гоша Дударь"),
    "web-html-css-js/3/2": ("H9XRtCjD3hA", 10, "Василий Муравьев"),
    "csharp-dotnet-start/1/1": ("8q200PT8jTU", 28, "Школа itProger / Программирование"),
    "csharp-dotnet-start/1/2": ("Xk8vRnm6xtc", 27, "#SimpleCode"),
    "csharp-dotnet-start/2/1": ("TpkMZprzoXE", 23, "Школа itProger / Программирование"),
    "csharp-dotnet-start/2/2": ("8eZy5xiildM", 24, "#SimpleCode"),
    "csharp-dotnet-start/2/3": ("YPCNQL978ps", 39, "Dev Jungles - Andrii Podkolzin"),
    "csharp-dotnet-start/3/1": ("C-zdujHific", 11, "DevTricks"),
    "csharp-dotnet-start/3/2": ("gRQbFRDjS_U", 24, "Дмитрий Юревич"),
    "sql-postgresql/1/1": ("GQfC0nYrto8", 14, "Listen IT"),
    "sql-postgresql/1/2": ("nxGhGQFk34Y", 13, "3D HOST"),
    "sql-postgresql/1/3": ("0Jw3pnF0huk", 8, "Andrey Sozykin"),
    "sql-postgresql/2/1": ("bYdjR6QexJY", 11, "Andrey Sozykin"),
    "sql-postgresql/2/2": ("H3LYwkePWfM", 16, "Vlad Mishustin"),
    "sql-postgresql/3/1": ("0kq99Y8m0gw", 15, "Диджитализируй!"),
    "sql-postgresql/3/2": ("C34HS5wU8Zg", 8, "Andrey Sozykin"),
    "ai-machine-learning-intro/1/1": ("NV8ltedGIs0", 13, "Etudarium"),
    "ai-machine-learning-intro/1/2": ("4HpgX2Kb5KU", 14, "Roman Kucev"),
    "ai-machine-learning-intro/2/1": ("cEeY0opsVMw", 49, "PyLounge"),
    "ai-machine-learning-intro/2/2": ("d4fdGyyOftw", 53, "Stepik"),
    "ai-machine-learning-intro/2/3": ("Hoar3-lKhHI", 10, "Школа itProger / Программирование"),
    "ai-machine-learning-intro/3/1": ("rE43fnoQNPw", 8, "Душкин объяснит"),
    "ai-machine-learning-intro/3/2": ("5UdOdUgDr-c", 12, "Школа itProger / Программирование"),
    "it-fundamentals/1/1": ("hscJXcQXOS4", 5, "Haggon"),
    "it-fundamentals/1/2": ("UQmWM0uZ5Tw", 8, "OnliSkill"),
    "it-fundamentals/1/3": ("wkdb_pP03p0", 5, "Owl Coding"),
    "it-fundamentals/2/1": ("bPJEJY8ADGQ", 4, "(не) AlixHatsu"),
    "it-fundamentals/2/2": ("Dn7hkeXnBsw", 14, "Merion Academy"),
    "it-fundamentals/3/1": ("zrnfvytnylE", 9, "Droider"),
    "it-fundamentals/3/2": ("6VZL0DJWr7g", 14, "Первый отдел"),
    "python-oop/1/1": ("gFRa6qVN980", 15, "Школа itProger / Программирование"),
    "python-oop/1/2": ("P4CNNo8jWj4", 21, "selfedu"),
    "python-oop/2/1": ("7WVYqjdMa6U", 15, "selfedu"),
    "python-oop/2/2": ("fzUI3NyJflw", 11, "selfedu"),
    "python-oop/2/3": ("7lqkS5OINbs", 7, "GarriTV"),
    "python-oop/3/1": ("dNg3l-wpRdY", 22, "Школа itProger / Программирование"),
    "python-oop/3/2": ("_TNCdLeVN2c", 8, "egoroff_channel"),
    "react-nextjs/1/1": ("rlTvbjScIKA", 11, "Web Developer Blog"),
    "react-nextjs/1/2": ("JLC_hCDwu_k", 17, "Какие-то уроки [Frontend]"),
    "react-nextjs/2/1": ("r_tOrjCU88c", 39, "senior_zone"),
    "react-nextjs/2/2": ("0gaXP88yvPc", 10, "senior_zone"),
    "react-nextjs/2/3": ("ec0unC3AHkM", 5, "FineGap"),
    "react-nextjs/3/1": ("ahntAVi3GM4", 20, "Zar Zakharov"),
    "react-nextjs/3/2": ("QvmH1ZCgK8Q", 8, "Vsevolod Heinemann"),
}


def youtube_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"
