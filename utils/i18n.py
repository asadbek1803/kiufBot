"""Internationalization (i18n) utilities for multilingual support"""

from typing import Dict
from schemas.language import LanguageEnum

# Translation dictionary
TRANSLATIONS: Dict[str, Dict[LanguageEnum, str]] = {
    # Menu texts
    "main_menu": {
        LanguageEnum.UZ: "🏛️ Asosiy menyu",
        LanguageEnum.EN: "🏛️ Main menu",
        LanguageEnum.RU: "🏛️ Главное меню",
    },
    "welcome": {
        LanguageEnum.UZ: "Assalomu alaykum! KIUF Universitetining rasmiy botiga xush kelibsiz! 👋",
        LanguageEnum.EN: "Welcome to the official KIUF University bot! 👋",
        LanguageEnum.RU: "Добро пожаловать в официальный бот Университета KIUF! 👋",
    },
    "select_language": {
        LanguageEnum.UZ: "Tilni tanlang / Choose language / Выберите язык",
        LanguageEnum.EN: "Select language",
        LanguageEnum.RU: "Выберите язык",
    },
    "language_changed": {
        LanguageEnum.UZ: "✅ Til o'zgartirildi!",
        LanguageEnum.EN: "✅ Language changed!",
        LanguageEnum.RU: "✅ Язык изменен!",
    },
    # Buttons
    "btn_360_university": {
        LanguageEnum.UZ: "🌐 360 University",
        LanguageEnum.EN: "🌐 360 University",
        LanguageEnum.RU: "🌐 360 University",
    },
    "btn_language": {
        LanguageEnum.UZ: "🌍 Til",
        LanguageEnum.EN: "🌍 Language",
        LanguageEnum.RU: "🌍 Язык",
    },
    "btn_back": {
        LanguageEnum.UZ: "⬅️ Orqaga",
        LanguageEnum.EN: "⬅️ Back",
        LanguageEnum.RU: "⬅️ Назад",
    },
    # Language names
    "lang_uzbek": {
        LanguageEnum.UZ: "🇺🇿 O'zbek tili",
        LanguageEnum.EN: "🇺🇿 Uzbek",
        LanguageEnum.RU: "🇺🇿 Узбекский",
    },
    "lang_english": {
        LanguageEnum.UZ: "🇬🇧 Ingliz tili",
        LanguageEnum.EN: "🇬🇧 English",
        LanguageEnum.RU: "🇬🇧 Английский",
    },
    "lang_russian": {
        LanguageEnum.UZ: "🇷🇺 Rus tili",
        LanguageEnum.EN: "🇷🇺 Russian",
        LanguageEnum.RU: "🇷🇺 Русский",
    },
    # Messages
    "open_360": {
        LanguageEnum.UZ: "360 University ko'rinishini oching",
        LanguageEnum.EN: "Open 360 University view",
        LanguageEnum.RU: "Открыть вид 360 University",
    },
    # Menu buttons
    "btn_admission": {
        LanguageEnum.UZ: "📄 Qabul 2025-2026",
        LanguageEnum.EN: "📄 Admission 2025-2026",
        LanguageEnum.RU: "📄 Приём 2025-2026",
    },
    "btn_university_info": {
        LanguageEnum.UZ: "🏛️ Universitet haqida ma'lumot",
        LanguageEnum.EN: "🏛️ Information about the university",
        LanguageEnum.RU: "🏛️ Информация об университете",
    },
    "btn_address": {
        LanguageEnum.UZ: "📍 Manzil",
        LanguageEnum.EN: "📍 Address",
        LanguageEnum.RU: "📍 Адрес",
    },
    "btn_faculties": {
        LanguageEnum.UZ: "📚 Fakultetlar",
        LanguageEnum.EN: "📚 Faculties",
        LanguageEnum.RU: "📚 Факультеты",
    },
    "btn_directions": {
        LanguageEnum.UZ: "🎓 Yo'nalishlar",
        LanguageEnum.EN: "🎓 Directions",
        LanguageEnum.RU: "🎓 Направления",
    },
    # Content texts
    "loading": {
        LanguageEnum.UZ: "⏳ Ma'lumotlar yuklanmoqda...",
        LanguageEnum.EN: "⏳ Loading information...",
        LanguageEnum.RU: "⏳ Загрузка информации...",
    },
    "error_loading": {
        LanguageEnum.UZ: "❌ Ma'lumotlarni yuklashda xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.",
        LanguageEnum.EN: "❌ Error loading information. Please try again later.",
        LanguageEnum.RU: "❌ Ошибка загрузки информации. Пожалуйста, попробуйте позже.",
    },
    "admission_info": {
        LanguageEnum.UZ: "📄 <b>Qabul 2025-2026</b>\n\n",
        LanguageEnum.EN: "📄 <b>Admission 2025-2026</b>\n\n",
        LanguageEnum.RU: "📄 <b>Приём 2025-2026</b>\n\n",
    },
    "university_info": {
        LanguageEnum.UZ: """🎓 <b>O'zbekiston – Koreya Xalqaro Universiteti (KIUF) haqida to'liq ma'lumot</b>

📌 <b>Rasmiy nomi:</b> Korea International University in Fergana (KIUF) — O'zbekiston Koreya Xalqaro Universiteti

📍 <b>Manzil:</b> Farg'ona shahri, A. Navoi ko'chasi 55-B uy, Farg'ona viloyati, O'zbekiston

📞 <b>Telefon:</b> +998 95 401 9454 / +998 95 401 9457

📧 <b>Email:</b> info@ukiu.uz

🕐 <b>Ish vaqti:</b> Dushanba – Juma, 08:00 dan 18:00 gacha

<b>🎓 Universitet haqida umumiy ma'lumot</b>

KIUF — bu Farg'ona shahridagi xususiy oliy ta'lim muassasasi bo'lib, O'zbekiston va Koreya ta'lim tizimini birlashtirgan universitet hisoblanadi. Ta'lim zamonaviy amaliyot jihozlari bilan ta'minlangan, xorijiy (koreys) professor-o'qituvchilar dars beradi va talabalarga xalqaro darajadagi ta'lim imkoniyatlari taqdim etiladi.

<b>📚 Ta'lim dasturlari va imkoniyatlar</b>
🎓 3+1 qo'shma diplom dasturi
🎓 2+2 qo'shma diplom dasturi

Siz 3 yil O'zbekistonda, keyin 1 yil Koreyada tahsil olib, 2 ta diplomga ega bo'lish imkoniga egasiz.

<b>🧑‍🏫 Ta'limning asosiy afzalliklari</b>

✅ Koreya ta'lim tizimi asosida zamonaviy amaliyot va o'quv uskunalari bilan ta'minlangan ta'lim.

✅ Koreyadan tashrif buyurgan professor-o'qituvchilardan dars olish.

✅ A'lo baholarga ega talabalar uchun 50%gacha kontrakt chegirmalari.

<b>📘 Yo'nalishlar (misollar)</b>

KIUFda texnik, ijtimoiy va til yo'nalishlari mavjud:

<b>🔹 Texnik-muhandislik:</b>
• Smart ishlab chiqarish muhandisligi
• Arxitektura muhandisligi
• Avtomobilsozlik muhandisligi
• Mashinasozlik muhandisligi
• Internet va axborot kommunikatsiyasi

<b>🔹 Ijtimoiy-gumanitar:</b>
• Xalqaro savdo
• Koreys tili
• Ingliz filologiyasi
• Maktabgacha ta'lim
• Turizm menejmenti
• Menejment va kompyuterlashtirilgan buxgalteriya hisobi

<b>🌍 Talabalar uchun imkoniyatlar</b>

🎓 <b>Koreys tilini chuqur o'rganish:</b>
Talabalarga koreys tili bo'yicha chuqur darslar, qo'shimcha darslar va 'TOPIK' imtihoni topshirish imkoniyati mavjud.

📌 <b>Amaliyot va ish imkoniyatlari:</b>
Koreys kompaniyalari bilan hamkorlik orqali talabalar amaliyot o'tash va bitirgandan keyin ish topish imkoniga ega bo'ladi.

🏠 <b>Talabalar turmush sharoitlari:</b>
370 nafar talabaga mo'ljallangan yotoqxona, oshxona, do'kon, sog'liq xonalari va boshqa qulayliklar mavjud.

💰 <b>Arzon ta'lim:</b>
KIUFda tahsil olish Koreyada o'qishdan taxminan 68% ga arzon bo'lishi mumkin.""",
        
        LanguageEnum.EN: """🎓 <b>Complete Information about Uzbekistan – Korea International University (KIUF)</b>

📌 <b>Official name:</b> Korea International University in Fergana (KIUF) — Uzbekistan Korea International University

📍 <b>Address:</b> 55-B A. Navoi Street, Fergana city, Fergana region, Uzbekistan

📞 <b>Phone:</b> +998 95 401 9454 / +998 95 401 9457

📧 <b>Email:</b> info@ukiu.uz

🕐 <b>Working hours:</b> Monday – Friday, from 08:00 to 18:00

<b>🎓 General Information about the University</b>

KIUF is a private higher education institution in Fergana city that combines the education systems of Uzbekistan and Korea. Education is provided with modern practical equipment, foreign (Korean) professors teach, and students are provided with international-level educational opportunities.

<b>📚 Educational Programs and Opportunities</b>
🎓 3+1 Joint Diploma Program
🎓 2+2 Joint Diploma Program

You can study 3 years in Uzbekistan, then 1 year in Korea, and earn 2 diplomas.

<b>🧑‍🏫 Main Advantages of Education</b>

✅ Education based on the Korean education system with modern practice and educational equipment.

✅ Studying with visiting professors from Korea.

✅ Up to 50% contract discounts for students with excellent grades.

<b>📘 Specializations (Examples)</b>

KIUF has technical, social, and language specializations:

<b>🔹 Technical Engineering:</b>
• Smart Manufacturing Engineering
• Architecture Engineering
• Automotive Engineering
• Mechanical Engineering
• Internet and Information Communication

<b>🔹 Social and Humanities:</b>
• International Trade
• Korean Language
• English Philology
• Preschool Education
• Tourism Management
• Management and Computerized Accounting

<b>🌍 Opportunities for Students</b>

🎓 <b>Deep Study of Korean Language:</b>
Students have opportunities for in-depth Korean language courses, additional classes, and taking the 'TOPIK' exam.

📌 <b>Internship and Employment Opportunities:</b>
Through cooperation with Korean companies, students can do internships and find jobs after graduation.

🏠 <b>Student Living Conditions:</b>
Dormitory for 370 students, dining hall, shop, medical rooms, and other facilities are available.

💰 <b>Affordable Education:</b>
Studying at KIUF can be approximately 68% cheaper than studying in Korea.""",
        
        LanguageEnum.RU: """🎓 <b>Полная информация об Узбекистанско-Корейском Международном Университете (KIUF)</b>

📌 <b>Официальное название:</b> Korea International University in Fergana (KIUF) — Узбекистанско-Корейский Международный Университет

📍 <b>Адрес:</b> г. Фергана, ул. А. Навои 55-Б, Ферганская область, Узбекистан

📞 <b>Телефон:</b> +998 95 401 9454 / +998 95 401 9457

📧 <b>Email:</b> info@ukiu.uz

🕐 <b>Рабочие часы:</b> Понедельник – Пятница, с 08:00 до 18:00

<b>🎓 Общая информация об университете</b>

KIUF — это частное высшее учебное заведение в г. Фергана, которое объединяет системы образования Узбекистана и Кореи. Обучение обеспечено современным практическим оборудованием, преподают иностранные (корейские) профессора, и студентам предоставляются возможности образования международного уровня.

<b>📚 Образовательные программы и возможности</b>
🎓 Программа совместного диплома 3+1
🎓 Программа совместного диплома 2+2

Вы можете учиться 3 года в Узбекистане, затем 1 год в Корее и получить 2 диплома.

<b>🧑‍🏫 Основные преимущества образования</b>

✅ Образование на основе корейской системы образования с современной практикой и учебным оборудованием.

✅ Обучение у приглашенных профессоров из Кореи.

✅ Скидки на контракт до 50% для студентов с отличными оценками.

<b>📘 Направления (примеры)</b>

В KIUF есть технические, социальные и языковые направления:

<b>🔹 Техническая инженерия:</b>
• Инженерия умного производства
• Архитектурная инженерия
• Автомобильная инженерия
• Машиностроительная инженерия
• Интернет и информационные коммуникации

<b>🔹 Социально-гуманитарные:</b>
• Международная торговля
• Корейский язык
• Английская филология
• Дошкольное образование
• Туристический менеджмент
• Менеджмент и компьютеризированный бухгалтерский учет

<b>🌍 Возможности для студентов</b>

🎓 <b>Глубокое изучение корейского языка:</b>
Студенты имеют возможности для углубленных курсов корейского языка, дополнительных занятий и сдачи экзамена 'TOPIK'.

📌 <b>Практика и возможности трудоустройства:</b>
Благодаря сотрудничеству с корейскими компаниями студенты могут проходить практику и найти работу после окончания учебы.

🏠 <b>Условия жизни студентов:</b>
Общежитие на 370 студентов, столовая, магазин, медицинские кабинеты и другие удобства доступны.

💰 <b>Доступное образование:</b>
Обучение в KIUF может быть примерно на 68% дешевле, чем обучение в Корее.""",
    },
    "address_info": {
        LanguageEnum.UZ: """📍 <b>KIUF Universiteti Manzili va Aloqa Ma'lumotlari</b>

📍 <b>Manzil:</b>
Farg'ona shahri, A. Navoi ko'chasi 55-B uy
Farg'ona viloyati, O'zbekiston

📞 <b>Telefon raqamlari:</b>
+998 95 401 9454
+998 95 401 9457

📧 <b>Email:</b>
info@ukiu.uz

🌐 <b>Veb-sayt:</b>
www.ukiu.uz

🕐 <b>Ish vaqti:</b>
Dushanba – Juma: 08:00 - 18:00
Shanba – Yakshanba: Dam olish kunlari

🗺️ <b>Yashash uchun qulay:</b>
• Yaqinida metro va avtobus bekatlari
• Qulay transport aloqasi
• Yaqinida banklar, do'konlar va boshqa infratuzilma""",
        
        LanguageEnum.EN: """📍 <b>KIUF University Address and Contact Information</b>

📍 <b>Address:</b>
55-B A. Navoi Street, Fergana city
Fergana region, Uzbekistan

📞 <b>Phone numbers:</b>
+998 95 401 9454
+998 95 401 9457

📧 <b>Email:</b>
info@ukiu.uz

🌐 <b>Website:</b>
www.ukiu.uz

🕐 <b>Working hours:</b>
Monday – Friday: 08:00 - 18:00
Saturday – Sunday: Days off

🗺️ <b>Convenient location:</b>
• Near metro and bus stops
• Convenient transport connections
• Nearby banks, shops and other infrastructure""",
        
        LanguageEnum.RU: """📍 <b>Адрес и контактная информация Университета KIUF</b>

📍 <b>Адрес:</b>
г. Фергана, ул. А. Навои 55-Б
Ферганская область, Узбекистан

📞 <b>Телефоны:</b>
+998 95 401 9454
+998 95 401 9457

📧 <b>Email:</b>
info@ukiu.uz

🌐 <b>Веб-сайт:</b>
www.ukiu.uz

🕐 <b>Рабочие часы:</b>
Понедельник – Пятница: 08:00 - 18:00
Суббота – Воскресенье: Выходные дни

🗺️ <b>Удобное расположение:</b>
• Рядом с остановками метро и автобусов
• Удобные транспортные связи
• Рядом банки, магазины и другая инфраструктура""",
    },
    "faculties_info": {
        LanguageEnum.UZ: """📚 <b>KIUF Universiteti Fakultetlari</b>

KIUF universitetida zamonaviy ta'lim beruvchi bir nechta fakultetlar mavjud:

<b>🔹 Texnik Fakultet</b>
Zamonaviy muhandislik yo'nalishlari va innovatsion texnologiyalar bilan ishlash

<b>🔹 Iqtisodiyot va Menejment Fakulteti</b>
Biznes, menejment va xalqaro savdo sohalarida mutaxassislar tayyorlash

<b>🔹 Filologiya Fakulteti</b>
Tillar (Koreys, Ingliz) va filologiya bo'yicha chuqur ta'lim

<b>🔹 Pedagogika Fakulteti</b>
Ta'lim tizimi uchun mutaxassislar tayyorlash

<b>🔹 Turizm va Servis Fakulteti</b>
Turizm va xizmat ko'rsatish sohalarida professional tayyorlash

Har bir fakultetda:
✅ Tajribali professor-o'qituvchilar
✅ Zamonaviy o'quv uskunalari
✅ Amaliy darslar va loyihalar
✅ Koreya bilan hamkorlik imkoniyatlari""",
        
        LanguageEnum.EN: """📚 <b>KIUF University Faculties</b>

KIUF University has several faculties providing modern education:

<b>🔹 Technical Faculty</b>
Working with modern engineering specializations and innovative technologies

<b>🔹 Faculty of Economics and Management</b>
Training specialists in business, management, and international trade

<b>🔹 Faculty of Philology</b>
In-depth education in languages (Korean, English) and philology

<b>🔹 Faculty of Pedagogy</b>
Training specialists for the education system

<b>🔹 Faculty of Tourism and Service</b>
Professional training in tourism and service sectors

Each faculty offers:
✅ Experienced professors and teachers
✅ Modern educational equipment
✅ Practical classes and projects
✅ Opportunities for cooperation with Korea""",
        
        LanguageEnum.RU: """📚 <b>Факультеты Университета KIUF</b>

В Университете KIUF существует несколько факультетов, предоставляющих современное образование:

<b>🔹 Технический Факультет</b>
Работа с современными инженерными направлениями и инновационными технологиями

<b>🔹 Факультет Экономики и Менеджмента</b>
Подготовка специалистов в сфере бизнеса, менеджмента и международной торговли

<b>🔹 Филологический Факультет</b>
Углубленное образование в области языков (корейский, английский) и филологии

<b>🔹 Педагогический Факультет</b>
Подготовка специалистов для системы образования

<b>🔹 Факультет Туризма и Сервиса</b>
Профессиональная подготовка в сферах туризма и обслуживания

Каждый факультет предлагает:
✅ Опытных профессоров и преподавателей
✅ Современное учебное оборудование
✅ Практические занятия и проекты
✅ Возможности сотрудничества с Кореей""",
    },
    "directions_info": {
        LanguageEnum.UZ: """🎓 <b>KIUF Universiteti Ta'lim Yo'nalishlari</b>

<b>🔹 TEXNIK-MUHANDISLIK YO'NALISHLARI</b>

1. <b>Smart ishlab chiqarish muhandisligi</b>
   • Zamonaviy ishlab chiqarish texnologiyalari
   • Robototexnika va avtomatlashtirish
   • Sanoat 4.0 texnologiyalari

2. <b>Arxitektura muhandisligi</b>
   • Binokorlik va arxitektura loyihalash
   • Shaharsozlik va landshaft dizayni
   • Zamonaviy qurilish materiallari

3. <b>Avtomobilsozlik muhandisligi</b>
   • Avtomobil texnologiyalari
   • Mexanika va elektronika
   • Transport tizimlari

4. <b>Mashinasozlik muhandisligi</b>
   • Mashinasozlik va mexanika
   • Konstruksiya va dizayn
   • Ishlab chiqarish jarayonlari

5. <b>Internet va axborot kommunikatsiyasi</b>
   • Axborot texnologiyalari
   • Tarmoq va telekommunikatsiyalar
   • Kiberxavfsizlik

<b>🔹 IJTIMOIY-GUMANITAR YO'NALISHLARI</b>

6. <b>Xalqaro savdo</b>
   • Xalqaro biznes va savdo
   • Marketing va brending
   • Logistika va ta'minot zanjiri

7. <b>Koreys tili</b>
   • Koreys tili va adabiyoti
   • Tarjima va tilshunoslik
   • Madaniy aloqalar

8. <b>Ingliz filologiyasi</b>
   • Ingliz tili va adabiyoti
   • Lingvistika va metodika
   • Xalqaro kommunikatsiya

9. <b>Maktabgacha ta'lim</b>
   • Pedagogika va psixologiya
   • Bolalar rivojlanishi
   • O'qitish metodikasi

10. <b>Turizm menejmenti</b>
    • Turizm va mehmonxona biznesi
    • Xizmat ko'rsatish
    • Tadbirkorlik

11. <b>Menejment va kompyuterlashtirilgan buxgalteriya hisobi</b>
    • Biznes menejmenti
    • Buxgalteriya hisobi va audit
    • Moliya va hisob-kitoblar

<b>✨ Qo'shimcha imkoniyatlar:</b>
• Koreya universitetlariga o'tish imkoniyati
• Qo'shma diplom dasturlari (3+1, 2+2)
• TOPIK imtihoni tayyorgarligi
• Amaliyot va ish imkoniyatlari""",
        
        LanguageEnum.EN: """🎓 <b>KIUF University Educational Specializations</b>

<b>🔹 TECHNICAL ENGINEERING SPECIALIZATIONS</b>

1. <b>Smart Manufacturing Engineering</b>
   • Modern manufacturing technologies
   • Robotics and automation
   • Industry 4.0 technologies

2. <b>Architecture Engineering</b>
   • Construction and architectural design
   • Urban planning and landscape design
   • Modern construction materials

3. <b>Automotive Engineering</b>
   • Automotive technologies
   • Mechanics and electronics
   • Transport systems

4. <b>Mechanical Engineering</b>
   • Mechanical engineering and mechanics
   • Construction and design
   • Manufacturing processes

5. <b>Internet and Information Communication</b>
   • Information technologies
   • Networks and telecommunications
   • Cybersecurity

<b>🔹 SOCIAL AND HUMANITIES SPECIALIZATIONS</b>

6. <b>International Trade</b>
   • International business and trade
   • Marketing and branding
   • Logistics and supply chain

7. <b>Korean Language</b>
   • Korean language and literature
   • Translation and linguistics
   • Cultural relations

8. <b>English Philology</b>
   • English language and literature
   • Linguistics and methodology
   • International communication

9. <b>Preschool Education</b>
   • Pedagogy and psychology
   • Child development
   • Teaching methodology

10. <b>Tourism Management</b>
    • Tourism and hotel business
    • Service provision
    • Entrepreneurship

11. <b>Management and Computerized Accounting</b>
    • Business management
    • Accounting and auditing
    • Finance and calculations

<b>✨ Additional opportunities:</b>
• Opportunity to transfer to Korean universities
• Joint diploma programs (3+1, 2+2)
• TOPIK exam preparation
• Internship and employment opportunities""",
        
        LanguageEnum.RU: """🎓 <b>Образовательные направления Университета KIUF</b>

<b>🔹 ТЕХНИЧЕСКИЕ ИНЖЕНЕРНЫЕ НАПРАВЛЕНИЯ</b>

1. <b>Инженерия умного производства</b>
   • Современные производственные технологии
   • Робототехника и автоматизация
   • Технологии Индустрии 4.0

2. <b>Архитектурная инженерия</b>
   • Строительство и архитектурное проектирование
   • Градостроительство и ландшафтный дизайн
   • Современные строительные материалы

3. <b>Автомобильная инженерия</b>
   • Автомобильные технологии
   • Механика и электроника
   • Транспортные системы

4. <b>Машиностроительная инженерия</b>
   • Машиностроение и механика
   • Конструирование и дизайн
   • Производственные процессы

5. <b>Интернет и информационные коммуникации</b>
   • Информационные технологии
   • Сети и телекоммуникации
   • Кибербезопасность

<b>🔹 СОЦИАЛЬНО-ГУМАНИТАРНЫЕ НАПРАВЛЕНИЯ</b>

6. <b>Международная торговля</b>
   • Международный бизнес и торговля
   • Маркетинг и брендинг
   • Логистика и цепочка поставок

7. <b>Корейский язык</b>
   • Корейский язык и литература
   • Перевод и лингвистика
   • Культурные отношения

8. <b>Английская филология</b>
   • Английский язык и литература
   • Лингвистика и методология
   • Международная коммуникация

9. <b>Дошкольное образование</b>
   • Педагогика и психология
   • Развитие ребенка
   • Методика преподавания

10. <b>Туристический менеджмент</b>
    • Туризм и гостиничный бизнес
    • Обслуживание
    • Предпринимательство

11. <b>Менеджмент и компьютеризированный бухгалтерский учет</b>
    • Бизнес-менеджмент
    • Бухгалтерский учет и аудит
    • Финансы и расчеты

<b>✨ Дополнительные возможности:</b>
• Возможность перевода в корейские университеты
• Программы совместного диплома (3+1, 2+2)
• Подготовка к экзамену TOPIK
• Возможности для практики и трудоустройства""",
    },
    # Admission submenu
    "admission_menu_title": {
        LanguageEnum.UZ: "📄 <b>Qabul 2025-2026</b>\n\nTanlang:",
        LanguageEnum.EN: "📄 <b>Admission 2025-2026</b>\n\nSelect:",
        LanguageEnum.RU: "📄 <b>Приём 2025-2026</b>\n\nВыберите:",
    },
    "btn_directions_quotas": {
        LanguageEnum.UZ: "📊 Qabul yo'nalishlari va kvotalari",
        LanguageEnum.EN: "📊 Admission directions and quotas",
        LanguageEnum.RU: "📊 Направления приёма и квоты",
    },
    "btn_admission_deadlines": {
        LanguageEnum.UZ: "📅 Qabul muddatlari va me'zonlari",
        LanguageEnum.EN: "📅 Admission deadlines and criteria",
        LanguageEnum.RU: "📅 Сроки и критерии приёма",
    },
    "btn_contract_payments": {
        LanguageEnum.UZ: "💰 Kontrakt to'lovlari va imtiyozlar",
        LanguageEnum.EN: "💰 Contract payments and benefits",
        LanguageEnum.RU: "💰 Платежи по контракту и льготы",
    },
    "btn_korean_language_benefit": {
        LanguageEnum.UZ: "🇰🇷 Koreys tili imtiyozi",
        LanguageEnum.EN: "🇰🇷 Korean language benefit",
        LanguageEnum.RU: "🇰🇷 Льгота по корейскому языку",
    },
    "btn_developer": {
        LanguageEnum.UZ: "👨‍💻 Dasturchi",
        LanguageEnum.EN: "👨‍💻 Developer",
        LanguageEnum.RU: "👨‍💻 Разработчик",
    },
    "btn_feedback": {
        LanguageEnum.UZ: "💬 Taklif va murojjatlar",
        LanguageEnum.EN: "💬 Feedback and suggestions",
        LanguageEnum.RU: "💬 Отзывы и предложения",
    },

    "feedback_menu_description": {
        LanguageEnum.UZ: """💬 <b>TAKLIF VA MUROJJATLAR</b>

Iltimos, o'z taklif yoki murojjatingizni yozib yuboring.

Adminlar sizning xabaringizni ko‘rib chiqib, javob berishadi.

📝 Xabaringizni yuboring:""",

        LanguageEnum.EN: """💬 <b>FEEDBACK AND SUGGESTIONS</b>

Please, write your feedback or suggestion.

Admins will review your message and respond.

Please, write your message:""",

        LanguageEnum.RU: """💬 <b>ОТЗЫВЫ И ПРЕДЛОЖЕНИЯ</b>

Пожалуйста, напишите ваш отзыв или предложение.

Администраторы просмотрят ваше сообщение и ответят.

Пожалуйста, напишите ваше сообщение:""",
    },
    
    # Schedule and Profile translations
    "btn_schedule": {
        LanguageEnum.UZ: "📅 Dars jadvali",
        LanguageEnum.EN: "📅 Schedule",
        LanguageEnum.RU: "📅 Расписание",
    },
    "btn_today_schedule": {
        LanguageEnum.UZ: "📅 Bugungi jadval",
        LanguageEnum.EN: "📅 Today's Schedule",
        LanguageEnum.RU: "📅 Расписание на сегодня",
    },
    "btn_week_schedule": {
        LanguageEnum.UZ: "📆 Haftalik jadval",
        LanguageEnum.EN: "📆 Weekly Schedule",
        LanguageEnum.RU: "📆 Расписание на неделю",
    },
    "btn_update_schedule": {
        LanguageEnum.UZ: "🔄 Jadvalni yangilash",
        LanguageEnum.EN: "🔄 Update Schedule",
        LanguageEnum.RU: "🔄 Обновить расписание",
    },
    "btn_prev_week": {
        LanguageEnum.UZ: "⬅️ Oldingi hafta",
        LanguageEnum.EN: "⬅️ Previous Week",
        LanguageEnum.RU: "⬅️ Предыдущая неделя",
    },
    "btn_next_week": {
        LanguageEnum.UZ: "➡️ Keyingi hafta",
        LanguageEnum.EN: "➡️ Next Week",
        LanguageEnum.RU: "➡️ Следующая неделя",
    },
    "btn_profile": {
        LanguageEnum.UZ: "👤 Profil",
        LanguageEnum.EN: "👤 Profile",
        LanguageEnum.RU: "👤 Профиль",
    },
    "btn_connect_hemis": {
        LanguageEnum.UZ: "🔗 HEMIS ni ulash",
        LanguageEnum.EN: "🔗 Connect HEMIS",
        LanguageEnum.RU: "🔗 Подключить HEMIS",
    },
    "btn_disconnect_hemis": {
        LanguageEnum.UZ: "❌ HEMISni o'chirish",
        LanguageEnum.EN: "❌ Disconnect HEMIS",
        LanguageEnum.RU: "❌ Отключить HEMIS",
    },
    "btn_change_group": {
        LanguageEnum.UZ: "👥 Guruhni o'zgartirish",
        LanguageEnum.EN: "👥 Change Group",
        LanguageEnum.RU: "👥 Изменить группу",
    },
    "enter_hemis_login": {
        LanguageEnum.UZ: "HEMIS loginni kiriting:",
        LanguageEnum.EN: "Enter HEMIS login:",
        LanguageEnum.RU: "Введите логин HEMIS:",
    },
    "enter_hemis_password": {
        LanguageEnum.UZ: "HEMIS parolini kiriting:",
        LanguageEnum.EN: "Enter HEMIS password:",
        LanguageEnum.RU: "Введите пароль HEMIS:",
    },
    "hemis_connected": {
        LanguageEnum.UZ: "✅ HEMIS muvaffaqiyatli ulandi!",
        LanguageEnum.EN: "✅ HEMIS successfully connected!",
        LanguageEnum.RU: "✅ HEMIS успешно подключен!",
    },
    "hemis_login_error": {
        LanguageEnum.UZ: "❌ HEMIS ga ulanishda xatolik. Login yoki parol noto'g'ri.",
        LanguageEnum.EN: "❌ Error connecting to HEMIS. Invalid login or password.",
        LanguageEnum.RU: "❌ Ошибка подключения к HEMIS. Неверный логин или пароль.",
    },
    "today_schedule": {
        LanguageEnum.UZ: "📅 <b>Bugungi dars jadvali:</b>\n\n",
        LanguageEnum.EN: "📅 <b>Today's Schedule:</b>\n\n",
        LanguageEnum.RU: "📅 <b>Расписание на сегодня:</b>\n\n",
    },
    "week_schedule": {
        LanguageEnum.UZ: "📆 <b>Haftalik dars jadvali:</b>\n\n",
        LanguageEnum.EN: "📆 <b>Weekly Schedule:</b>\n\n",
        LanguageEnum.RU: "📆 <b>Расписание на неделю:</b>\n\n",
    },
    "no_classes_today": {
        LanguageEnum.UZ: "Bugun dars yo'q! 🎉",
        LanguageEnum.EN: "No classes today! 🎉",
        LanguageEnum.RU: "Сегодня нет занятий! 🎉",
    },
    "schedule_loading": {
        LanguageEnum.UZ: "⏳ Jadval yuklanmoqda, kuting...",
        LanguageEnum.EN: "⏳ Schedule is loading, please wait...",
        LanguageEnum.RU: "⏳ Расписание загружается, подождите...",
    },
    "enter_group": {
        LanguageEnum.UZ: "Guruh nomini (masalan: INT-A-25) kiriting:",
        LanguageEnum.EN: "Enter group name (e.g.: INT-A-25):",
        LanguageEnum.RU: "Введите название группы (например: INT-A-25):",
    },
    "group_saved": {
        LanguageEnum.UZ: "✅ Guruh muvaffaqiyatli saqlandi!",
        LanguageEnum.EN: "✅ Group successfully saved!",
        LanguageEnum.RU: "✅ Группа успешно сохранена!",
    },
}


def get_text(key: str, language: LanguageEnum = LanguageEnum.UZ) -> str:
    """Get translated text by key and language"""
    if key in TRANSLATIONS:
        return TRANSLATIONS[key].get(language, TRANSLATIONS[key][LanguageEnum.EN])
    return key

