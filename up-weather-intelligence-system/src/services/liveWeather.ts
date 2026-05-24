// ===========================================================
// Live Weather & Prediction Service
// Connects to YOUR FastAPI backend endpoints
// ===========================================================

export interface LiveWeatherReading {
  districtId: string;
  temperatureC: number;
  relativeHumidity: number;
  specificHumidity: number;
  dewPointC: number;
  shortwaveRadiation: number;
  windSpeedMs: number;
  windDirectionDeg: number;
  windVectorX: number;
  windVectorY: number;
  precipitation: number;
  cloudCover: number;
  pressureHpa: number;
  apparentTempC: number;
  observationTime: string;
}

export interface PredictionResponse {
  district_id: string;
  classification_threat_pct: number;
  will_rain: boolean;
  predicted_rain_mm: number;
  [key: string]: any;
}

const PUBLIC_WEATHER_ENDPOINT = "https://api.open-meteo.com/v1/forecast";

function toQuery(params: Record<string, string | number>) {
  return new URLSearchParams(
    Object.entries(params).reduce<Record<string, string>>((acc, [key, value]) => {
      acc[key] = String(value);
      return acc;
    }, {})
  ).toString();
}

function windVectors(speedMs: number, directionDeg: number) {
  const rad = (directionDeg * Math.PI) / 180;
  return {
    x: Math.round(-speedMs * Math.sin(rad) * 100) / 100,
    y: Math.round(-speedMs * Math.cos(rad) * 100) / 100,
  };
}

function specificHumidityGkg(tempC: number, rh: number, pressureHpa = 1013.25) {
  const saturation = 6.112 * Math.exp((17.67 * tempC) / (tempC + 243.5));
  const vaporPressure = (rh / 100) * saturation;
  const kgKg = (0.622 * vaporPressure) / (pressureHpa - 0.378 * vaporPressure);
  return Math.round(kgKg * 1000 * 10) / 10;
}

function normalizeLiveReading(raw: any, districtId: string): LiveWeatherReading {
  const windSpeed = Number(raw.wind_speed_10m ?? raw.windSpeedMs ?? 0);
  const windDirection = Number(raw.wind_direction_10m ?? raw.windDirectionDeg ?? 0);
  const vectors = windVectors(windSpeed, windDirection);
  const temp = Number(raw.temperature_2m ?? raw.temperatureC ?? 0);
  const rh = Number(raw.relative_humidity_2m ?? raw.relativeHumidity ?? 0);
  const pressure = Number(raw.surface_pressure ?? raw.pressureHpa ?? 1013.25);

  return {
    districtId,
    temperatureC: temp,
    relativeHumidity: rh,
    specificHumidity: specificHumidityGkg(temp, rh, pressure),
    dewPointC: Number(raw.dew_point_2m ?? raw.dewPointC ?? temp - 3),
    shortwaveRadiation: Number(raw.shortwave_radiation ?? raw.shortwaveRadiation ?? 0),
    windSpeedMs: windSpeed,
    windDirectionDeg: windDirection,
    windVectorX: Number(raw.windVectorX ?? vectors.x),
    windVectorY: Number(raw.windVectorY ?? vectors.y),
    precipitation: Number(raw.precipitation ?? 0),
    cloudCover: Number(raw.cloud_cover ?? raw.cloudCover ?? 0),
    pressureHpa: pressure,
    apparentTempC: Number(raw.apparent_temperature ?? raw.apparentTempC ?? temp),
    observationTime: String(raw.time ?? raw.observationTime ?? new Date().toISOString()),
  };
}

/**
 * Fetch live weather reading for a district from your backend.
 * Your backend should expose this endpoint, or you can wire it
 * to any live weather source.
 */
export async function fetchLiveWeather(
  apiBaseUrl: string,
  districtId: string,
  districtName?: string,
  lat?: number,
  lng?: number
): Promise<LiveWeatherReading> {
  const params = new URLSearchParams({ district_id: districtId });
  if (districtName) params.set("district_name", districtName);
  if (lat != null) params.set("lat", String(lat));
  if (lng != null) params.set("lng", String(lng));

  const res = await fetch(`${apiBaseUrl.replace(/\/$/, "")}/api/v1/weather/current?${params.toString()}`);
  if (!res.ok) {
    throw new Error(`Live weather endpoint returned ${res.status}`);
  }
  const data = await res.json();
  return normalizeLiveReading(data, data.districtId ?? data.district_id ?? districtId);
}

/**
 * Fetch live weather directly by coordinates. This makes the dashboard work
 * even before your backend implements /api/v1/weather/current.
 */
export async function fetchLiveWeatherByCoordinates(
  districtId: string,
  lat: number,
  lng: number
): Promise<LiveWeatherReading> {
  const query = toQuery({
    latitude: lat,
    longitude: lng,
    current: "temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation,cloud_cover,surface_pressure,wind_speed_10m,wind_direction_10m,shortwave_radiation",
    wind_speed_unit: "ms",
    timezone: "Asia/Kolkata",
  });
  const res = await fetch(`${PUBLIC_WEATHER_ENDPOINT}?${query}`);
  if (!res.ok) throw new Error(`Coordinate live weather returned ${res.status}`);
  const data = await res.json();
  return normalizeLiveReading(data.current ?? {}, districtId);
}

/**
 * Fetch 24-hour forecast for probability mountain chart.
 */
export async function fetchHourlyForecast(
  apiBaseUrl: string,
  districtId: string,
  districtName?: string,
  lat?: number,
  lng?: number
): Promise<Array<{ time: string; precipProbability: number; rainfallMm: number; tempC: number }>> {
  const params = new URLSearchParams({ district_id: districtId });
  if (districtName) params.set("district_name", districtName);
  if (lat != null) params.set("lat", String(lat));
  if (lng != null) params.set("lng", String(lng));
  const res = await fetch(`${apiBaseUrl.replace(/\/$/, "")}/api/v1/weather/forecast?${params.toString()}`);
  if (!res.ok) return [];
  return res.json();
}

export async function fetchHourlyForecastByCoordinates(
  lat: number,
  lng: number
): Promise<Array<{ time: string; precipProbability: number; rainfallMm: number; tempC: number }>> {
  const query = toQuery({
    latitude: lat,
    longitude: lng,
    hourly: "temperature_2m,precipitation_probability,precipitation",
    forecast_hours: 24,
    timezone: "Asia/Kolkata",
  });
  const res = await fetch(`${PUBLIC_WEATHER_ENDPOINT}?${query}`);
  if (!res.ok) return [];
  const data = await res.json();
  const hourly = data.hourly ?? {};
  const times: string[] = hourly.time ?? [];
  return times.map((time, index) => ({
    time: time.slice(11, 16),
    precipProbability: Number(hourly.precipitation_probability?.[index] ?? 0),
    rainfallMm: Number(hourly.precipitation?.[index] ?? 0),
    tempC: Number(hourly.temperature_2m?.[index] ?? 0),
  }));
}

/**
 * Send prediction request to YOUR backend models.
 * This POSTs to your FastAPI /api/v1/predict endpoint.
 */
export async function callPredict(
  apiBaseUrl: string,
  payload: {
    district_id: string;
    temperature_c: number;
    humidity_pct: number;
    wind_vector_x: number;
    wind_vector_y: number;
    lag_1_rain: number;
    lag_3_rain: number;
    lag_7_rain: number;
  }
): Promise<PredictionResponse> {
  const url = `${apiBaseUrl.replace(/\/$/, "")}/api/v1/predict`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status}: ${text}`);
  }
  return res.json();
}

/**
 * Fetch all districts list from your SQLite database via backend.
 */
export async function fetchDistricts(apiBaseUrl: string): Promise<any[]> {
  const res = await fetch(`${apiBaseUrl}/api/v1/districts`);
  if (!res.ok) return [];
  return res.json();
}

/**
 * Ping backend health check.
 */
export async function pingBackend(apiBaseUrl: string): Promise<{ ok: boolean; latency: number }> {
  const t0 = performance.now();
  try {
    const res = await fetch(`${apiBaseUrl}/`);
    return { ok: res.ok, latency: Math.round(performance.now() - t0) };
  } catch {
    return { ok: false, latency: -1 };
  }
}
