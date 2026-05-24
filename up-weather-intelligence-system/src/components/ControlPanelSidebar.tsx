import React, { useState } from 'react';
import { DistrictData } from '../data/districts';
import { Calendar, Search, Sliders, Cpu, Gauge, RefreshCw, Filter, Sparkles, Database } from 'lucide-react';

interface ControlPanelSidebarProps {
  districts: DistrictData[];
  selectedDistrict: DistrictData;
  onSelectDistrict: (district: DistrictData) => void;
  selectedDate: string;
  onSelectDate: (date: string) => void;
  xgBoostBias: number;
  setXgBoostBias: (val: number) => void;
  lightGbmMultiplier: number;
  setLightGbmMultiplier: (val: number) => void;
  lagWeight: number;
  setLagWeight: (val: number) => void;
  onResetWeights: () => void;
}

export const ControlPanelSidebar: React.FC<ControlPanelSidebarProps> = ({
  districts,
  selectedDistrict,
  onSelectDistrict,
  selectedDate,
  onSelectDate,
  xgBoostBias,
  setXgBoostBias,
  lightGbmMultiplier,
  setLightGbmMultiplier,
  lagWeight,
  setLagWeight,
  onResetWeights
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [regionFilter, setRegionFilter] = useState<string>('All');

  const regions = ['All', 'Western UP', 'Central UP', 'Eastern UP', 'Bundelkhand'];

  const filteredDistricts = districts.filter(d => {
    const matchesSearch = d.name.toLowerCase().includes(searchQuery.toLowerCase()) || d.id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRegion = regionFilter === 'All' || d.region === regionFilter;
    return matchesSearch && matchesRegion;
  });

  return (
    <div className="bg-[#0b1329]/90 backdrop-blur-md rounded-2xl border border-slate-800 p-5 shadow-2xl flex flex-col h-full space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-sky-500 to-indigo-600 rounded-xl shadow-lg shadow-sky-500/20 text-slate-950 font-black tracking-tighter">
            UP
          </div>
          <div>
            <h1 className="text-base font-bold text-white tracking-tight">Control Panel</h1>
            <p className="text-xs text-slate-400">75 Districts &amp; Temporal Lags</p>
          </div>
        </div>
        <span className="text-[10px] font-mono bg-sky-500/10 text-sky-400 px-2 py-1 rounded border border-sky-500/20">
          FastAPI Engine
        </span>
      </div>

      {/* Floating Label Date Picker */}
      <div className="space-y-1.5">
        <label className="text-xs font-semibold text-slate-300 flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-sky-400" /> Target Inference Date
          </span>
          <span className="text-[10px] text-slate-500 font-mono">Live Data</span>
        </label>
        <div className="relative group">
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => onSelectDate(e.target.value)}
            className="w-full bg-[#020617] border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-sky-500 transition-colors font-medium shadow-inner"
          />
        </div>
      </div>

      {/* District Selector & Search */}
      <div className="space-y-2 flex-1 flex flex-col min-h-[250px]">
        <label className="text-xs font-semibold text-slate-300 flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <Search className="w-3.5 h-3.5 text-sky-400" /> District Selection Form
          </span>
          <span className="text-[10px] text-sky-400 font-mono">Map Sync Active</span>
        </label>

        {/* Region filter pills */}
        <div className="flex flex-wrap gap-1.5 pt-1">
          {regions.map(r => (
            <button
              key={r}
              onClick={() => setRegionFilter(r)}
              className={`px-2 py-1 rounded text-[11px] font-medium transition-colors ${
                regionFilter === r 
                  ? 'bg-sky-500 text-slate-950 font-bold' 
                  : 'bg-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              {r}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div className="relative mt-2">
          <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Filter className="h-3.5 w-3.5 text-slate-500" />
          </span>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by district name or UP code..."
            className="w-full bg-[#020617] pl-9 pr-3 py-2 border border-slate-700 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500"
          />
          {searchQuery && (
            <button 
              onClick={() => setSearchQuery('')}
              className="absolute inset-y-0 right-0 pr-3 flex items-center text-xs text-slate-500 hover:text-white cursor-pointer"
            >
              Clear
            </button>
          )}
        </div>

        {/* District list container */}
        <div className="mt-2 flex-1 overflow-y-auto pr-1 space-y-1.5 max-h-[220px] custom-scrollbar border border-slate-800 rounded-lg p-1 bg-[#020617]/50">
          {filteredDistricts.length === 0 ? (
            <div className="p-4 text-center text-slate-500 text-xs">No districts matching filter criteria.</div>
          ) : (
            filteredDistricts.map(district => {
              const isSelected = district.id === selectedDistrict.id;
              const hasRain = district.threatProbability > 50;
              return (
                <div
                  key={district.id}
                  onClick={() => onSelectDistrict(district)}
                  className={`p-2.5 rounded-lg text-xs cursor-pointer flex items-center justify-between transition-all ${
                    isSelected
                      ? 'bg-gradient-to-r from-sky-500/20 to-indigo-500/20 border border-sky-400/80 text-white font-bold shadow-md shadow-sky-500/10'
                      : 'bg-[#020617] border border-slate-800/80 text-slate-300 hover:border-slate-700 hover:bg-slate-900'
                  }`}
                >
                  <div className="flex items-center gap-2 truncate">
                    <span className="font-mono text-[10px] text-slate-500 bg-slate-800 px-1.5 py-0.5 rounded">{district.id}</span>
                    <span className="truncate">{district.name}</span>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-mono ${
                      hasRain ? 'bg-red-500/20 text-red-400 font-bold' : 'bg-emerald-500/10 text-emerald-400'
                    }`}>
                      {district.threatProbability}%
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>
        <div className="text-[10px] text-slate-500 italic text-right">Clicking a district focuses map &amp; updates pipeline</div>
      </div>

      {/* Model Parameter Override Simulator */}
      <div className="space-y-3 pt-4 border-t border-slate-800">
        <div className="flex items-center justify-between">
          <label className="text-xs font-semibold text-white flex items-center gap-1.5">
            <Sliders className="w-3.5 h-3.5 text-sky-400" /> Feature Pipeline Modifiers
          </label>
          <button 
            onClick={onResetWeights}
            className="text-[10px] text-sky-400 hover:underline flex items-center gap-1 cursor-pointer"
          >
            <RefreshCw className="w-2.5 h-2.5" /> Reset
          </button>
        </div>

        {/* XGBoost bias */}
        <div className="space-y-1 bg-[#020617] p-3 rounded-xl border border-slate-800">
          <div className="flex justify-between text-xs">
            <span className="text-slate-300 flex items-center gap-1">
              <Cpu className="w-3 h-3 text-sky-400" /> XGBoost Threat Bias
            </span>
            <span className="font-mono text-sky-400 font-bold">{xgBoostBias > 0 ? `+${xgBoostBias}` : xgBoostBias}%</span>
          </div>
          <input
            type="range"
            min="-30"
            max="30"
            value={xgBoostBias}
            onChange={(e) => setXgBoostBias(parseFloat(e.target.value))}
            className="w-full accent-sky-400 bg-slate-800 rounded-lg cursor-pointer h-1.5"
          />
          <div className="text-[10px] text-slate-500">Adjust specific humidity &amp; dew point sensitivity</div>
        </div>

        {/* LightGBM Log transform multiplier */}
        <div className="space-y-1 bg-[#020617] p-3 rounded-xl border border-slate-800">
          <div className="flex justify-between text-xs">
            <span className="text-slate-300 flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-indigo-400" /> LightGBM Volume Scale
            </span>
            <span className="font-mono text-indigo-400 font-bold">{lightGbmMultiplier}x</span>
          </div>
          <input
            type="range"
            min="0.5"
            max="2.0"
            step="0.1"
            value={lightGbmMultiplier}
            onChange={(e) => setLightGbmMultiplier(parseFloat(e.target.value))}
            className="w-full accent-indigo-400 bg-slate-800 rounded-lg cursor-pointer h-1.5"
          />
          <div className="text-[10px] text-slate-500">Tweak log-transform outlier handling factor</div>
        </div>

        {/* Lag Weight */}
        <div className="space-y-1 bg-[#020617] p-3 rounded-xl border border-slate-800">
          <div className="flex justify-between text-xs">
            <span className="text-slate-300 flex items-center gap-1">
              <Gauge className="w-3 h-3 text-emerald-400" /> Temporal Lags Weight
            </span>
            <span className="font-mono text-emerald-400 font-bold">{lagWeight}x</span>
          </div>
          <input
            type="range"
            min="0"
            max="3"
            step="0.2"
            value={lagWeight}
            onChange={(e) => setLagWeight(parseFloat(e.target.value))}
            className="w-full accent-emerald-400 bg-slate-800 rounded-lg cursor-pointer h-1.5"
          />
          <div className="text-[10px] text-slate-500">Lags 1d/3d/7d front incoming momentum</div>
        </div>
      </div>

      {/* DB Engine status */}
      <div className="p-3 bg-slate-900/80 rounded-xl border border-slate-800 text-[11px] flex items-center justify-between text-slate-400">
        <span className="flex items-center gap-1.5">
          <Database className="w-3.5 h-3.5 text-sky-400" /> SQLite Index:
        </span>
        <span className="font-mono text-sky-300 font-bold">Sub-ms Lookup Active</span>
      </div>
    </div>
  );
};
