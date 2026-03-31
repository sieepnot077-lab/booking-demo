from datetime import datetime
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

from database import (
    create_appointment,
    get_appointment,
    get_appointments,
    init_db,
    update_appointment_status,
)


BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
app.config["SECRET_KEY"] = "demo-booking-secret"

STATUS_OPTIONS = ["pending", "confirmed", "completed", "cancelled"]
HISTORY_STATUSES = ["completed", "cancelled"]
THAI_MONTHS = [
    "",
    "มกราคม",
    "กุมภาพันธ์",
    "มีนาคม",
    "เมษายน",
    "พฤษภาคม",
    "มิถุนายน",
    "กรกฎาคม",
    "สิงหาคม",
    "กันยายน",
    "ตุลาคม",
    "พฤศจิกายน",
    "ธันวาคม",
]
STATUS_LABELS = {
    "pending": "รอดำเนินการ",
    "confirmed": "ยืนยันแล้ว",
    "completed": "เสร็จสิ้น",
    "cancelled": "ยกเลิก",
}
THAI_MONTH_OPTIONS = [
    {"value": f"{index:02d}", "label": month_name}
    for index, month_name in enumerate(THAI_MONTHS)
    if index > 0
]


def format_thai_date(value):
    if not value:
        return "-"

    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return value

    return f"{parsed.day} {THAI_MONTHS[parsed.month]} {parsed.year + 543}"


def format_thai_time(value):
    if not value:
        return "-"

    try:
        parsed = datetime.strptime(value, "%H:%M")
    except ValueError:
        return value

    return f"{parsed.hour:02d}:{parsed.minute:02d} น."


def format_thai_datetime(date_value, time_value):
    return f"{format_thai_date(date_value)} เวลา {format_thai_time(time_value)}"


def normalize_booking_date(value):
    cleaned = value.strip()
    date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y"]

    for date_format in date_formats:
        try:
            parsed = datetime.strptime(cleaned, date_format)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue

    try:
        day, month, year = cleaned.split("/")
        if len(year) == 4 and int(year) > 2400:
            parsed = datetime(int(year) - 543, int(month), int(day))
            return parsed.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        pass

    raise ValueError("invalid date")


def normalize_booking_time(value):
    cleaned = value.strip()
    time_formats = ["%H:%M", "%I:%M %p", "%I:%M%p"]

    for time_format in time_formats:
        try:
            parsed = datetime.strptime(cleaned.upper(), time_format)
            return parsed.strftime("%H:%M")
        except ValueError:
            continue

    raise ValueError("invalid time")


@app.context_processor
def inject_template_helpers():
    current_thai_year = datetime.now().year + 543
    return {
        "status_labels": STATUS_LABELS,
        "thai_month_options": THAI_MONTH_OPTIONS,
        "thai_year_options": [str(year) for year in range(current_thai_year, current_thai_year + 3)],
        "day_options": [f"{day:02d}" for day in range(1, 32)],
        "hour_options": [f"{hour:02d}" for hour in range(0, 24)],
        "minute_options": ["00", "15", "30", "45"],
    }


@app.template_filter("thai_date")
def thai_date_filter(value):
    return format_thai_date(value)


@app.template_filter("thai_time")
def thai_time_filter(value):
    return format_thai_time(value)


@app.template_filter("thai_datetime")
def thai_datetime_filter(appointment):
    return format_thai_datetime(
        appointment.get("booking_date"),
        appointment.get("booking_time"),
    )


@app.route("/", methods=["GET"])
def booking_form():
    return render_template("booking_form.html", form_data={})


@app.route("/book", methods=["POST"])
def book_appointment():
    booking_day = request.form.get("booking_day", "").strip()
    booking_month = request.form.get("booking_month", "").strip()
    booking_year = request.form.get("booking_year", "").strip()
    booking_hour = request.form.get("booking_hour", "").strip()
    booking_minute = request.form.get("booking_minute", "").strip()

    form_data = {
        "customer_name": request.form.get("customer_name", "").strip(),
        "phone": request.form.get("phone", "").strip(),
        "booking_day": booking_day,
        "booking_month": booking_month,
        "booking_year": booking_year,
        "booking_hour": booking_hour,
        "booking_minute": booking_minute,
        "note": request.form.get("note", "").strip(),
    }

    if not all(
        [
            form_data["customer_name"],
            form_data["phone"],
            form_data["booking_day"],
            form_data["booking_month"],
            form_data["booking_year"],
            form_data["booking_hour"],
            form_data["booking_minute"],
        ]
    ):
        flash("กรุณากรอกชื่อ เบอร์โทร วันที่ และเวลาให้ครบ", "error")
        return render_template("booking_form.html", form_data=form_data), 400

    try:
        booking_date_input = f"{booking_day}/{booking_month}/{booking_year}"
        booking_time_input = f"{booking_hour}:{booking_minute}"
        normalized_data = {
            "customer_name": form_data["customer_name"],
            "phone": form_data["phone"],
            "booking_date": normalize_booking_date(booking_date_input),
            "booking_time": normalize_booking_time(booking_time_input),
            "note": form_data["note"],
        }
    except ValueError:
        flash("กรุณาเลือกวันที่และเวลาให้ถูกต้อง", "error")
        return render_template("booking_form.html", form_data=form_data), 400

    appointment_id = create_appointment(**normalized_data)
    return redirect(url_for("booking_success", appointment_id=appointment_id))


@app.route("/success/<int:appointment_id>", methods=["GET"])
def booking_success(appointment_id: int):
    appointment = get_appointment(appointment_id)
    if appointment is None:
        flash("ไม่พบข้อมูลการจองคิว", "error")
        return redirect(url_for("booking_form"))

    return render_template("booking_success.html", appointment=appointment)


@app.route("/admin/appointments", methods=["GET"])
def admin_appointments():
    selected_status = request.args.get("status", "").strip()
    selected_date = request.args.get("date", "").strip()

    appointments = get_appointments(
        status=selected_status or None,
        booking_date=selected_date or None,
        include_history=False,
    )

    return render_template(
        "admin_appointments.html",
        appointments=appointments,
        status_options=STATUS_OPTIONS,
        selected_status=selected_status,
        selected_date=selected_date,
        page_title="รายการคิวปัจจุบัน",
        page_description="หน้านี้แสดงเฉพาะคิวที่ยังอยู่ระหว่างดำเนินการ",
        is_history_view=False,
    )


@app.route("/admin/history", methods=["GET"])
def admin_history():
    selected_status = request.args.get("status", "").strip()
    selected_date = request.args.get("date", "").strip()

    history_status = selected_status if selected_status in HISTORY_STATUSES else None

    appointments = get_appointments(
        status=history_status,
        booking_date=selected_date or None,
        include_history=True,
    )

    return render_template(
        "admin_appointments.html",
        appointments=appointments,
        status_options=HISTORY_STATUSES,
        selected_status=history_status or "",
        selected_date=selected_date,
        page_title="ประวัติการจองคิว",
        page_description="คิวที่เสร็จสิ้นหรือยกเลิกแล้วจะถูกเก็บไว้ที่นี่",
        is_history_view=True,
    )


@app.route("/admin/appointments/<int:appointment_id>/status", methods=["POST"])
def change_appointment_status(appointment_id: int):
    next_status = request.form.get("status", "").strip()
    redirect_target = request.form.get("redirect_to", "admin_appointments").strip()

    if next_status not in STATUS_OPTIONS:
        flash("สถานะที่เลือกไม่ถูกต้อง", "error")
        return redirect(url_for("admin_appointments"))

    updated = update_appointment_status(appointment_id, next_status)
    if updated:
        if next_status in HISTORY_STATUSES:
            flash("อัปเดตสถานะเรียบร้อย และย้ายรายการไปที่ประวัติแล้ว", "success")
        else:
            flash("อัปเดตสถานะคิวเรียบร้อย", "success")
    else:
        flash("ไม่พบคิวที่ต้องการอัปเดต", "error")

    destination = "admin_history" if redirect_target == "admin_history" else "admin_appointments"
    return redirect(url_for(destination))


def main():
    init_db()
    app.run(debug=True)


if __name__ == "__main__":
    main()
