import { useState, useEffect, useRef } from "react";
import axios from "axios";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from "recharts";

const API = "http://127.0.0.1:8000";

const TRAINS = [
  { id: "TRAIN-01", section: "SEC-01", limit: 110, incident: 0.02 },
  { id: "TRAIN-02", section: "SEC-03", limit: 130, incident: 0.01 },
  { id: "TRAIN-03", section: "SEC-02", limit: 100, incident: 0.05 },
];

function randomEvent(train) {
  const speed = parseFloat((Math.random() * train.limit * 0.9 + 30).toFixed(1));
  const ratio = speed / train.limit;
  return {
    train_id: train.id,
    section_id: train.section,
    speed_kmh: speed,
    signal_aspect: ratio > 0.85 ? "green" : ratio > 0.5 ? "yellow" : "red",
    rfid_read_success: Math.random() > 0.05 ? 1 : 0,
    radio_packet_loss_pct: parseFloat((Math.random() * 8).toFixed(2)),
    weather_index: parseFloat((Math.random() * 0.4).toFixed(3)),
    freight_load_tonnes: parseFloat((Math.random() * 1500 + 200).toFixed(1)),
    deceleration_rate: parseFloat((Math.random() * 0.4 + 0.4).toFixed(3)),
    section_speed_limit: train.limit,
    section_incident_rate: train.incident,
  };
}

export default function App() {
  const [trainData, setTrainData] = useState({});
  const [alerts, setAlerts]       = useState([]);
  const [maHistory, setMaHistory] = useState([]);
  const [tick, setTick]           = useState(0);
  const tickRef = useRef(0);

  useEffect(() => {
    const interval = setInterval(async () => {
      tickRef.current += 1;
      const t = tickRef.current;
      setTick(t);

      const newData = {};
      const newAlerts = [];
      let maPoint = { tick: t };

      for (const train of TRAINS) {
        const event = randomEvent(train);

        try {
          const [maRes, speedRes, anomalyRes] = await Promise.all([
            axios.post(`${API}/predict/ma`,     event),
            axios.post(`${API}/predict/speed`,  event),
            axios.post(`${API}/detect/anomaly`, event),
          ]);

          newData[train.id] = {
            speed:    event.speed_kmh,
            ma:       maRes.data.predicted_ma_metres,
            advisory: speedRes.data.advisory_speed_kmh,
            confidence: maRes.data.confidence,
            anomaly:  anomalyRes.data,
            signal:   event.signal_aspect,
            weather:  event.weather_index,
          };

          maPoint[train.id] = maRes.data.predicted_ma_metres;

          if (anomalyRes.data.is_anomaly) {
            newAlerts.push({
              id: Date.now() + train.id,
              train: train.id,
              severity: anomalyRes.data.severity,
              msg: anomalyRes.data.description,
              time: new Date().toLocaleTimeString(),
            });
          }
        } catch (e) {
          console.error(e);
        }
      }

      setTrainData(newData);
      setMaHistory(prev => [...prev.slice(-20), maPoint]);
      if (newAlerts.length > 0) {
        setAlerts(prev => [...newAlerts, ...prev].slice(0, 10));
      }
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  const signalColor = (s) =>
    s === "green" ? "#16a34a" : s === "yellow" ? "#ca8a04" : "#dc2626";

  const severityColor = (s) =>
    s === "CRITICAL" ? "#dc2626" : s === "WARNING" ? "#ca8a04" : "#2563eb";

  return (
    <div style={{ background: "#0f172a", minHeight: "100vh",
      color: "#e2e8f0", fontFamily: "sans-serif", padding: "20px" }}>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center",
        gap: 12, marginBottom: 24 }}>
        <span style={{ fontSize: 28 }}>🚆</span>
        <div>
          <h1 style={{ margin: 0, fontSize: 22, color: "#f8fafc" }}>
            SmartKavach NMS Dashboard
          </h1>
          <p style={{ margin: 0, fontSize: 12, color: "#94a3b8" }}>
            AI-Enhanced Train Collision Avoidance System · Live
          </p>
        </div>
        <div style={{ marginLeft: "auto", background: "#16a34a",
          padding: "4px 12px", borderRadius: 20, fontSize: 12 }}>
          ● LIVE
        </div>
      </div>

      {/* Train Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)",
        gap: 16, marginBottom: 24 }}>
        {TRAINS.map(train => {
          const d = trainData[train.id];
          return (
            <div key={train.id} style={{ background: "#1e293b",
              borderRadius: 12, padding: 16,
              border: d?.anomaly?.is_anomaly
                ? "1px solid #dc2626" : "1px solid #334155" }}>
              <div style={{ display: "flex", justifyContent: "space-between",
                alignItems: "center", marginBottom: 12 }}>
                <span style={{ fontWeight: 600, fontSize: 15 }}>{train.id}</span>
                <span style={{ width: 12, height: 12, borderRadius: "50%",
                  background: d ? signalColor(d.signal) : "#475569",
                  display: "inline-block" }} />
              </div>
              {d ? (
                <>
                  <div style={{ display: "grid",
                    gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                    <div style={{ background: "#0f172a", borderRadius: 8, padding: 10 }}>
                      <div style={{ fontSize: 11, color: "#94a3b8" }}>Speed</div>
                      <div style={{ fontSize: 20, fontWeight: 700,
                        color: "#38bdf8" }}>{d.speed}</div>
                      <div style={{ fontSize: 10, color: "#64748b" }}>km/h</div>
                    </div>
                    <div style={{ background: "#0f172a", borderRadius: 8, padding: 10 }}>
                      <div style={{ fontSize: 11, color: "#94a3b8" }}>Advisory</div>
                      <div style={{ fontSize: 20, fontWeight: 700,
                        color: "#34d399" }}>{d.advisory}</div>
                      <div style={{ fontSize: 10, color: "#64748b" }}>km/h</div>
                    </div>
                    <div style={{ background: "#0f172a", borderRadius: 8, padding: 10 }}>
                      <div style={{ fontSize: 11, color: "#94a3b8" }}>MA Distance</div>
                      <div style={{ fontSize: 20, fontWeight: 700,
                        color: "#a78bfa" }}>{d.ma}m</div>
                      <div style={{ fontSize: 10, color: "#64748b" }}>{d.confidence}</div>
                    </div>
                    <div style={{ background: "#0f172a", borderRadius: 8, padding: 10 }}>
                      <div style={{ fontSize: 11, color: "#94a3b8" }}>Weather</div>
                      <div style={{ fontSize: 20, fontWeight: 700,
                        color: d.weather > 0.5 ? "#f87171" : "#34d399" }}>
                        {(d.weather * 100).toFixed(0)}%
                      </div>
                      <div style={{ fontSize: 10, color: "#64748b" }}>severity</div>
                    </div>
                  </div>
                  {d.anomaly?.is_anomaly && (
                    <div style={{ marginTop: 10, background: "#450a0a",
                      border: "1px solid #dc2626", borderRadius: 8,
                      padding: "8px 12px", fontSize: 12, color: "#fca5a5" }}>
                      ⚠️ {d.anomaly.severity}: {d.anomaly.description}
                    </div>
                  )}
                </>
              ) : (
                <div style={{ color: "#475569", fontSize: 13 }}>
                  Waiting for data...
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* MA Chart + Alerts */}
      <div style={{ display: "grid",
        gridTemplateColumns: "2fr 1fr", gap: 16 }}>

        {/* MA Chart */}
        <div style={{ background: "#1e293b", borderRadius: 12, padding: 16 }}>
          <h3 style={{ margin: "0 0 16px", fontSize: 14, color: "#94a3b8" }}>
            Movement Authority — Live (metres)
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={maHistory}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="tick" stroke="#475569" tick={{ fontSize: 10 }} />
              <YAxis stroke="#475569" tick={{ fontSize: 10 }} />
              <Tooltip contentStyle={{ background: "#1e293b",
                border: "1px solid #334155", borderRadius: 8 }} />
              <Legend />
              <Line type="monotone" dataKey="TRAIN-01"
                stroke="#38bdf8" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="TRAIN-02"
                stroke="#34d399" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="TRAIN-03"
                stroke="#a78bfa" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Alerts */}
        <div style={{ background: "#1e293b", borderRadius: 12, padding: 16 }}>
          <h3 style={{ margin: "0 0 16px", fontSize: 14, color: "#94a3b8" }}>
            Anomaly Alert Feed
          </h3>
          {alerts.length === 0 ? (
            <div style={{ color: "#475569", fontSize: 13 }}>
              ✅ No anomalies detected
            </div>
          ) : (
            alerts.map(a => (
              <div key={a.id} style={{ marginBottom: 8,
                background: "#0f172a", borderRadius: 8,
                padding: "8px 12px",
                borderLeft: `3px solid ${severityColor(a.severity)}` }}>
                <div style={{ display: "flex",
                  justifyContent: "space-between", marginBottom: 2 }}>
                  <span style={{ fontSize: 12, fontWeight: 600,
                    color: severityColor(a.severity) }}>
                    {a.severity}
                  </span>
                  <span style={{ fontSize: 10,
                    color: "#64748b" }}>{a.time}</span>
                </div>
                <div style={{ fontSize: 11,
                  color: "#cbd5e1" }}>{a.train}</div>
                <div style={{ fontSize: 11,
                  color: "#94a3b8" }}>{a.msg}</div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}