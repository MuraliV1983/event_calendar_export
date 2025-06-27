from flask import Flask, jsonify, request, send_file, render_template
from config import get_connection
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta  # For monthly support
from export_events import export_to_excel
from datetime import datetime

app = Flask(__name__)

@app.route('/add-user', methods=['POST'])
def add_user():
    data = request.get_json()
    
    conn = None
    cursor = None

    try:
        conn = get_connection()
        print("✅ DB connection successful (add-user)")
        cursor = conn.cursor()

        sql = """
        INSERT INTO users (name, email, password)
        VALUES (%s, %s, %s)
        """
        values = (
            data.get('name'),
            data.get('email'),
            data.get('password')
        )

        cursor.execute(sql, values)
        conn.commit()

        return jsonify(message="✅ User added successfully!", user_id=cursor.lastrowid)

    except Exception as e:
        return jsonify(error=str(e)), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/add-event', methods=['POST'])
def add_event():
    data = request.get_json()

    conn = None
    cursor = None

    try:
        conn = get_connection()
        print("✅ DB connection successful (add-event)")
        cursor = conn.cursor()

        # Insert into events
        sql = """
        INSERT INTO events (
            evnt_user_id, evnt_name, evnt_title, evnt_desc,
            evnt_date, evnt_start_time, evnt_end_time, evnt_location
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data.get('evnt_user_id'),
            data.get('evnt_name'),
            data.get('evnt_title'),
            data.get('evnt_desc'),
            data.get('evnt_date'),
            data.get('evnt_start_time'),
            data.get('evnt_end_time'),
            data.get('evnt_location')
        )

        cursor.execute(sql, values)
        event_id = cursor.lastrowid

        # Optional: Insert into recurring_events
        recur_type = data.get('recur_type')       # 'daily', 'weekly', 'monthly'
        recur_until = data.get('recur_repeat_until')

        if recur_type and recur_until:
            print("🔁 Inserting recurring event")
            recur_sql = """
            INSERT INTO recurring_events (recur_evnt_id, recur_type, recur_repeat_until)
            VALUES (%s, %s, %s)
            """
            cursor.execute(recur_sql, (event_id, recur_type, recur_until))

        conn.commit()

        return jsonify(message="✅ Event added successfully!", event_id=event_id)

    except Exception as e:
        return jsonify(error=str(e)), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/events', methods=['GET'])
def get_user_events():
    user_id = request.args.get('user_id')
    start_filter = request.args.get('start_date')
    end_filter = request.args.get('end_date')

    if not user_id:
        return jsonify(error="Missing user_id in query params"), 400

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch holidays into a set
        cursor.execute("SELECT hldy_holiday_date FROM holidays WHERE hldy_status = 1")
        holiday_rows = cursor.fetchall()
        holiday_dates = set(row['hldy_holiday_date'] for row in holiday_rows)

        # Parse start and end filters
        start_filter_date = datetime.strptime(start_filter, "%Y-%m-%d").date() if start_filter else None
        end_filter_date = datetime.strptime(end_filter, "%Y-%m-%d").date() if end_filter else None

        # Fetch user events
        sql = """
        SELECT 
            e.evnt_id,
            e.evnt_name,
            e.evnt_title,
            e.evnt_desc,
            e.evnt_date,
            e.evnt_start_time,
            e.evnt_end_time,
            e.evnt_location,
            r.recur_type,
            r.recur_repeat_until
        FROM events e
        LEFT JOIN recurring_events r ON e.evnt_id = r.recur_evnt_id
        WHERE e.evnt_user_id = %s
        ORDER BY e.evnt_date ASC
        """

        cursor.execute(sql, (user_id,))
        rows = cursor.fetchall()
        result = []

        for row in rows:
            start_date = row['evnt_date']
            occurrences = []

            # Handle recurring events
            if row['recur_type'] and row['recur_repeat_until']:
                current_date = start_date
                end_date = row['recur_repeat_until']

                while current_date <= end_date:
                    # Skip holidays
                    if current_date not in holiday_dates:
                        # ✅ Apply date filter if provided
                        if (
                            (not start_filter_date or current_date >= start_filter_date)
                            and (not end_filter_date or current_date <= end_filter_date)
                        ):
                            occurrences.append(current_date.strftime("%Y-%m-%d"))

                    if row['recur_type'] == 'daily':
                        current_date += timedelta(days=1)
                    elif row['recur_type'] == 'weekly':
                        current_date += timedelta(weeks=1)
                    elif row['recur_type'] == 'monthly':
                        current_date += relativedelta(months=1)
                    else:
                        break
            else:
                # Single occurrence
                if start_date not in holiday_dates:
                    if (
                        (not start_filter_date or start_date >= start_filter_date)
                        and (not end_filter_date or start_date <= end_filter_date)
                    ):
                        occurrences.append(start_date.strftime("%Y-%m-%d"))

            row['occurrences'] = occurrences

            # ✅ Skip if no filtered dates
            if not occurrences:
                continue

            # Format times and dates
            row['evnt_date'] = start_date.strftime("%Y-%m-%d")
            row['evnt_start_time'] = str(row['evnt_start_time'])
            row['evnt_end_time'] = str(row['evnt_end_time'])
            if row['recur_repeat_until']:
                row['recur_repeat_until'] = row['recur_repeat_until'].strftime("%Y-%m-%d")

            result.append(row)

        return jsonify(result)

    except Exception as e:
        return jsonify(error=str(e)), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Export to Excel Logic Here ...
@app.route('/export', methods=['POST'])
def export():
    user_id = request.form['user_id']
    conn = get_connection()
    cursor = conn.cursor()
    print("Query 1: Non-recurring events")
    # 🔹 Get normal events (non-recurring)
    cursor.execute("""
        SELECT evnt_id, evnt_user_id, evnt_name, evnt_date, evnt_date, 'none'
        FROM events
        WHERE evnt_user_id = %s
          AND evnt_status = 1
          AND evnt_id NOT IN (SELECT recur_evnt_id FROM recurring_events WHERE recur_status = 1)
    """, (user_id,))
    non_recurring_events = cursor.fetchall()
    print("Query 2: Recurring events")
    # 🔹 Get recurring events with recurrence info
    cursor.execute("""
        SELECT 
            e.evnt_id, e.evnt_user_id, e.evnt_name,
            e.evnt_date, r.recur_repeat_until,
            r.recur_type
        FROM events e
        JOIN recurring_events r ON e.evnt_id = r.recur_evnt_id
        WHERE e.evnt_user_id = %s
          AND e.evnt_status = 1
          AND r.recur_status = 1
    """, (user_id,))
    recurring_events = cursor.fetchall()

    # 🔹 Merge both
    all_events = non_recurring_events + recurring_events

    # 🔹 Get holidays
    cursor.execute("SELECT hldy_holiday_date FROM holidays WHERE hldy_status = 1")
    holidays = {row[0] for row in cursor.fetchall()}

    # 🔹 Export to Excel
    file_path = f"user_{user_id}_events.xlsx"
    export_to_excel(all_events, holidays, file_path)

    cursor.close()
    conn.close()

    return send_file(file_path, as_attachment=True)

@app.route('/')
def index():
    return render_template('index.html')  # Flask will look inside templates/index.html

if __name__ == '__main__':
    app.run(debug=True)
