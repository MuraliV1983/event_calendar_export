# 🗓️ Event Calendar Export – MySQL + Python + Flask

Export recurring and one-time events to Excel with automatic holiday exclusion.

This project allows users to manage and export their event schedules — including daily, weekly, and monthly recurring events — using Flask, MySQL, and `openpyxl`.

---

## ✅ Features

- Add events with recurrence: `daily`, `weekly`, `monthly`
- Skip all holidays stored in your `holidays` table
- Generate each occurrence of recurring events
- Export to Excel in a clean format: one row per date
- Smart handling of event + recurrence + holiday logic
- Ready for Google Calendar integration (coming soon)
- Easy-to-use web form and API structure

---

## 📸 Sample Output (Excel)

| Event ID | User ID | Event Name        | Event Date  |
|----------|---------|-------------------|-------------|
| 1        | 1       | Yoga Class        | 2025-06-27  |
| 3        | 1       | Daily Walk        | 2025-06-25  |
| 5        | 1       | Team Meeting      | 2025-07-10  |
| 6        | 1       | Team Task Update  | 2025-06-30  |

---

## 🧱 Tech Stack

- ✅ Python 3.10+
- ✅ Flask (backend)
- ✅ MySQL (events database)
- ✅ `openpyxl` (Excel generation)
- ✅ Jinja2 Templates (for form UI)

---

## 🚀 Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/event-calendar-export.git
cd event-calendar-export
2. Install dependencies
bash
Copy
Edit
pip install -r requirements.txt
3. Start the app
bash
Copy
Edit
python app.py
Open in browser: http://127.0.0.1:5000/

📝 Folder Structure
pgsql
Copy
Edit
event_calendar/
├── app.py
├── export_events.py
├── connection.py
├── templates/
│   └── index.html
├── requirements.txt
└── README.md
🔮 Upcoming Features (To-Do)
 Filter by date and event type in UI

 Google Calendar sync (OAuth2)

 Background job for large exports (Celery or RQ)

 Event edit/delete interface

🔖 Author
Murali Dharan
Proudly built as part of my 🔁 #MuraliCodes series
🔗 LinkedIn
