import "./Layout.css";
import logo from "../assets/logo.png";

export default function Layout({ children }) {
  return (
    <div className="layout">
      <header className="header">
        <h1>AI-система обработки обращений граждан</h1>
        <img src={logo} className="header-icon" />
      </header>

      <main className="content">{children}</main>

      <footer className="footer">
        © 2026 NAA ietn SUSU Все права защищены
      </footer>
    </div>
  );
}
