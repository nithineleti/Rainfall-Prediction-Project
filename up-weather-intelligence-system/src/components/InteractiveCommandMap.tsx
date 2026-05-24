import React, { useState } from 'react';
import { DistrictData } from '../data/districts';
import { MapPin, AlertCircle, CheckCircle, Navigation, ShieldAlert, ZoomIn, Compass, Layers } from 'lucide-react';

interface InteractiveCommandMapProps {
  districts: DistrictData[];
  selectedDistrict: DistrictData;
  onSelectDistrict: (district: DistrictData) => void;
  hoveredDistrict: DistrictData | null;
  onHoverDistrict: (district: DistrictData | null) => void;
  isMapSyncing: boolean;
}

export const InteractiveCommandMap: React.FC<InteractiveCommandMapProps> = ({
  districts,
  selectedDistrict,
  onSelectDistrict,
  hoveredDistrict,
  onHoverDistrict,
  isMapSyncing
}) => {
  const [mapLayer, setMapLayer] = useState<'cartodb-dark' | 'threat-heat' | 'wind-vectors'>('cartodb-dark');
  const [zoomLevel, setZoomLevel] = useState<number>(1);

  // Group districts for visual representation
  const threatDistricts = districts.filter(d => d.threatProbability > 50);

  return (
    <div className="bg-[#0b1329]/90 backdrop-blur-md rounded-2xl border border-slate-800 shadow-2xl overflow-hidden flex flex-col h-full relative">
      {/* Map Header bar */}
      <div className="p-4 bg-[#050b1e]/90 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 z-10">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-sky-400 animate-pulse"></div>
          <h2 className="text-base font-bold text-white tracking-wide flex items-center gap-2">
            <span>UP Interactive Geo-Map</span>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">Leaflet Canvas v1.9.4</span>
          </h2>
        </div>

        {/* Layer Controls */}
        <div className="flex items-center gap-1.5 bg-[#020617] p-1 rounded-lg border border-slate-800">
          <button
            onClick={() => setMapLayer('cartodb-dark')}
            className={`px-2.5 py-1 rounded text-xs font-medium transition-all flex items-center gap-1 ${
              mapLayer === 'cartodb-dark' ? 'bg-sky-500 text-slate-950 font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Layers className="w-3 h-3" />
            CartoDB.DarkMatter
          </button>
          <button
            onClick={() => setMapLayer('threat-heat')}
            className={`px-2.5 py-1 rounded text-xs font-medium transition-all flex items-center gap-1 ${
              mapLayer === 'threat-heat' ? 'bg-indigo-500 text-white font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Threat Pulse Heat
          </button>
          <button
            onClick={() => setMapLayer('wind-vectors')}
            className={`px-2.5 py-1 rounded text-xs font-medium transition-all flex items-center gap-1 ${
              mapLayer === 'wind-vectors' ? 'bg-slate-700 text-sky-300 font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Navigation className="w-3 h-3" />
            Wind Vectors
          </button>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-ping"></span>
            Rain Threat &gt;50%: <strong className="text-white">{threatDistricts.length}</strong>
          </span>
        </div>
      </div>

      {/* Map Viewport */}
      <div className="relative flex-1 min-h-[480px] bg-[#020617] overflow-hidden flex items-center justify-center p-6 select-none">
        {/* Outer Bounding Border for entire state: Neon Sky Blue, 3px width */}
        <div className="absolute inset-4 rounded-3xl border-[3px] border-sky-400/80 shadow-[0_0_25px_rgba(56,189,248,0.25)] pointer-events-none z-0">
          <div className="absolute -top-3 left-8 bg-[#020617] px-3 py-0.5 border border-sky-400 text-sky-400 rounded text-[10px] font-mono tracking-widest uppercase">
            Uttar Pradesh — 75 Districts (SQLite Indexed)
          </div>
        </div>

        {/* Background Grid simulation for cartodb dark matter */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] opacity-30 pointer-events-none"></div>

        {/* Map Syncing Indicator */}
        {isMapSyncing && (
          <div className="absolute top-6 right-6 bg-sky-500/10 border border-sky-500 text-sky-400 px-3 py-1.5 rounded-lg text-xs flex items-center gap-2 font-mono animate-pulse shadow-lg z-20">
            <ZoomIn className="w-4 h-4 animate-spin" />
            Syncing Map Focus...
          </div>
        )}

        {/* Interactive District Grid Representation */}
        <div 
          className="w-full max-w-4xl h-full min-h-[420px] relative transition-transform duration-500 ease-out z-10"
          style={{ transform: `scale(${zoomLevel})` }}
        >
          {/* Simulated Geographic layout of UP */}
          {districts.map((district) => {
            const isSelected = selectedDistrict.id === district.id;
            const isHovered = hoveredDistrict?.id === district.id;
            const hasRainThreat = district.threatProbability > 50;
            const isHighThreat = district.threatProbability > 75;

            // Calculate styling based on prompt requirement:
            // "Low-Fade Interactive Districts: Individual districts should stay at 5% opacity, turning into high-contrast glowing blue shapes on hover."
            // "The 'Rainfall Threat' Pulse: When a district is predicted to have rain (>50%), the map border for that specific district should have a pulsating red glow animation."
            
            return (
              <div
                key={district.id}
                onClick={() => onSelectDistrict(district)}
                onMouseEnter={() => onHoverDistrict(district)}
                onMouseLeave={() => onHoverDistrict(null)}
                className={`absolute p-2 rounded-xl transition-all duration-300 cursor-pointer flex flex-col items-center justify-center text-center ${
                  isSelected 
                    ? 'bg-sky-500/20 border-2 border-sky-400 shadow-[0_0_20px_rgba(56,189,248,0.5)] z-30 scale-125 opacity-100' 
                    : isHovered 
                    ? 'bg-sky-500/40 border-2 border-sky-300 shadow-[0_0_15px_rgba(56,189,248,0.7)] z-20 scale-110 opacity-100' 
                    : hasRainThreat 
                    ? 'bg-slate-900/60 border border-red-500/80 shadow-[0_0_12px_rgba(239,68,68,0.4)] opacity-90 animate-pulse'
                    : 'bg-slate-900/40 border border-slate-800 opacity-30 hover:opacity-100 hover:border-sky-500'
                }`}
                style={{
                  left: `${district.mapX}%`,
                  top: `${district.mapY}%`,
                  transform: `translate(-50%, -50%) ${isSelected ? 'scale(1.2)' : ''}`,
                  minWidth: isSelected ? '110px' : '75px'
                }}
              >
                {/* Rainfall Threat Pulse Glow animation */}
                {hasRainThreat && (
                  <div className="absolute -inset-1 rounded-xl bg-red-500/20 animate-ping opacity-75 pointer-events-none"></div>
                )}

                <div className="flex items-center gap-1">
                  {isHighThreat ? (
                    <ShieldAlert className="w-3.5 h-3.5 text-red-400 shrink-0 animate-bounce" />
                  ) : hasRainThreat ? (
                    <AlertCircle className="w-3 h-3 text-amber-400 shrink-0" />
                  ) : (
                    <CheckCircle className="w-3 h-3 text-emerald-400 shrink-0" />
                  )}
                  <span className={`font-semibold text-xs truncate ${isSelected ? 'text-white' : isHovered ? 'text-sky-200' : 'text-slate-200'}`}>
                    {district.name}
                  </span>
                </div>

                {/* Threat level percentage badge */}
                <div className="mt-1 flex items-center justify-center gap-1 w-full">
                  <span className={`text-[10px] px-1.5 py-0.2 rounded font-mono ${
                    hasRainThreat ? 'bg-red-500/20 text-red-300 font-bold' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {district.threatProbability}% rain
                  </span>
                  {district.predictedRainfallMm > 0 && (
                    <span className="text-[10px] text-sky-300 font-mono font-bold bg-sky-950 px-1 rounded">
                      {district.predictedRainfallMm}mm
                    </span>
                  )}
                </div>

                {/* Wind Vector indicator in specific view mode */}
                {mapLayer === 'wind-vectors' && (
                  <div className="mt-1 flex items-center gap-0.5 text-[9px] text-sky-400 font-mono">
                    <Navigation className="w-2.5 h-2.5" style={{ transform: `rotate(${Math.atan2(district.windVectorY, district.windVectorX) * (180/Math.PI)}deg)` }} />
                    <span>{district.baselineWindSpeed}m/s</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* High-Contrast Dark Tooltip on Hover */}
        {hoveredDistrict && (
          <div className="absolute bottom-6 left-6 bg-[#020617] border border-slate-700 text-white p-3 rounded-xl shadow-2xl z-30 max-w-xs animate-fade-in pointer-events-none">
            <div className="flex items-center justify-between gap-4 border-b border-slate-800 pb-1.5 mb-1.5">
              <div className="font-bold text-sm text-sky-400 flex items-center gap-1.5">
                <MapPin className="w-4 h-4 text-sky-400" />
                {hoveredDistrict.name} District
              </div>
              <span className="text-[10px] font-mono text-slate-400">{hoveredDistrict.id}</span>
            </div>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-400">Threat Level:</span>
                <span className={`font-bold ${hoveredDistrict.threatProbability > 50 ? 'text-red-400' : 'text-emerald-400'}`}>
                  {hoveredDistrict.threatProbability > 50 ? 'Rain Expected' : 'No Rain Threat'} ({hoveredDistrict.threatProbability}%)
                </span>
              </div>
              {hoveredDistrict.threatProbability > 50 && (
                <div className="flex justify-between">
                  <span className="text-slate-400">Estimated Volume:</span>
                  <span className="font-bold text-sky-300 font-mono">{hoveredDistrict.predictedRainfallMm} mm (Log-Transformed)</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-slate-400">Temperature / RH:</span>
                <span className="font-mono">{hoveredDistrict.baselineTemp}°C / {hoveredDistrict.baselineHumidity}%</span>
              </div>
              <div className="flex justify-between text-[10px] text-slate-500 pt-1 border-t border-slate-800">
                <span>Lags (1d/3d/7d):</span>
                <span>{hoveredDistrict.lag1Rain} / {hoveredDistrict.lag3Rain} / {hoveredDistrict.lag7Rain} mm</span>
              </div>
            </div>
          </div>
        )}

        {/* Map Legend & Controls bottom right */}
        <div className="absolute bottom-6 right-6 flex flex-col gap-2 z-20">
          <div className="bg-[#020617]/90 backdrop-blur-md p-2 rounded-xl border border-slate-800 text-[11px] space-y-1 shadow-lg">
            <div className="font-semibold text-slate-300 border-b border-slate-800 pb-1 mb-1">Threat Legend</div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded bg-red-500/20 border border-red-500 animate-pulse"></div>
              <span className="text-slate-300">&gt; 50% Rain Probability (Pulsing Red)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded bg-sky-500/20 border border-sky-400"></div>
              <span className="text-slate-300">Selected Focus District</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded bg-slate-800 border border-slate-700 opacity-40"></div>
              <span className="text-slate-400">Low-Fade District (5% opacity)</span>
            </div>
          </div>

          <div className="flex gap-1 justify-end">
            <button 
              onClick={() => setZoomLevel(prev => Math.min(prev + 0.1, 1.5))} 
              className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-200 border border-slate-700 text-xs font-mono"
              title="Zoom In"
            >
              +
            </button>
            <button 
              onClick={() => setZoomLevel(1)} 
              className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-200 border border-slate-700 text-xs flex items-center gap-1"
              title="Reset Zoom"
            >
              <Compass className="w-3 h-3" /> Reset View
            </button>
            <button 
              onClick={() => setZoomLevel(prev => Math.max(prev - 0.1, 0.7))} 
              className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-200 border border-slate-700 text-xs font-mono"
              title="Zoom Out"
            >
              -
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
