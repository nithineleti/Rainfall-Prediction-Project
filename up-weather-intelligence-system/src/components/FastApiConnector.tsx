import React from 'react';
import { Server, Activity, RefreshCw, Send, Radio, CheckCircle2, AlertTriangle, Wifi, WifiOff, Pause, Play } from 'lucide-react';
import { DistrictData } from '../data/districts';
import { LiveWeatherReading } from '../services/liveWeather';

interface FastApiConnectorProps {
  apiMode: 'live' | 'embedded';
  setApiMode: (mode: 'live' | 'embedded') => void;
  apiUrl: string;
  setApiUrl: (url: string) => void;
  lastPing: number | null;
  onRunHealthCheck: () => void;
  isConnected: boolean;
  selectedDistrict: DistrictData;
  liveWeather: LiveWeatherReading | null;
  liveError: string | null;
  isLoadingLive: boolean;
  autoRefresh: boolean;
  setAutoRefresh: (v: boolean) => void;
  lastFetchedAt: Date | null;
  onManualRefresh: () => void;
  backendPrediction: { threat_pct: number; rain_mm: number; will_rain: boolean; source: 'backend' | 'simulated' } | null;
  backendError: string | null;
}

export const FastApiConnector: React.FC<FastApiConnectorProps> = ({
  apiMode, setApiMode, apiUrl, setApiUrl, lastPing, onRunHealthCheck,
  isConnected, selectedDistrict, liveWeather, liveError, isLoadingLive,
  autoRefresh, setAutoRefresh, lastFetchedAt, onManualRefresh,
  backendPrediction, backendError
}) => {
  return (
    <div className="bg-[#0f172a]/95 backdrop-blur-md rounded-2xl border border-slate-800 p-5 shadow-2xl mb-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-4 pb-4 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-tr from-sky-500 to-indigo-500 rounded-xl text-slate-950 font-black shadow-lg shadow-sky-500/20">
            <Server className="w-6 h-6 text-slate-950" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h2 className="text-lg font-bold text-white tracking-wide">Live Telemetry &amp; Backend Hub</h2>
              {isConnected ? (
                <span className="text-[10px] px-2 py-0.5 rounded font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1">
                  <Wifi className="w-3 h-3" /> Backend ONLINE
                </span>
              ) : (
                <span className="text-[10px] px-2 py-0.5 rounded font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 flex items-center gap-1">
                  <WifiOff className="w-3 h-3" /> Backend OFFLINE
                </span>
              )}
              {liveWeather && (
                <span className="text-[10px] px-2 py-0.5 rounded font-mono font-bold bg-red-500/20 text-red-300 border border-red-500/40 flex items-center gap-1">
                  <Radio className="w-3 h-3 animate-pulse" /> LIVE
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Real-time temperature, RH, dew point, solar radiation → processed by your dual-stage ML pipeline
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 bg-[#020617] p-1.5 rounded-xl border border-slate-800">
          <button onClick={() => setApiMode('embedded')} className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 cursor-pointer ${apiMode === 'embedded' ? 'bg-sky-500 text-slate-950 shadow-lg' : 'text-slate-400 hover:text-white'}`}>
            <Activity className="w-3.5 h-3.5" /> Embedded Sandbox
          </button>
          <button onClick={() => setApiMode('live')} className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 cursor-pointer ${apiMode === 'live' ? 'bg-sky-500 text-slate-950 shadow-lg' : 'text-slate-400 hover:text-white'}`}>
            <Server className="w-3.5 h-3.5" /> Live Backend Mode
          </button>
        </div>
      </div>

      {/* Main Content (Always show Telemetry) */}
      <div className="space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between bg-[#020617] p-4 rounded-xl border border-slate-800 gap-3">
          <div>
            <div className="text-xs font-mono text-slate-400 uppercase tracking-wider flex items-center gap-2">
              Live Stream — {selectedDistrict.name} ({selectedDistrict.id})
              <span className="text-[10px] bg-red-500/20 text-red-400 px-2 py-0.5 rounded font-mono border border-red-500/30 animate-pulse">● REAL-TIME</span>
            </div>
            <h3 className="text-sm font-bold text-white mt-0.5">Lat {selectedDistrict.lat.toFixed(4)}°N, Lng {selectedDistrict.lng.toFixed(4)}°E</h3>
            {lastFetchedAt && <p className="text-[11px] text-emerald-400 mt-1 font-mono">Last fetch: {lastFetchedAt.toLocaleTimeString()} {autoRefresh && '· auto-refresh 60s'}</p>}
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => setAutoRefresh(!autoRefresh)} className={`px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1 cursor-pointer ${autoRefresh ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'bg-slate-800 text-slate-400 border border-slate-700'}`}>
              {autoRefresh ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}{autoRefresh ? 'Auto ON' : 'Paused'}
            </button>
            <button onClick={onManualRefresh} disabled={isLoadingLive} className="px-3 py-1.5 bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold rounded-lg text-xs flex items-center gap-1.5 cursor-pointer shadow-lg shadow-sky-500/20 disabled:opacity-50">
              <RefreshCw className={`w-3.5 h-3.5 ${isLoadingLive ? 'animate-spin' : ''}`} />Fetch Live Now
            </button>
          </div>
        </div>

        {liveError && <div className="p-3 rounded-xl bg-red-950/40 border border-red-500/30 text-red-300 text-xs flex items-center gap-2"><AlertTriangle className="w-4 h-4" />{liveError}</div>}

        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3">
          <LiveCard label="Temperature" value={liveWeather ? `${liveWeather.temperatureC.toFixed(1)} °C` : '—'} sub={liveWeather ? `Feels: ${liveWeather.apparentTempC.toFixed(1)}°C` : 'Waiting...'} color="text-white" loading={isLoadingLive} />
          <LiveCard label="RH (%)" value={liveWeather ? `${liveWeather.relativeHumidity.toFixed(0)} %` : '—'} sub="Relative Humidity" color="text-indigo-400" loading={isLoadingLive} />
          <LiveCard label="Specific Hum." value={liveWeather ? `${liveWeather.specificHumidity} g/kg` : '—'} sub="Derived value" color="text-sky-400" loading={isLoadingLive} />
          <LiveCard label="Dew Point" value={liveWeather ? `${liveWeather.dewPointC.toFixed(1)} °C` : '—'} sub={liveWeather ? `Spread: ${(liveWeather.temperatureC - liveWeather.dewPointC).toFixed(1)}°` : '—'} color="text-purple-400" loading={isLoadingLive} />
          <LiveCard label="Solar Rad" value={liveWeather ? `${liveWeather.shortwaveRadiation.toFixed(0)} W/m²` : '—'} sub="Shortwave" color="text-amber-400" loading={isLoadingLive} />
          <LiveCard label="Wind" value={liveWeather ? `${liveWeather.windSpeedMs.toFixed(1)} m/s` : '—'} sub={liveWeather ? `${liveWeather.windDirectionDeg}° dir` : '—'} color="text-cyan-400" loading={isLoadingLive} />
          <LiveCard label="Cloud Cover" value={liveWeather ? `${liveWeather.cloudCover.toFixed(0)} %` : '—'} sub="Total" color="text-slate-300" loading={isLoadingLive} />
          <LiveCard label="Pressure" value={liveWeather ? `${liveWeather.pressureHpa.toFixed(0)} hPa` : '—'} sub="Surface" color="text-emerald-400" loading={isLoadingLive} />
          <LiveCard label="Precipitation" value={liveWeather ? `${liveWeather.precipitation.toFixed(1)} mm` : '—'} sub="Observed" color="text-blue-400" loading={isLoadingLive} />
          <LiveCard label="Wind (u,v)" value={liveWeather ? `${liveWeather.windVectorX}, ${liveWeather.windVectorY}` : '—'} sub="ML features" color="text-pink-400" loading={isLoadingLive} />
        </div>

        <div className="p-4 bg-slate-900/90 rounded-xl border border-slate-800 space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5"><Send className="w-3.5 h-3.5 text-sky-400" />ML Prediction Pipeline</h4>
              <p className="text-[11px] text-slate-400">Live readings processed by your dual-stage models at <code className="text-sky-300 font-mono">{apiUrl}</code></p>
            </div>
            <div className="flex items-center gap-2">
              <input type="text" value={apiUrl} onChange={(e) => setApiUrl(e.target.value)} placeholder="http://localhost:8000" className="bg-[#020617] border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-sky-400 font-mono w-52 focus:outline-none focus:border-sky-500" />
              <button onClick={onRunHealthCheck} className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-lg text-xs flex items-center gap-1.5 cursor-pointer transition-all shadow-md"><RefreshCw className="w-3 h-3" />Test & Sync</button>
            </div>
          </div>

          {backendPrediction && (
            <div className={`p-3 rounded-lg border font-mono text-xs ${backendPrediction.source === 'backend' ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300' : 'bg-amber-950/30 border-amber-500/30 text-amber-300'}`}>
              <div className="flex items-center justify-between pb-2 border-b border-slate-800 mb-2">
                <div className="flex items-center gap-2 font-bold">
                  {backendPrediction.source === 'backend' ? <CheckCircle2 className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
                  {backendPrediction.source === 'backend' ? '✓ Prediction from YOUR Backend (.pkl models)' : '⚠ Backend offline — simulator fallback'}
                </div>
                {lastPing && <span className="text-[10px] text-slate-400">Latency: {lastPing}ms</span>}
              </div>
              <pre className="text-[11px] leading-relaxed overflow-x-auto">{JSON.stringify({
                district_id: selectedDistrict.id,
                threat_pct: backendPrediction.threat_pct,
                will_rain: backendPrediction.will_rain,
                rain_mm: backendPrediction.rain_mm,
                source: backendPrediction.source,
                inputs: liveWeather ? { temp: liveWeather.temperatureC, humidity: liveWeather.relativeHumidity, lag1: selectedDistrict.lag1Rain, lag3: selectedDistrict.lag3Rain, lag7: selectedDistrict.lag7Rain } : null
              }, null, 2)}</pre>
            </div>
          )}

          {backendError && (
            <div className="p-3 rounded-lg bg-red-950/40 border border-red-500/30 text-red-300 text-xs space-y-1">
              <div className="font-bold">Backend Error: {backendError}</div>
              <div className="text-[11px] text-slate-400">Make sure uvicorn is running and CORS is enabled in app.py.</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const LiveCard: React.FC<{ label: string; value: string; sub: string; color: string; loading: boolean }> = ({ label, value, sub, color, loading }) => (
  <div className="bg-[#020617] p-3 rounded-xl border border-slate-800 relative overflow-hidden">
    {loading && <div className="absolute top-1 right-1"><RefreshCw className="w-2.5 h-2.5 animate-spin text-sky-500" /></div>}
    <div className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider mb-1">{label}</div>
    <div className={`text-lg font-mono font-bold ${color}`}>{value}</div>
    <div className="text-[10px] text-slate-500 mt-1 font-mono truncate">{sub}</div>
  </div>
);
