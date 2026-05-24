import React from 'react';
import { DistrictData } from '../data/districts';
import { LiveWeatherReading } from '../services/liveWeather';
import { Thermometer, Droplets, Wind, ShieldCheck, AlertTriangle, CloudRain, TrendingUp, Zap, HelpCircle, Radio, Sun, Gauge, Compass } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

interface AnalysisSidebarProps {
  selectedDistrict: DistrictData;
  selectedDate: string;
  liveWeather: LiveWeatherReading | null;
  hourlyForecast: Array<{ time: string; precipProbability: number; rainfallMm: number; tempC: number }>;
  backendPrediction: { threat_pct: number; rain_mm: number; will_rain: boolean; source: 'backend' | 'simulated' } | null;
  isLoadingLive: boolean;
}

export const AnalysisSidebar: React.FC<AnalysisSidebarProps> = ({
  selectedDistrict, selectedDate, liveWeather, hourlyForecast, backendPrediction, isLoadingLive
}) => {
  const threatPct = backendPrediction?.threat_pct ?? selectedDistrict.threatProbability;
  const rainMm = backendPrediction?.rain_mm ?? selectedDistrict.predictedRainfallMm;
  const isRainThreat = threatPct > 50;
  const isHighThreat = threatPct > 75;
  const predictionSource = backendPrediction?.source ?? 'simulated';

  const mountainData = hourlyForecast.length > 0
    ? hourlyForecast.map(h => ({ time: h.time, probability: h.precipProbability, rainfallMm: h.rainfallMm, tempC: h.tempC }))
    : [];

  const liveTemp = liveWeather?.temperatureC;
  const liveRH = liveWeather?.relativeHumidity;
  const liveDew = liveWeather?.dewPointC;
  const liveSolar = liveWeather?.shortwaveRadiation;
  const liveWind = liveWeather?.windSpeedMs;
  const liveDewSpread = liveWeather ? (liveWeather.temperatureC - liveWeather.dewPointC) : null;

  return (
    <div className="bg-[#0b1329]/90 backdrop-blur-md rounded-2xl border border-slate-800 p-5 shadow-2xl flex flex-col space-y-5 h-full overflow-y-auto custom-scrollbar">
      {/* Header */}
      <div className="flex flex-col space-y-3 pb-4 border-b border-slate-800">
        <div className="flex items-start justify-between gap-2">
          <div>
            <div className="text-[11px] font-mono tracking-wider text-slate-400 uppercase flex items-center gap-1.5">
              {selectedDistrict.region} — {selectedDistrict.id}
              <span className="text-red-400 flex items-center gap-0.5"><Radio className="w-2.5 h-2.5 animate-pulse" /> live</span>
            </div>
            <h2 className="text-2xl font-black text-white tracking-tight mt-0.5">{selectedDistrict.name}</h2>
            <div className="text-[10px] text-slate-500 font-mono mt-0.5">
              {selectedDate} · {liveWeather ? new Date(liveWeather.observationTime).toLocaleTimeString() : 'Awaiting data...'}
            </div>
          </div>
          <div className={`px-3 py-1.5 rounded-xl border flex items-center gap-2 shadow-lg shrink-0 ${isHighThreat ? 'bg-red-950/80 border-red-500 text-red-400 shadow-red-500/20 animate-pulse' : isRainThreat ? 'bg-amber-950/80 border-amber-500 text-amber-400 shadow-amber-500/10' : 'bg-emerald-950/80 border-emerald-500 text-emerald-400 shadow-emerald-500/10'}`}>
            {isHighThreat ? <AlertTriangle className="w-4 h-4 shrink-0" /> : isRainThreat ? <CloudRain className="w-4 h-4 shrink-0" /> : <ShieldCheck className="w-4 h-4 shrink-0" />}
            <div className="flex flex-col text-right"><span className="text-[10px] font-bold tracking-wider uppercase opacity-80 leading-none">Threat</span><span className="text-xs font-black font-mono leading-tight">{isHighThreat ? 'SEVERE' : isRainThreat ? 'RAIN' : 'SAFE'}</span></div>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3 pt-1">
          <div className="bg-[#020617] p-3 rounded-xl border border-slate-800 flex items-center justify-between">
            <div><div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Classification</div><div className="text-xl font-bold font-mono text-white mt-0.5">{threatPct.toFixed(1)}%</div><div className="text-[9px] text-slate-500">XGBoost {predictionSource === 'backend' ? '(your .pkl)' : '(sim)'}</div></div>
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs font-mono ${isRainThreat ? 'bg-red-500/20 text-red-400 border border-red-500/40' : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'}`}>{isRainThreat ? 'YES' : 'NO'}</div>
          </div>
          <div className="bg-[#020617] p-3 rounded-xl border border-slate-800 flex items-center justify-between">
            <div><div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Regression</div><div className="text-xl font-bold font-mono text-sky-400 mt-0.5">{rainMm.toFixed(1)} mm</div><div className="text-[9px] text-slate-500">LightGBM Log-Transform</div></div>
            <div className="w-8 h-8 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400"><Droplets className="w-4 h-4" /></div>
          </div>
        </div>
        <div className={`text-[10px] font-mono px-2 py-1 rounded text-center ${predictionSource === 'backend' ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/30' : 'bg-amber-500/10 text-amber-300 border border-amber-500/30'}`}>
          {predictionSource === 'backend' ? '✓ Inference by YOUR FastAPI backend (.pkl models)' : '⚠ Backend offline — simulator active'}
        </div>
      </div>

      {/* LIVE TELEMETRY */}
      <div className="space-y-2">
        <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center justify-between">
          <span className="flex items-center gap-1.5"><Radio className="w-3.5 h-3.5 text-red-400 animate-pulse" />Real-Time Telemetry</span>
          <span className="text-[10px] font-mono text-slate-500 font-normal">Live Stream</span>
        </h3>
        <div className="grid grid-cols-2 gap-2.5">
          <LiveStat icon={<Thermometer className="w-3.5 h-3.5 text-amber-400" />} label="Live Temp" value={liveTemp != null ? `${liveTemp.toFixed(1)}°C` : '—'} sub={liveDewSpread != null ? `Dew Spread: ${liveDewSpread.toFixed(1)}°` : 'loading'} loading={isLoadingLive} />
          <LiveStat icon={<Droplets className="w-3.5 h-3.5 text-sky-400" />} label="Live RH" value={liveRH != null ? `${liveRH.toFixed(0)}%` : '—'} sub="Relative Humidity" loading={isLoadingLive} />
          <LiveStat icon={<Sun className="w-3.5 h-3.5 text-yellow-400" />} label="Solar Rad" value={liveSolar != null ? `${liveSolar.toFixed(0)} W/m²` : '—'} sub="Shortwave (live)" loading={isLoadingLive} />
          <LiveStat icon={<Gauge className="w-3.5 h-3.5 text-purple-400" />} label="Dew Point" value={liveDew != null ? `${liveDew.toFixed(1)}°C` : '—'} sub="Live @ 2m" loading={isLoadingLive} />
        </div>
        <div className="bg-[#020617] p-3 rounded-xl border border-slate-800 flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400 flex items-center gap-1.5 mb-0.5"><Wind className="w-3.5 h-3.5 text-slate-400" />Live Wind Vector</div>
            {liveWeather ? <div className="text-xs font-mono text-white">u: {liveWeather.windVectorX} m/s  |  v: {liveWeather.windVectorY} m/s</div> : <div className="text-xs font-mono text-slate-500">Fetching...</div>}
          </div>
          <div className="text-right"><div className="text-xs font-bold font-mono text-sky-400">{liveWind != null ? `${liveWind.toFixed(1)} m/s` : '—'}</div><div className="text-[9px] text-slate-500 flex items-center gap-1 justify-end"><Compass className="w-2.5 h-2.5" />{liveWeather ? `${liveWeather.windDirectionDeg}°` : ''}</div></div>
        </div>
      </div>

      {/* 24-Hour Forecast Mountain */}
      <div className="space-y-2">
        <div className="flex items-center justify-between"><h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5"><TrendingUp className="w-3.5 h-3.5 text-sky-400" />24-Hour Forecast Mountain</h3><span className="text-[10px] text-slate-500 font-mono">{mountainData.length}h ahead</span></div>
        <div className="bg-[#020617] p-3 rounded-xl border border-slate-800/80 h-44 w-full pt-3">
          {mountainData.length === 0 ? (
            <div className="h-full flex items-center justify-center text-xs text-slate-500">{isLoadingLive ? 'Loading...' : 'No forecast data'}</div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={mountainData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                <defs><linearGradient id="colorProb" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor={isRainThreat ? '#ef4444' : '#38bdf8'} stopOpacity={0.8} /><stop offset="95%" stopColor={isRainThreat ? '#ef4444' : '#38bdf8'} stopOpacity={0.05} /></linearGradient></defs>
                <XAxis dataKey="time" stroke="#64748b" fontSize={9} tickLine={false} axisLine={false} interval={2} />
                <YAxis stroke="#64748b" fontSize={9} tickLine={false} axisLine={false} domain={[0, 100]} />
                <Tooltip content={({ active, payload }) => { if (active && payload && payload.length) { const d = payload[0].payload; return (<div className="bg-[#0f172a] border border-slate-700 p-2 rounded-lg shadow-xl text-xs"><div className="font-bold text-slate-300 font-mono">{d.time}</div><div className="text-red-400">Rain: {d.probability}%</div>{d.rainfallMm > 0 && <div className="text-sky-400">Vol: {d.rainfallMm} mm</div>}<div className="text-amber-400">Temp: {d.tempC}°C</div></div>); } return null; }} />
                <ReferenceLine y={50} stroke="#ef4444" strokeDasharray="3 3" strokeWidth={1} />
                <Area type="monotone" dataKey="probability" stroke={isRainThreat ? '#ef4444' : '#38bdf8'} strokeWidth={2} fillOpacity={1} fill="url(#colorProb)" />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Feature Pipeline (Lags) */}
      <div className="space-y-2 pt-2 border-t border-slate-800">
        <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5"><Zap className="w-3.5 h-3.5 text-indigo-400" />Temporal Lags (Historical)</h3>
        <div className="bg-[#020617] p-3 rounded-xl border border-slate-800 space-y-2">
          {[{ label: 'Lag 1d', val: selectedDistrict.lag1Rain, color: 'bg-sky-400', max: 1.5 }, { label: 'Lag 3d Front', val: selectedDistrict.lag3Rain, color: 'bg-indigo-400', max: 0.8 }, { label: 'Lag 7d Accum', val: selectedDistrict.lag7Rain, color: 'bg-purple-400', max: 0.4 }].map((row) => (
            <div key={row.label}><div className="flex items-center justify-between text-xs"><span className="text-slate-400">{row.label}:</span><span className="font-mono font-bold text-white">{row.val} mm</span></div><div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mt-0.5"><div className={`${row.color} h-full rounded-full`} style={{ width: `${Math.min(100, row.val * row.max)}%` }} /></div></div>
          ))}
        </div>
        <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800/80 text-[11px] text-slate-400 space-y-1">
          <div className="font-bold text-white flex items-center gap-1.5"><HelpCircle className="w-3 h-3 text-sky-400" />Live Interpretation</div>
          <p className="text-xs leading-relaxed">
            {liveWeather && isRainThreat ? `Live RH at ${liveRH?.toFixed(0)}%, dew spread ${liveDewSpread?.toFixed(1)}°C — atmosphere saturated. Predicted ${rainMm.toFixed(1)} mm.` : liveWeather ? `Live RH ${liveRH?.toFixed(0)}%, dew spread ${liveDewSpread?.toFixed(1)}°C — stable conditions. No rain expected.` : 'Awaiting live reading...'}
          </p>
        </div>
      </div>
    </div>
  );
};

const LiveStat: React.FC<{ icon: React.ReactNode; label: string; value: string; sub: string; loading: boolean }> = ({ icon, label, value, sub, loading }) => (
  <div className="bg-[#020617] p-2.5 rounded-xl border border-slate-800 relative">
    {loading && <div className="absolute top-1 right-1"><div className="w-1.5 h-1.5 rounded-full bg-sky-400 animate-pulse" /></div>}
    <div className="flex items-center justify-between text-slate-400 text-[11px] mb-0.5"><span>{label}</span>{icon}</div>
    <div className="text-base font-bold font-mono text-white">{value}</div>
    <div className="text-[9px] text-slate-500 mt-0.5 truncate">{sub}</div>
  </div>
);
