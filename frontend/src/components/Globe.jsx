import React, { useEffect, useRef, useState } from "react";
import GlobeGl from "react-globe.gl";

export function Globe({ className, blockedIps = [] }) {
  const globeEl = useRef();
  const [dimensions, setDimensions] = useState({ width: 350, height: 350 });

  const COUNTRY_COORDS = {
    "US": { lat: 37.0902, lng: -95.7129 },
    "CN": { lat: 35.8617, lng: 104.1954 },
    "RU": { lat: 61.5240, lng: 105.3188 },
    "HK": { lat: 22.3193, lng: 114.1694 },
    "LV": { lat: 56.8796, lng: 24.6032 },
    "IN": { lat: 20.5937, lng: 78.9629 },
    "UK": { lat: 55.3781, lng: -3.4360 },
    "GB": { lat: 55.3781, lng: -3.4360 },
    "DE": { lat: 51.1657, lng: 10.4515 },
    "FR": { lat: 46.2276, lng: 2.2137 },
    "BR": { lat: -14.2350, lng: -51.9253 },
    "NL": { lat: 52.1326, lng: 5.2913 },
    "SG": { lat: 1.3521, lng: 103.8198 },
    "CA": { lat: 56.1304, lng: -106.3468 },
    "AU": { lat: -25.2744, lng: 133.7751 },
    "IR": { lat: 32.4279, lng: 53.6880 },
    "KP": { lat: 40.3399, lng: 127.5101 },
  };

  useEffect(() => {
    // Enable smooth auto-rotation and disable zoom to fit the UI
    if (globeEl.current) {
      globeEl.current.controls().autoRotate = true;
      globeEl.current.controls().autoRotateSpeed = 1.2;
      globeEl.current.controls().enableZoom = false;
    }

    // Ensure it perfectly fits its CSS container
    const onResize = () => {
      const container = document.getElementById("globe-container");
      if (container) {
        setDimensions({
          width: container.offsetWidth,
          height: container.offsetWidth,
        });
      }
    };

    window.addEventListener('resize', onResize);
    onResize();

    return () => window.removeEventListener('resize', onResize);
  }, []);

  // Dynamically map our blocked IPs to physical coordinates
  const pointsData = blockedIps.map(block => {
    // If the country is unknown, spawn it randomly in the ocean. Otherwise, use country coords + jitter
    const coords = COUNTRY_COORDS[block.country] || { lat: (Math.random() * 100) - 50, lng: (Math.random() * 360) - 180 };

    return {
      lat: coords.lat + (Math.random() * 2 - 1),
      lng: coords.lng + (Math.random() * 2 - 1),
      size: block.threat_score > 50 ? 2.5 : 1.5, // Massively increased text size
      color: block.threat_score > 50 ? "#ff0033" : "#00ffff", // Neon Red and Neon Cyan for extreme contrast
      label: block.ip
    };
  });

  // Using daytime high-resolution realistic satellite imagery for the globe
  const earthTexture = "//unpkg.com/three-globe/example/img/earth-blue-marble.jpg";
  const earthTopology = "//unpkg.com/three-globe/example/img/earth-topology.png";

  return (
    <div id="globe-container" className={`flex items-center justify-center w-full max-w-[500px] scale-110 aspect-square mx-auto cursor-grab ${className}`}>
      <GlobeGl
        ref={globeEl}
        width={dimensions.width}
        height={dimensions.height}
        globeImageUrl={earthTexture}
        bumpImageUrl={earthTopology}
        backgroundColor="rgba(0,0,0,0)" // Transparent background to match our UI
        atmosphereColor="#3b82f6" // Glowing blue atmosphere
        atmosphereAltitude={0.15}
        
        // Big Bright Dots (Removed IP Text)
        labelsData={pointsData}
        labelLat="lat"
        labelLng="lng"
        labelText={() => ""} // Return empty string to hide the IP address text
        labelSize="size"
        labelDotRadius={d => d.size * 1.5} // Massively increased the core dot size
        labelColor="color"
        labelResolution={2}
        labelAltitude={0.02} // Float slightly above surface
        
        // Animated Radar Ping Effect
        ringsData={pointsData}
        ringLat="lat"
        ringLng="lng"
        ringColor="color"
        ringMaxRadius={maxR => maxR.size * 6} // Massive radar pings
        ringPropagationSpeed={2}
        ringRepeatPeriod={800}
      />
    </div>
  );
}
