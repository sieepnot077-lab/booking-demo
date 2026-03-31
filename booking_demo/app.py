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


@app.route("/", methods=["GET"])
def booking_form():
    return render_template("booking_form.html")


@app.route("/book", methods=["POST"])
def book_appointment():
    form_data = {
        "customer_name": request.form.get("customer_name", "").strip(),
        "phone": request.form.get("phone", "").strip(),
        "booking_date": request.form.get("booking_date", "").strip(),
        "booking_time": request.form.get("booking_time", "").strip(),
        "note": request.form.get("note", "").strip(),
    }

    if not all(
        [
            form_data["customer_name"],
            form_data["phone"],
            form_data["booking_date"],
            form_data["booking_time"],
        ]
    ):
        flash("กรุณากรอกชื่อ เบอร์โทร วันที่ และเวลาให้ครบ", "error")
        return render_template("booking_form.html", form_data=form_data), 400

    appointment_id = create_appointment(**form_data)
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
    )

    return render_template(
        "admin_appointments.html",
        appointments=appointments,
        status_options=STATUS_OPTIONS,
        selected_status=selected_status,
        selected_date=selected_date,
    )


@app.route("/admin/appointments/<int:appointment_id>/status", methods=["POST"])
def change_appointment_status(appointment_id: int):
    next_status = request.form.get("status", "").strip()

    if next_status not in STATUS_OPTIONS:
        flash("สถานะที่เลือกไม่ถูกต้อง", "error")
        return redirect(url_for("admin_appointments"))

    updated = update_appointment_status(appointment_id, next_status)
    if updated:
        flash("อัปเดตสถานะคิวเรียบร้อย", "success")
    else:
        flash("ไม่พบคิวที่ต้องการอัปเดต", "error")

    return redirect(url_for("admin_appointments"))


def main():
    init_db()
    app.run(debug=True)


if __name__ == "__main__":
    main()
