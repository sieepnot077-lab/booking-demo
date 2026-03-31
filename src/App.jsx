import { useState } from "react";

const defaultForm = {
  email: "",
  password: "",
  remember: true,
};

export default function App() {
  const [form, setForm] = useState(defaultForm);
  const [message, setMessage] = useState("");
  const [loggedInUser, setLoggedInUser] = useState("");

  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;

    setForm((current) => ({
      ...current,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    if (!form.email || !form.password) {
      setMessage("กรุณากรอกอีเมลและรหัสผ่านให้ครบ");
      return;
    }

    setMessage("");
    setLoggedInUser(form.email);
  };

  const handleLogout = () => {
    setLoggedInUser("");
    setForm(defaultForm);
    setMessage("");
  };

  if (loggedInUser) {
    return (
      <main className="dashboard-shell">
        <section className="dashboard-card">
          <div className="dashboard-badge">เข้าสู่ระบบสำเร็จ</div>
          <h1>ยินดีต้อนรับ, {loggedInUser}</h1>
          <p>
            ตอนนี้คุณอยู่ในหน้าหลังล็อกอินแล้ว หน้านี้สามารถต่อยอดเป็นแดชบอร์ด,
            หน้าสมาชิก, หรือหน้าจัดการข้อมูลได้ตามต้องการ
          </p>

          <div className="dashboard-grid">
            <article>
              <h2>สถานะบัญชี</h2>
              <p>บัญชีของคุณพร้อมใช้งาน และสามารถเชื่อมต่อกับ backend จริงได้ต่อทันที</p>
            </article>
            <article>
              <h2>งานถัดไป</h2>
              <p>เพิ่ม API login, token, และระบบป้องกันหน้า private route ได้ในขั้นต่อไป</p>
            </article>
          </div>

          <button type="button" className="primary-button dashboard-button" onClick={handleLogout}>
            ออกจากระบบ
          </button>
        </section>
      </main>
    );
  }

  return (
    <main className="page-shell">
      <section className="hero-panel">
        <div className="brand-pill">ระบบล็อกอิน React</div>
        <h1>เข้าสู่ระบบของคุณด้วยหน้าล็อกอินที่สวยงามและใช้งานง่าย</h1>
        <p>
          หน้าเว็บนี้สร้างด้วย React และ CSS แบบล้วน พร้อมต่อยอดเชื่อมกับระบบ
          backend จริงในภายหลังได้ทันที
        </p>

        <div className="feature-grid">
          <article>
            <span>01</span>
            <h2>รองรับทุกหน้าจอ</h2>
            <p>แสดงผลได้ดีทั้งบนมือถือ แท็บเล็ต และคอมพิวเตอร์</p>
          </article>
          <article>
            <span>02</span>
            <h2>พร้อมต่อยอดระบบจริง</h2>
            <p>มี state สำหรับ validation, API login และ session logic ให้ต่อได้ง่าย</p>
          </article>
          <article>
            <span>03</span>
            <h2>ปรับแต่งได้ง่าย</h2>
            <p>โครงสร้าง class และ CSS อ่านง่าย แก้สีและเลย์เอาต์ได้สะดวก</p>
          </article>
        </div>
      </section>

      <section className="login-panel">
        <div className="login-card">
          <div className="login-header">
            <p className="eyebrow">ยินดีต้อนรับกลับ</p>
            <h2>เข้าสู่ระบบ</h2>
            <p>กรอกข้อมูลของคุณเพื่อเข้าใช้งานระบบ</p>
          </div>

          <form className="login-form" onSubmit={handleSubmit}>
            <label>
              อีเมล
              <input
                type="email"
                name="email"
                placeholder="example@email.com"
                value={form.email}
                onChange={handleChange}
              />
            </label>

            <label>
              รหัสผ่าน
              <input
                type="password"
                name="password"
                placeholder="กรอกรหัสผ่าน"
                value={form.password}
                onChange={handleChange}
              />
            </label>

            <div className="form-options">
              <label className="checkbox-row">
                <input
                  type="checkbox"
                  name="remember"
                  checked={form.remember}
                  onChange={handleChange}
                />
                <span>จดจำฉันไว้</span>
              </label>

              <button type="button" className="link-button">
                ลืมรหัสผ่าน?
              </button>
            </div>

            <button type="submit" className="primary-button">
              เข้าสู่ระบบ
            </button>

            <div className="divider">
              <span>หรือเข้าสู่ระบบด้วย</span>
            </div>

            <div className="social-row">
              <button type="button" className="social-button">
                Google
              </button>
              <button type="button" className="social-button">
                GitHub
              </button>
            </div>
          </form>

          <footer className="login-footer">
            <p>
              ยังไม่มีบัญชี? <a href="/">สมัครสมาชิก</a>
            </p>
            {message ? <div className="status-message">{message}</div> : null}
          </footer>
        </div>
      </section>
    </main>
  );
}
