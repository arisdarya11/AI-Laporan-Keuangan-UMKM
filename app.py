import { useState, useEffect } from "react";
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from "recharts";

const DATA_2024 = [
  { bulan: "Jan", pemasukan: 37475000, pengeluaran: 71890000, laba: -34415000 },
  { bulan: "Feb", pemasukan: 49074000, pengeluaran: 67126000, laba: -18052000 },
  { bulan: "Mar", pemasukan: 51810000, pengeluaran: 47417000, laba: 4393000 },
  { bulan: "Apr", pemasukan: 43127000, pengeluaran: 53804000, laba: -10677000 },
  { bulan: "May", pemasukan: 62302000, pengeluaran: 87099000, laba: -24797000 },
  { bulan: "Jun", pemasukan: 40313000, pengeluaran: 68130000, laba: -27817000 },
  { bulan: "Jul", pemasukan: 39711000, pengeluaran: 57107000, laba: -17396000 },
  { bulan: "Aug", pemasukan: 62049000, pengeluaran: 70893000, laba: -8844000 },
  { bulan: "Sep", pemasukan: 60286000, pengeluaran: 67390000, laba: -7104000 },
  { bulan: "Oct", pemasukan: 46561000, pengeluaran: 63874000, laba: -17313000 },
  { bulan: "Nov", pemasukan: 48907000, pengeluaran: 56148000, laba: -7241000 },
  { bulan: "Dec", pemasukan: 71079000, pengeluaran: 68130000, laba: 2949000 },
];

const DATA_2025 = [
  { bulan: "Jan", pemasukan: 51250000, pengeluaran: 48493000, laba: 2757000 },
  { bulan: "Feb", pemasukan: 57811000, pengeluaran: 43070000, laba: 14741000 },
  { bulan: "Mar", pemasukan: 67782000, pengeluaran: 79227000, laba: -11445000 },
  { bulan: "Apr", pemasukan: 77271000, pengeluaran: 59475000, laba: 17796000 },
  { bulan: "May", pemasukan: 38519000, pengeluaran: 61367000, laba: -22848000 },
  { bulan: "Jun", pemasukan: 54552000, pengeluaran: 69324000, laba: -14772000 },
  { bulan: "Jul", pemasukan: 52790000, pengeluaran: 50144000, laba: 2646000 },
  { bulan: "Aug", pemasukan: 28445000, pengeluaran: 62055000, laba: -33610000 },
  { bulan: "Sep", pemasukan: 48309000, pengeluaran: 73344000, laba: -25035000 },
  { bulan: "Oct", pemasukan: 66122000, pengeluaran: 71862000, laba: -5740000 },
  { bulan: "Nov", pemasukan: 49510000, pengeluaran: 70733000, laba: -21223000 },
  { bulan: "Dec", pemasukan: 49501000, pengeluaran: 86095000, laba: -36594000 },
];

const KAT_DATA = [
  { name: "Beban Gaji", value: 590204000, color: "#f97316" },
  { name: "Bahan Baku", value: 449615000, color: "#eab308" },
  { name: "Beban Sewa", value: 220039000, color: "#22c55e" },
  { name: "Beban Pemasaran", value: 101242000, color: "#06b6d4" },
  { name: "Beban Keuangan", value: 83354000, color: "#8b5cf6" },
  { name: "Bahan Pembantu", value: 73982000, color: "#ec4899" },
];

const METODE_DATA = [
  { name: "Transfer BCA", value: 1532866000, color: "#3b82f6" },
  { name: "Tunai", value: 929502000, color: "#10b981" },
  { name: "Transfer BRI", value: 528538000, color: "#f59e0b" },
  { name: "QRIS", value: 136940000, color: "#a855f7" },
];

const fmt = (v) => {
  if (Math.abs(v) >= 1000000000) return `Rp ${(v / 1000000000).toFixed(1)}M`;
  if (Math.abs(v) >= 1000000) return `Rp ${(v / 1000000).toFixed(0)}jt`;
  return `Rp ${(v / 1000).toFixed(0)}rb`;
};

function AnimatedNumber({ value }) {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    let start = 0;
    const steps = 60;
    const inc = value / steps;
    let count = 0;
    const t = setInterval(() => {
      count++;
      start += inc;
      if (count >= steps) { setDisplay(value); clearInterval(t); }
      else setDisplay(Math.floor(start));
    }, 16);
    return () => clearInterval(t);
  }, [value]);
  return <span>Rp {Math.abs(display).toLocaleString("id-ID")}</span>;
}

const Tip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: "#0d1117", border: "1px solid #21262d", borderRadius: 10, padding: "10px 14px" }}>
      <p style={{ color: "#8b949e", fontSize: 11, marginBottom: 6 }}>{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color, fontSize: 12, margin: "2px 0" }}>{p.name}: {fmt(p.value)}</p>
      ))}
    </div>
  );
};

export default function App() {
  const [page, setPage] = useState("overview");
  const [tahun, setTahun] = useState("2024");
  const [visible, setVisible] = useState(true);

  const data = tahun === "2024" ? DATA_2024 : DATA_2025;
  const totalP = data.reduce((s, d) => s + d.pemasukan, 0);
  const totalK = data.reduce((s, d) => s + d.pengeluaran, 0);
  const totalL = totalP - totalK;
  const best = [...data].sort((a, b) => b.laba - a.laba)[0];
  const worst = [...data].sort((a, b) => a.laba - b.laba)[0];
  const untungCount = data.filter(d => d.laba > 0).length;

  useEffect(() => {
    setVisible(false);
    const t = setTimeout(() => setVisible(true), 100);
    return () => clearTimeout(t);
  }, [page, tahun]);

  const navItems = [
    { id: "overview", label: "Overview", icon: "▣" },
    { id: "cashflow", label: "Cashflow", icon: "◈" },
    { id: "pengeluaran", label: "Pengeluaran", icon: "◉" },
    { id: "transaksi", label: "Transaksi", icon: "◎" },
  ];

  const S = {
    wrap: { display: "flex", minHeight: "100vh", background: "#060810", color: "#e6edf3", fontFamily: "system-ui, sans-serif" },
    sidebar: { width: 215, background: "#0d1117", borderRight: "1px solid #161b22", display: "flex", flexDirection: "column", padding: "22px 12px", position: "fixed", height: "100vh", zIndex: 50 },
    main: { marginLeft: 215, flex: 1, padding: "26px 28px", overflowY: "auto" },
    card: { background: "#0d1117", border: "1px solid #161b22", borderRadius: 14 },
  };

  return (
    <div style={S.wrap}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Space+Mono:wght@700&display=swap');
        * { box-sizing: border-box; }
        .nav-btn { cursor:pointer; border-radius:9px; padding:9px 11px; display:flex; align-items:center; gap:9px; transition:all 0.2s; margin-bottom:2px; }
        .nav-btn:hover { background:rgba(88,166,255,0.08); }
        .nav-btn.active { background:rgba(88,166,255,0.12); }
        .card-h { transition:transform 0.25s, box-shadow 0.25s; }
        .card-h:hover { transform:translateY(-2px); box-shadow:0 12px 30px rgba(0,0,0,0.5) !important; }
        .fi { animation:fi 0.4s ease both; }
        .fi:nth-child(1){animation-delay:.03s}.fi:nth-child(2){animation-delay:.07s}
        .fi:nth-child(3){animation-delay:.11s}.fi:nth-child(4){animation-delay:.15s}
        .fi:nth-child(5){animation-delay:.19s}.fi:nth-child(6){animation-delay:.23s}
        @keyframes fi { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:translateY(0)} }
        .blink { animation:blink 2s ease-in-out infinite; }
        @keyframes blink { 0%,100%{opacity:1}50%{opacity:0.3} }
        .bar-a { transition:width 1s cubic-bezier(.4,0,.2,1); }
        ::-webkit-scrollbar{width:3px}::-webkit-scrollbar-track{background:#060810}::-webkit-scrollbar-thumb{background:#21262d;border-radius:3px}
      `}</style>

      {/* SIDEBAR */}
      <div style={S.sidebar}>
        <div style={{ marginBottom: 30, paddingLeft: 4 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: "linear-gradient(135deg,#58a6ff,#a78bfa)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 17, boxShadow: "0 0 20px rgba(88,166,255,0.3)" }}>💰</div>
            <div>
              <div style={{ fontFamily: "'Space Mono',monospace", fontWeight: 700, fontSize: 14, color: "#e6edf3", letterSpacing: 1 }}>FINTRACK</div>
              <div style={{ fontSize: 8, color: "#21262d", letterSpacing: 3, textTransform: "uppercase" }}>UMKM Analytics</div>
            </div>
          </div>
        </div>

        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 9, letterSpacing: 2, textTransform: "uppercase", color: "#21262d", marginBottom: 10, paddingLeft: 8 }}>MENU</div>
          {navItems.map(n => (
            <div key={n.id} className={`nav-btn ${page === n.id ? "active" : ""}`} onClick={() => setPage(n.id)}>
              <span style={{ fontSize: 14, color: page === n.id ? "#58a6ff" : "#484f58" }}>{n.icon}</span>
              <span style={{ fontSize: 13, fontWeight: page === n.id ? 600 : 400, color: page === n.id ? "#58a6ff" : "#6e7681" }}>{n.label}</span>
              {page === n.id && <div className="blink" style={{ marginLeft: "auto", width: 5, height: 5, borderRadius: "50%", background: "#58a6ff" }} />}
            </div>
          ))}
        </div>

        <div style={{ background: "#161b22", borderRadius: 11, padding: 11, border: "1px solid #21262d", marginBottom: 14 }}>
          <div style={{ fontSize: 9, color: "#21262d", letterSpacing: 2, textTransform: "uppercase", marginBottom: 9 }}>TAHUN</div>
          <div style={{ display: "flex", gap: 6 }}>
            {["2024","2025"].map(y => (
              <button key={y} onClick={() => setTahun(y)} style={{ flex: 1, padding: "7px 0", borderRadius: 7, border: "none", cursor: "pointer", fontFamily: "'Space Mono',monospace", fontWeight: 700, fontSize: 12, background: tahun === y ? "linear-gradient(135deg,#58a6ff,#a78bfa)" : "rgba(255,255,255,0.03)", color: tahun === y ? "#fff" : "#484f58", boxShadow: tahun === y ? "0 4px 14px rgba(88,166,255,0.25)" : "none" }}>{y}</button>
            ))}
          </div>
        </div>

        <div style={{ paddingTop: 12, borderTop: "1px solid #161b22", display: "flex", alignItems: "center", gap: 9 }}>
          <div style={{ width: 32, height: 32, borderRadius: "50%", background: "linear-gradient(135deg,#f97316,#fb923c)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 15 }}>👩</div>
          <div>
            <div style={{ fontSize: 11, color: "#6e7681", fontWeight: 500 }}>Dapur Ibu Sari</div>
            <div style={{ fontSize: 9, color: "#30363d" }}>2024 – 2025</div>
          </div>
        </div>
      </div>

      {/* MAIN */}
      <div style={S.main}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 26 }}>
          <div>
            <h1 style={{ fontFamily: "'Space Grotesk',sans-serif", fontWeight: 700, fontSize: 22, color: "#e6edf3", margin: 0 }}>
              {{ overview: "Ringkasan Keuangan", cashflow: "Analisis Cashflow", pengeluaran: "Breakdown Pengeluaran", transaksi: "Data Transaksi" }[page]}
            </h1>
            <p style={{ color: "#30363d", fontSize: 12, margin: "4px 0 0" }}>UD. Dapur Ibu Sari · Tahun {tahun} · 3.000 transaksi</p>
          </div>
          <div style={{ background: "#0d1117", border: "1px solid #161b22", borderRadius: 9, padding: "7px 14px", fontSize: 11, color: "#484f58" }}>
            📅 {tahun === "2024" ? "Jan – Des 2024" : "Jan – Des 2025"}
          </div>
        </div>

        {/* OVERVIEW */}
        {page === "overview" && visible && (
          <div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12, marginBottom: 16 }}>
              {[
                { label: "Total Pemasukan", val: totalP, icon: "↑", c: "#3fb950", bg: "rgba(63,185,80,0.08)", b: "rgba(63,185,80,0.2)" },
                { label: "Total Pengeluaran", val: totalK, icon: "↓", c: "#f85149", bg: "rgba(248,81,73,0.08)", b: "rgba(248,81,73,0.2)" },
                { label: "Laba / Rugi", val: totalL, icon: totalL >= 0 ? "▲" : "▼", c: totalL >= 0 ? "#3fb950" : "#f85149", bg: totalL >= 0 ? "rgba(63,185,80,0.08)" : "rgba(248,81,73,0.08)", b: totalL >= 0 ? "rgba(63,185,80,0.2)" : "rgba(248,81,73,0.2)" },
                { label: "Total Transaksi", val: null, icon: "≡", c: "#58a6ff", bg: "rgba(88,166,255,0.08)", b: "rgba(88,166,255,0.2)" },
              ].map((k, i) => (
                <div key={i} className="card-h fi" style={{ background: k.bg, border: `1px solid ${k.b}`, borderRadius: 14, padding: "18px 18px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
                    <span style={{ fontSize: 9, color: "#484f58", textTransform: "uppercase", letterSpacing: 1.2 }}>{k.label}</span>
                    <div style={{ width: 28, height: 28, borderRadius: 7, background: k.bg, border: `1px solid ${k.b}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, color: k.c }}>{k.icon}</div>
                  </div>
                  <div style={{ fontFamily: "'Space Grotesk',sans-serif", fontWeight: 700, fontSize: 16, color: "#e6edf3" }}>
                    {k.val === null ? <><span style={{ fontFamily: "'Space Mono',monospace" }}>3.000</span> <span style={{ fontSize: 11, color: "#484f58" }}>trx</span></> : <AnimatedNumber value={k.val} />}
                  </div>
                  <div style={{ marginTop: 10, height: 2, background: "rgba(255,255,255,0.04)", borderRadius: 2 }}>
                    <div style={{ height: "100%", width: "65%", background: `linear-gradient(90deg,${k.c}44,${k.c})`, borderRadius: 2 }} />
                  </div>
                </div>
              ))}
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 260px", gap: 12, marginBottom: 12 }}>
              <div className="card-h fi" style={{ ...S.card, padding: "20px 22px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                  <div>
                    <div style={{ fontFamily: "'Space Grotesk',sans-serif", fontWeight: 600, fontSize: 14, color: "#e6edf3" }}>Pemasukan vs Pengeluaran</div>
                    <div style={{ fontSize: 11, color: "#30363d", marginTop: 2 }}>Per bulan {tahun}</div>
                  </div>
                  <div style={{ display: "flex", gap: 12 }}>
                    {[["#3fb950","Pemasukan"],["#f97316","Pengeluaran"]].map(([c,l]) => (
                      <span key={l} style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 10, color: "#484f58" }}>
                        <span style={{ width: 7, height: 7, borderRadius: 2, background: c, display: "inline-block" }} />{l}
                      </span>
                    ))}
                  </div>
                </div>
                <ResponsiveContainer width="100%" height={220}>
                  <AreaChart data={data} margin={{ top: 5, right: 5, left: 5, bottom: 0 }}>
                    <defs>
                      <linearGradient id="gp" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3fb950" stopOpacity={0.25}/><stop offset="95%" stopColor="#3fb950" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="gk" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#f97316" stopOpacity={0.25}/><stop offset="95%" stopColor="#f97316" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#161b22" />
                    <XAxis dataKey="bulan" tick={{ fill: "#484f58", fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: "#484f58", fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={v => `${(v/1e6).toFixed(0)}jt`} />
                    <Tooltip content={<Tip />} />
                    <Area type="monotone" dataKey="pemasukan" name="Pemasukan" stroke="#3fb950" strokeWidth={2} fill="url(#gp)" dot={false} activeDot={{ r: 4 }} />
                    <Area type="monotone" dataKey="pengeluaran" name="Pengeluaran" stroke="#f97316" strokeWidth={2} fill="url(#gk)" dot={false} activeDot={{ r: 4 }} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {[
                  { emoji: "🏆", label: "Bulan Terbaik", name: best.bulan, val: `+${fmt(best.laba)}`, c: "#3fb950", bg: "rgba(63,185,80,0.07)", b: "rgba(63,185,80,0.15)" },
                  { emoji: "📉", label: "Bulan Terburuk", name: worst.bulan, val: fmt(worst.laba), c: "#f85149", bg: "rgba(248,81,73,0.07)", b: "rgba(248,81,73,0.15)" },
                  { emoji: "📊", label: "Bulan Untung", name: `${untungCount} / 12`, bar: untungCount / 12, c: "#58a6ff", bg: "rgba(88,166,255,0.07)", b: "rgba(88,166,255,0.15)" },
                ].map((s, i) => (
                  <div key={i} className="card-h fi" style={{ background: s.bg, border: `1px solid ${s.b}`, borderRadius: 12, padding: "14px 16px", flex: 1 }}>
                    <div style={{ fontSize: 9, color: s.c, letterSpacing: 1.5, textTransform: "uppercase", marginBottom: 8 }}>{s.emoji} {s.label}</div>
                    <div style={{ fontFamily: "'Space Mono',monospace", fontWeight: 700, fontSize: 20, color: "#e6edf3" }}>{s.name}</div>
                    {s.val && <div style={{ fontSize: 12, color: s.c, marginTop: 4 }}>{s.val}</div>}
                    {s.bar !== undefined && <div style={{ marginTop: 10, height: 3, background: "rgba(255,255,255,0.05)", borderRadius: 3 }}><div className="bar-a" style={{ height: "100%", width: `${s.bar * 100}%`, background: "linear-gradient(90deg,#58a6ff,#a78bfa)", borderRadius: 3 }} /></div>}
                  </div>
                ))}
              </div>
            </div>

            <div className="card-h fi" style={{ ...S.card, padding: "18px 20px" }}>
              <div style={{ fontFamily: "'Space Grotesk',sans-serif", fontWeight: 600, fontSize: 14, color: "#e6edf3", marginBottom: 14 }}>Metode Pembayaran</div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 10 }}>
                {METODE_DATA.map((m, i) => {
                  const total = METODE_DATA.reduce((s, d) => s + d.value, 0);
                  const pct = ((m.value / total) * 100).toFixed(1);
                  return (
                    <div key={i} style={{ background: `${m.color}0d`, border: `1px solid ${m.color}25`, borderRadius: 10, padding: "12px 14px" }}>
                      <div style={{ fontSize: 10, color: "#484f58", marginBottom: 6 }}>{m.name}</div>
                      <div style={{ fontWeight: 700, fontSize: 14, color: "#e6edf3", marginBottom: 8 }}>{fmt(m.value)}</div>
                      <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
                        <div style={{ flex: 1, height: 3, background: "rgba(255,255,255,0.05)", borderRadius: 3 }}><div className="bar-a" style={{ height: "100%", width: `${pct}%`, background: m.color, borderRadius: 3 }} /></div>
                        <span style={{ fontSize: 10, color: m.color, fontWeight: 600 }}>{pct}%</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* CASHFLOW */}
        {page === "cashflow" && visible && (
          <div>
            <div className="card-h fi" style={{ ...S.card, padding: "20px 22px", marginBottom: 12 }}>
              <div style={{ fontFamily: "'Space Grotesk',sans-serif", fontWeight: 600, fontSize: 14, color: "#e6edf3", marginBottom: 4 }}>Laba / Rugi per Bulan</div>
              <div style={{ fontSize: 11, color: "#30363d", marginBottom: 16 }}>🟢 Untung · 🔴 Rugi</div>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={data} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#161b22" vertical={false} />
                  <XAxis dataKey="bulan" tick={{ fill: "#484f58", fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#484f58", fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={v => `${(v/1e6).toFixed(0)}jt`} />
                  <Tooltip content={<Tip />} />
                  <Bar dataKey="laba" name="Laba/Rugi" radius={[5,5,0,0]}>
                    {data.map((d, i) => <Cell key={i} fill={d.laba >= 0 ? "#3fb950" : "#f85149"} opacity={0.85} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              {[{ title: "Tren Pemasukan", key: "pemasukan", c: "#3fb950" }, { title: "Tren Pengeluaran", key: "pengeluaran", c: "#f97316" }].map((ch, i) => (
                <div key={i} className="card-h fi" style={{ ...S.card, padding: "18px 20px" }}>
                  <div style={{ fontFamily: "'Space Grotesk',sans-serif", fontWeight: 600, fontSize: 13, color: "#e6edf3", marginBottom: 16 }}>{ch.title}</div>
                  <ResponsiveContainer width="100%" height={170}>
                    <LineChart data={data}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#161b22" />
                      <XAxis dataKey="bulan" tick={{ fill: "#484f58", fontSize: 10 }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fill: "#484f58", fontSize: 9 }} axisLine={false} tickLine={false} tickFormatter={v => `${(v/1e6).toFixed(0)}jt`} />
                      <Tooltip content={<Tip />} />
                      <Line type="monotone" dataKey={ch.key} name={ch.title} stroke={ch.c} strokeWidth={2.5} dot={{ r: 3, fill: ch.c }} activeDot={{ r: 5 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* PENGELUARAN */}
        {page === "pengeluaran" && visible && (
          <div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
              <div className="card-h fi" style={{ ...S.card, padding: "18px 20px" }}>
                <div style={{ fontFamily: "'Space Grotesk',sans-serif", fontWeight: 600, fontSize: 14, color: "#e6edf3", marginBottom: 2 }}>Komposisi Pengeluaran</div>
                <div style={{ fontSize: 11, color: "#30363d", marginBottom: 4 }}>Total Rp 1,73 Miliar</div>
                <ResponsiveContainer width="100%" height={260}>
                  <PieChart>
                    <Pie data={KAT_DATA} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={3} dataKey="value">
                      {KAT_DATA.map((k, i) => <Cell key={i} fill={k.color} stroke="none" />)}
                    </Pie>
                    <Tooltip formatter={v => [fmt(v), ""]} contentStyle={{ background: "#0d1117", border: "1px solid #21262d", borderRadius: 8, fontSize: 12 }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="card-h fi" style={{ ...S.card, padding: "18px 20px" }}>
                <div style={{ fontFamily: "'Space Grotesk',sans-serif", fontWeight: 600, fontSize: 14, color: "#e6edf3", marginBottom: 18 }}>Detail Kategori</div>
                {KAT_DATA.map((k, i) => {
                  const total = KAT_DATA.reduce((s, d) => s + d.value, 0);
                  const pct = ((k.value / total) * 100).toFixed(1);
                  return (
                    <div key={i} style={{ marginBottom: 14 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
                          <div style={{ width: 8, height: 8, borderRadius: 2, background: k.color }} />
                          <span style={{ fontSize: 12, color: "#8b949e" }}>{k.name}</span>
                        </div>
                        <div>
                          <span style={{ fontSize: 12, color: "#e6edf3", fontWeight: 600 }}>{fmt(k.value)}</span>
                          <span style={{ fontSize: 10, color: "#30363d", marginLeft: 6 }}>{pct}%</span>
                        </div>
                      </div>
                      <div style={{ height: 4, background: "#161b22", borderRadius: 4 }}>
                        <div className="bar-a" style={{ height: "100%", width: `${pct}%`, background: `linear-gradient(90deg,${k.color}88,${k.color})`, borderRadius: 4 }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
            <div className="card-h fi" style={{ ...S.card, padding: "18px 20px" }}>
              <div style={{ fontFamily: "'Space Grotesk',sans-serif", fontWeight: 600, fontSize: 14, color: "#e6edf3", marginBottom: 16 }}>Ranking Pengeluaran</div>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={KAT_DATA} layout="vertical" margin={{ left: 10, right: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#161b22" horizontal={false} />
                  <XAxis type="number" tick={{ fill: "#484f58", fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={v => `${(v/1e6).toFixed(0)}jt`} />
                  <YAxis type="category" dataKey="name" tick={{ fill: "#6e7681", fontSize: 11 }} axisLine={false} tickLine={false} width={112} />
                  <Tooltip content={<Tip />} />
                  <Bar dataKey="value" name="Pengeluaran" radius={[0,5,5,0]}>
                    {KAT_DATA.map((k, i) => <Cell key={i} fill={k.color} opacity={0.82} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* TRANSAKSI */}
        {page === "transaksi" && visible && (
          <div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12, marginBottom: 14 }}>
              {[
                { label: "Ringkasan 2024", p: 612694000, k: 779008000, l: -166314000 },
                { label: "Ringkasan 2025", p: 641862000, k: 775189000, l: -133327000 },
                { label: "Perkembangan", extra: true },
              ].map((r, i) => (
                <div key={i} className="card-h fi" style={{ ...S.card, padding: "16px 18px" }}>
                  <div style={{ fontSize: 9, color: "#30363d", textTransform: "uppercase", letterSpacing: 1.2, marginBottom: 12 }}>{r.label}</div>
                  {r.extra ? (
                    <>
                      <div style={{ fontSize: 11, color: "#484f58", marginBottom: 6 }}>Kerugian berkurang</div>
                      <div style={{ fontFamily: "'Space Mono',monospace", fontSize: 20, fontWeight: 700, color: "#3fb950" }}>Rp 32.9jt</div>
                      <div style={{ fontSize: 11, color: "#484f58", marginTop: 4 }}>dari 2024 → 2025 ↑</div>
                      <div style={{ marginTop: 10, height: 3, background: "#161b22", borderRadius: 3 }}><div className="bar-a" style={{ height: "100%", width: "72%", background: "linear-gradient(90deg,#3fb950,#34d399)", borderRadius: 3 }} /></div>
                    </>
                  ) : (
                    <>
                      <div style={{ fontSize: 12, color: "#3fb950", marginBottom: 3 }}>↑ {fmt(r.p)}</div>
                      <div style={{ fontSize: 12, color: "#f85149", marginBottom: 10 }}>↓ {fmt(r.k)}</div>
                      <div style={{ fontFamily: "'Space Mono',monospace", fontSize: 17, fontWeight: 700, color: r.l >= 0 ? "#3fb950" : "#f85149" }}>{fmt(r.l)}</div>
                    </>
                  )}
                </div>
              ))}
            </div>
            <div className="card-h fi" style={{ ...S.card, padding: "18px 22px" }}>
              <div style={{ fontFamily: "'Space Grotesk',sans-serif", fontWeight: 600, fontSize: 14, color: "#e6edf3", marginBottom: 4 }}>Perbandingan Laba/Rugi 2024 vs 2025</div>
              <div style={{ fontSize: 11, color: "#30363d", marginBottom: 16, display: "flex", gap: 16 }}>
                {[["#58a6ff","2024"],["#a78bfa","2025"]].map(([c,l]) => (
                  <span key={l} style={{ display: "flex", alignItems: "center", gap: 5 }}>
                    <span style={{ width: 8, height: 8, borderRadius: 2, background: c, display: "inline-block" }} />{l}
                  </span>
                ))}
              </div>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={DATA_2024.map((d, i) => ({ bulan: d.bulan, "Laba 2024": d.laba, "Laba 2025": DATA_2025[i]?.laba || 0 }))} margin={{ top: 5, right: 10, left: 10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#161b22" vertical={false} />
                  <XAxis dataKey="bulan" tick={{ fill: "#484f58", fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#484f58", fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={v => `${(v/1e6).toFixed(0)}jt`} />
                  <Tooltip content={<Tip />} />
                  <Bar dataKey="Laba 2024" fill="#58a6ff" opacity={0.78} radius={[4,4,0,0]} />
                  <Bar dataKey="Laba 2025" fill="#a78bfa" opacity={0.78} radius={[4,4,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
