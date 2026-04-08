'use client'

import { useEffect, useRef } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || ''

interface TrafficData {
  _id: string
  avg_speed: number
  avg_congestion: number
}

export default function Map({ trafficData }: { trafficData: TrafficData[] }) {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<InstanceType<typeof mapboxgl.Map> | null>(null)
  const markersRef = useRef<Array<InstanceType<typeof mapboxgl.Marker>>>([])
  const token = process.env.NEXT_PUBLIC_MAPBOX_TOKEN
  const hasValidToken = Boolean(token && token.startsWith('pk.'))

  useEffect(() => {
    if (!mapContainer.current || !hasValidToken || !token) return

    mapboxgl.accessToken = token

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11',
      center: [-74.0, 40.7],
      zoom: 11,
    })

    return () => {
      markersRef.current.forEach((marker) => marker.remove())
      markersRef.current = []
      map.current?.remove()
    }
  }, [hasValidToken, token])

  // Update markers based on traffic data
  useEffect(() => {
    if (!map.current || !trafficData) return

    const currentMap = map.current

    markersRef.current.forEach((marker) => marker.remove())
    markersRef.current = []

    const coords = {
      downtown: { lat: 40.7128, lng: -74.006 },
      suburban: { lat: 40.7489, lng: -73.968 },
      highway: { lat: 40.6892, lng: -74.0445 }
    }

    trafficData.forEach((zone) => {
      const coord = coords[zone._id as keyof typeof coords]
      if (!coord) return

      const color = zone.avg_congestion > 0.85 ? '#ff4444' : zone.avg_congestion > 0.6 ? '#ffaa00' : '#00aa00'

      const el = document.createElement('div')
      el.className = 'marker'
      el.style.width = '30px'
      el.style.height = '30px'
      el.style.borderRadius = '50%'
      el.style.backgroundColor = color
      el.style.border = '2px solid white'
      el.style.cursor = 'pointer'
      el.title = `${zone._id}: ${zone.avg_congestion * 100}%`

      const marker = new mapboxgl.Marker(el)
        .setLngLat([coord.lng, coord.lat])
        .addTo(currentMap)

      markersRef.current.push(marker)
    })
  }, [trafficData])

  if (!hasValidToken) {
    return (
      <div className="w-full h-full rounded-lg overflow-hidden grid place-items-center bg-slate-900/60 border border-slate-700">
        <div className="text-center px-6">
          <p className="text-lg font-semibold text-slate-100">Mapbox Token Missing Or Invalid</p>
          <p className="text-sm text-slate-300 mt-2">
            Set a real public token (starts with pk.) in frontend/.env.local as NEXT_PUBLIC_MAPBOX_TOKEN.
          </p>
        </div>
      </div>
    )
  }

  return <div ref={mapContainer} className="w-full h-full rounded-lg overflow-hidden" />
}