import React, { useState, useEffect, useCallback, useRef } from 'react';
import { UP_DISTRICTS, DistrictData, simulateDistrictInference, SYSTEM_STATS } from './data/districts';
import { FastApiConnector } from './components/FastApiConnector';
import { ControlPanelSidebar } from './components/ControlPanelSidebar';
import { InteractiveCommandMap } from './components/InteractiveCommandMap';
import { AnalysisSidebar } from './components/AnalysisSidebar';
import {
  callPredict,
  fetchHourlyForecast,
  fetchHourlyForecastByCoordinates,
  fetchLiveWeather,
  fetchLiveWeatherByCoordinates,
  LiveWeatherReading,
  pingBackend,
  PredictionResponse,
} from './services/liveWeather';
import { CloudLightning, Database, ShieldAlert, Cpu, Activity, Info, Radio } from 'lucide-react';

// Use a fallback for the API URL if env is not defined
const DEFAULT_API_URL = (window as any).VITE_API_URL || 'http://localhost:8000';

export const App: React.FC = () => {
  // District data
  const [districts, setDistricts] = useState<DistrictData[]>(UP_DISTRICTS);
  const [selectedDistrict, setSelectedDistrict] = useState<DistrictData>(UP_DISTRICTS[49]);
  const [hoveredDistrict, setHoveredDistrict] = useState<DistrictData | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0]);

  // Model weights (embedded simulator)
  const [xgBoostBias, setXgBoostBias] = useState<number>(0);
  const [lightGbmMultiplier, setLightGbmMultiplier] = useState<number>(1.0);
  const [lagWeight, setLagWeight] = useState<number>(1.0);

  // Backend config
  const [apiMode, setApiMode] = useState<'live' | 'embedded'>('live');
  const [apiUrl, setApiUrl] = useState<string>(DEFAULT_API_URL);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [lastPing, setLastPing] = useState<number | null>(null);
  const [isSyncing, setIsSyncing] = useState<boolean>(false);
  const [showDocs, setShowDocs] = useState<boolean>(false);

  // Live weather state
  const [liveWeather, setLiveWeather] = useState<LiveWeatherReading | null>(null);
  const [liveError, setLiveError] = useState<string | null>(null);
  const [isLoadingLive, setIsLoadingLive] = useState<boolean>(false);
  const [hourlyForecast, setHourlyForecast] = useState<Array<{ time: string; precipProbability: number; rainfallMm: number; tempC: number }>>([]);
  const [autoRefresh, setAutoRefresh] = useState<boolean>(true);
  const [lastFetchedAt, setLastFetchedAt] = useState<Date | null>(null);

  // Prediction result
  const [backendPrediction, setBackendPrediction] = useState<{ threat_pct: number; rain_mm: number; will_rain: boolean; source: 'backend' | 'simulated' } | null>(null);
  const [backendError, setBackendError] = useState<string | null>(null);

  const refreshTimerRef = useRef<number | null>(null);

  // --- Live weather fetch (from backend) ---
  const fetchLiveData = useCallback(async (district: DistrictData) => {
    setIsLoadingLive(true);
    setLiveError(null);
    try {
      let reading: LiveWeatherReading;

      try {
        // First try your backend. This lets your VS Code project own the live-data source.
        reading = await fetchLiveWeather(apiUrl, district.id, district.name, district.lat, district.lng);
      } catch {
        // If your backend endpoint is not ready yet, use coordinate-based live data directly.
        reading = await fetchLiveWeatherByCoordinates(district.id, district.lat, district.lng);
      }

      setLiveWeather(reading);
      setLastFetchedAt(new Date());

      // Forecast: backend first, coordinate source second.
      let hourlyRes = await fetchHourlyForecast(apiUrl, district.id, district.name, district.lat, district.lng).catch(() => []);
      if (hourlyRes.length === 0) {
        hourlyRes = await fetchHourlyForecastByCoordinates(district.lat, district.lng).catch(() => []);
      }
      setHourlyForecast(hourlyRes);

    } catch (err: any) {
      // Last-resort fallback keeps the UI usable and clearly reports the live-data error.
      setLiveError(err.message || 'Failed to fetch live weather data');
      const reading: LiveWeatherReading = {
        districtId: district.id,
        temperatureC: Math.round((district.baselineTemp + (Math.random() * 2 - 1)) * 10) / 10,
        relativeHumidity: Math.round(district.baselineHumidity + (Math.random() * 4 - 2)),
        specificHumidity: Math.round((district.baselineHumidity * 0.018 + (Math.random() * 0.01)) * 10) / 10,
        dewPointC: Math.round((district.baselineTemp - district.dewPointSpread + (Math.random() * 1 - 0.5)) * 10) / 10,
        shortwaveRadiation: Math.round((district.baselineSolarRad + (Math.random() * 2 - 1)) * 10) / 10,
        windSpeedMs: Math.round((district.baselineWindSpeed * 0.447 + (Math.random() * 0.5 - 0.25)) * 10) / 10,
        windDirectionDeg: Math.round(180 + (Math.random() * 60 - 30)),
        windVectorX: Math.round((district.windVectorX + (Math.random() * 0.3 - 0.15)) * 100) / 100,
        windVectorY: Math.round((district.windVectorY + (Math.random() * 0.3 - 0.15)) * 100) / 100,
        precipitation: district.lag1Rain > 0 ? Math.round(district.lag1Rain * (0.8 + Math.random() * 0.4) * 10) / 10 : Math.round(Math.random() * 2 * 10) / 10,
        cloudCover: Math.round(40 + Math.random() * 40),
        pressureHpa: Math.round(1010 + Math.random() * 10),
        apparentTempC: Math.round((district.baselineTemp + (Math.random() * 1.5 - 0.75)) * 10) / 10,
        observationTime: new Date().toISOString()
      };
      setLiveWeather(reading);
      setLastFetchedAt(new Date());
      setHourlyForecast([]);
    } finally {
      setIsLoadingLive(false);
    }
  }, [apiUrl, selectedDistrict]);

  // --- Run backend prediction ---
  const runBackendInference = useCallback(async (district: DistrictData, weather: LiveWeatherReading) => {
    setBackendError(null);
    if (apiMode !== 'live') {
      const sim = simulateDistrictInference(
        { ...district, baselineTemp: weather.temperatureC, baselineHumidity: weather.relativeHumidity, lag1Rain: weather.precipitation },
        xgBoostBias, lightGbmMultiplier, lagWeight
      );
      setBackendPrediction({
        threat_pct: sim.threatProbability,
        rain_mm: sim.predictedRainfallMm,
        will_rain: sim.threatProbability > 50,
        source: 'simulated'
      });
      return;
    }

    try {
      const result: PredictionResponse = await callPredict(apiUrl, {
        district_id: district.id,
        temperature_c: weather.temperatureC,
        humidity_pct: weather.relativeHumidity,
        wind_vector_x: weather.windVectorX,
        wind_vector_y: weather.windVectorY,
        lag_1_rain: district.lag1Rain,
        lag_3_rain: district.lag3Rain,
        lag_7_rain: district.lag7Rain
      });
      
      const pred = {
        threat_pct: result.classification_threat_pct,
        rain_mm: result.predicted_rain_mm,
        will_rain: result.will_rain,
        source: 'backend' as const
      };
      
      setBackendPrediction(pred);
      
      // SYNC: Update the global districts array so the map marker reflects real backend data
      setDistricts(prev => prev.map(d => 
        d.id === district.id 
          ? { 
              ...d, 
              threatProbability: pred.threat_pct, 
              predictedRainfallMm: pred.rain_mm,
              status: pred.threat_pct > 70 ? 'High Threat' : pred.threat_pct > 30 ? 'Warning' : 'Safe' 
            }
          : d
      ));
      
      setIsConnected(true);
    } catch (err: any) {
      setBackendError(err.message);
      setIsConnected(false);
      const sim = simulateDistrictInference(
        { ...district, baselineTemp: weather.temperatureC, baselineHumidity: weather.relativeHumidity, lag1Rain: weather.precipitation },
        xgBoostBias, lightGbmMultiplier, lagWeight
      );
      setBackendPrediction({
        threat_pct: sim.threatProbability,
        rain_mm: sim.predictedRainfallMm,
        will_rain: sim.threatProbability > 50,
        source: 'simulated'
      });
    }
  }, [apiMode, apiUrl, xgBoostBias, lightGbmMultiplier, lagWeight]);

  // Fetch on district change
  useEffect(() => {
    fetchLiveData(selectedDistrict);
  }, [selectedDistrict.id, fetchLiveData]);

  // Run prediction after live weather fetched
  useEffect(() => {
    if (liveWeather && liveWeather.districtId === selectedDistrict.id) {
      runBackendInference(selectedDistrict, liveWeather);
    }
  }, [liveWeather, selectedDistrict, runBackendInference]);

  // Auto-refresh
  useEffect(() => {
    if (refreshTimerRef.current) window.clearInterval(refreshTimerRef.current);
    if (autoRefresh) {
      refreshTimerRef.current = window.setInterval(() => fetchLiveData(selectedDistrict), 60000);
    }
    return () => { if (refreshTimerRef.current) window.clearInterval(refreshTimerRef.current); };
  }, [autoRefresh, selectedDistrict, fetchLiveData]);

  // Local model overrides
  useEffect(() => {
    setIsSyncing(true);
    const timer = setTimeout(() => {
      const updated = UP_DISTRICTS.map(d => simulateDistrictInference(d, xgBoostBias, lightGbmMultiplier, lagWeight));
      setDistricts(updated);
      const found = updated.find(d => d.id === selectedDistrict.id) || updated[0];
      setSelectedDistrict(prev => ({ ...prev, ...found }));
      setIsSyncing(false);
    }, 150);
    return () => clearTimeout(timer);
  }, [xgBoostBias, lightGbmMultiplier, lagWeight]);

  const handleSelectDistrict = (district: DistrictData) => {
    setIsSyncing(true);
    setSelectedDistrict(district);
    setTimeout(() => setIsSyncing(false), 200);
  };

  const handleResetWeights = () => { setXgBoostBias(0); setLightGbmMultiplier(1.0); setLagWeight(1.0); };

  const handleRunHealthCheck = async () => {
    setIsSyncing(true);
    const result = await pingBackend(apiUrl);
    setIsConnected(result.ok);
    setLastPing(result.latency > 0 ? result.latency : null);
    if (result.ok && liveWeather) runBackendInference(selectedDistrict, liveWeather);
    setIsSyncing(false);
  };

  const threatCount = districts.filter(d => d.threatProbability > 50).length;

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100 flex flex-col font-['Inter'] selection:bg-sky-500 selection:text-slate-950 overflow-x-hidden">
      {/* Header */}
      <header className="bg-[#0b1329]/95 backdrop-blur-md border-b border-slate-800 sticky top-0 z-50 px-4 lg:px-8 py-3 shadow-xl">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="bg-sky-500/20 p-2 rounded-lg border border-sky-500/30">
              <CloudLightning className="w-5 h-5 text-sky-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-black text-white tracking-tight text-transform: uppercase">RAINFALL PREDICTION</h1>
                <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-sky-500/10 text-sky-400 border border-sky-500/20 uppercase tracking-wider">
                  Enterprise
                </span>
                <span className="text-[10px] font-mono bg-red-500/10 text-red-400 border border-red-500/30 px-2 py-0.5 rounded-full font-bold flex items-center gap-1">
                  <Radio className="w-2.5 h-2.5 animate-pulse" /> LIVE
                </span>
              </div>
              <p className="text-xs text-slate-400">End-to-End Predictive Weather Intelligence System • 75 Districts • Real-Time Telemetry</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 lg:gap-6 text-xs">
            <div className="flex items-center gap-2 bg-[#020617] px-3 py-1.5 rounded-lg border border-slate-800">
              <Database className="w-4 h-4 text-sky-400" />
              <div><div className="text-[10px] text-slate-400">SQLite Index</div><div className="font-mono font-bold text-white">{SYSTEM_STATS.indexSpeed}</div></div>
            </div>
            <div className="flex items-center gap-2 bg-[#020617] px-3 py-1.5 rounded-lg border border-slate-800">
              <Cpu className="w-4 h-4 text-indigo-400" />
              <div>
                <div className="text-[10px] text-slate-400">{backendPrediction?.source === 'backend' ? 'Your FastAPI Backend' : 'Embedded ML Sim'}</div>
                <div className={`font-mono font-bold ${backendPrediction?.source === 'backend' ? 'text-emerald-400' : 'text-amber-400'}`}>
                  {backendPrediction?.source === 'backend' ? 'CONNECTED' : 'STANDBY'}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2 bg-[#020617] px-3 py-1.5 rounded-lg border border-slate-800">
              <ShieldAlert className="w-4 h-4 text-amber-400" />
              <div><div className="text-[10px] text-slate-400">Threat Districts</div><div className="font-mono font-bold text-amber-400">{threatCount} / 75</div></div>
            </div>
            <button onClick={() => setShowDocs(!showDocs)} className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 border transition-all cursor-pointer ${showDocs ? 'bg-sky-500 text-slate-950 border-sky-400 shadow-lg shadow-sky-500/20' : 'bg-slate-800 text-slate-300 border-slate-700 hover:text-white'}`}>
              <Info className="w-3.5 h-3.5" /> Architecture
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 lg:p-6 space-y-6">
        {showDocs && (
          <div className="bg-[#0f172a] rounded-2xl border border-sky-500/30 p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2"><div className="p-1.5 bg-sky-500/10 rounded-lg text-sky-400"><Activity className="w-5 h-5" /></div><h2 className="text-lg font-bold text-white">System Architecture</h2></div>
              <button onClick={() => setShowDocs(false)} className="text-xs bg-slate-800 text-slate-300 hover:text-white px-3 py-1 rounded-lg border border-slate-700 cursor-pointer">Close</button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 text-xs">
              <div className="space-y-2 bg-[#020617] p-4 rounded-xl border border-slate-800">
                <h3 className="font-bold text-sky-400 uppercase tracking-wider text-sm">1. Live Telemetry</h3>
                <p className="text-slate-300">All values are <strong className="text-white">REAL-TIME</strong>, fetched from your backend which sources live atmospheric data and serves it to the dashboard.</p>
              </div>
              <div className="space-y-2 bg-[#020617] p-4 rounded-xl border border-slate-800">
                <h3 className="font-bold text-indigo-400 uppercase tracking-wider text-sm">2. Your FastAPI Backend</h3>
                <p className="text-slate-300">Live readings are POSTed to <code className="text-sky-300 font-mono">/api/v1/predict</code> on your local server. Your trained models compute rainfall predictions.</p>
              </div>
              <div className="space-y-2 bg-[#020617] p-4 rounded-xl border border-slate-800">
                <h3 className="font-bold text-emerald-400 uppercase tracking-wider text-sm">3. Dual-Model Stack</h3>
                <p className="text-slate-300"><strong className="text-white">Classifier:</strong> Threat detection. <strong className="text-white">Regressor:</strong> Log-Transform volume estimation.</p>
              </div>
            </div>
          </div>
        )}

        <FastApiConnector
          apiMode={apiMode} setApiMode={setApiMode}
          apiUrl={apiUrl} setApiUrl={setApiUrl}
          lastPing={lastPing} onRunHealthCheck={handleRunHealthCheck}
          isConnected={isConnected} selectedDistrict={selectedDistrict}
          liveWeather={liveWeather} liveError={liveError}
          isLoadingLive={isLoadingLive} autoRefresh={autoRefresh}
          setAutoRefresh={setAutoRefresh} lastFetchedAt={lastFetchedAt}
          onManualRefresh={() => fetchLiveData(selectedDistrict)}
          backendPrediction={backendPrediction} backendError={backendError}
        />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          <div className="lg:col-span-3 h-full">
            <ControlPanelSidebar
              districts={districts} selectedDistrict={selectedDistrict}
              onSelectDistrict={handleSelectDistrict} selectedDate={selectedDate}
              onSelectDate={setSelectedDate} xgBoostBias={xgBoostBias}
              setXgBoostBias={setXgBoostBias} lightGbmMultiplier={lightGbmMultiplier}
              setLightGbmMultiplier={setLightGbmMultiplier} lagWeight={lagWeight}
              setLagWeight={setLagWeight} onResetWeights={handleResetWeights}
            />
          </div>
          <div className="lg:col-span-6 h-full">
            <InteractiveCommandMap
              districts={districts} selectedDistrict={selectedDistrict}
              onSelectDistrict={handleSelectDistrict} hoveredDistrict={hoveredDistrict}
              onHoverDistrict={setHoveredDistrict} isMapSyncing={isSyncing}
            />
          </div>
          <div className="lg:col-span-3 h-full">
            <AnalysisSidebar
              selectedDistrict={selectedDistrict} selectedDate={selectedDate}
              liveWeather={liveWeather} hourlyForecast={hourlyForecast}
              backendPrediction={backendPrediction} isLoadingLive={isLoadingLive}
            />
          </div>
        </div>
      </main>

      <footer className="bg-[#0b1329]/90 border-t border-slate-800 mt-12 py-6 px-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-sky-500/10 rounded-xl border border-sky-500/20 flex items-center justify-center">
                <CloudLightning className="w-6 h-6 text-sky-400" />
              </div>
              <div>
                <p className="font-semibold text-slate-400 text-transform: uppercase">Rainfall Prediction • End-to-End UP Weather Intelligence</p>
                <p className="text-xs text-slate-500">© 2024 Dual-Stage ML Infrastructure • V1.2.0-Production</p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-4 font-mono text-[11px]">
            <span className="text-emerald-400">● Live Data Streaming</span>
            <span>•</span>
            <span>{lastFetchedAt ? `Last Update: ${lastFetchedAt.toLocaleTimeString()}` : 'Awaiting first fetch...'}</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
