'use client'

import { useEffect, useState } from 'react'
import Map from '@/components/Map'
import BentoGrid from '@/components/BentoGrid'
import AlertButton from '@/components/AlertButton'
import Loading from '@/components/Loading'
import { fetchStatus, setupWebSocket } from '@/lib/api'

interface AlertItem {
  type: string
  severity: 'high' | 'medium' | 'low'
  facility_id?: string
  zone?: string
  warehouse?: string
}

interface TrafficItem {
  _id: string
  avg_speed: number
  avg_congestion: number
}

interface DashboardData {
  traffic?: TrafficItem[]
  alerts?: AlertItem[]
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeScenario, setActiveScenario] = useState<string | null>(null)

  useEffect(() => {
    // Initial fetch
    fetchStatus().then(setData).catch(console.error).finally(() => setLoading(false))

    // Poll every 5 seconds
    const interval = setInterval(() => {
      fetchStatus().then(setData).catch(console.error)
    }, 5000)

    // Setup WebSocket
    const ws = setupWebSocket((message) => {
      if (message.type === 'status_update') {
        setData(message.data)
      }
    })

    return () => {
      clearInterval(interval)
      ws?.close()
    }
  }, [])

  if (loading) return <Loading />

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-4">
      {/* Header */}
      <header className="mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              🏙️ SimCity Command Center
            </h1>
            <p className="text-gray-400 mt-2">Real-time disaster simulation & monitoring</p>
          </div>
          <div className="text-right">
            {activeScenario && (
              <div className="glass-effect px-4 py-2 rounded-lg mb-2">
                <span className="font-bold text-warning">Active: {activeScenario.toUpperCase()}</span>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Control Buttons */}
      <div className="mb-6 flex gap-3 flex-wrap">
        <AlertButton scenario="flood" activeScenario={activeScenario} setActiveScenario={setActiveScenario} />
        <AlertButton scenario="earthquake" activeScenario={activeScenario} setActiveScenario={setActiveScenario} />
        <AlertButton scenario="fire" activeScenario={activeScenario} setActiveScenario={setActiveScenario} />
        {activeScenario && (
          <button
            onClick={() => setActiveScenario(null)}
            className="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg font-semibold transition"
          >
            🔄 Reset
          </button>
        )}
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Map - takes full width on mobile, 2 cols on desktop */}
        <div className="xl:col-span-2 card h-96">
          <h2 className="text-2xl font-bold mb-4">🗺️ City Map</h2>
          <Map trafficData={data?.traffic ?? []} />
        </div>

        {/* Alerts Sidebar */}
        <div className="card h-96 overflow-y-auto">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            🚨 Alerts
            {data?.alerts && data.alerts.length > 0 && (
              <span className="bg-critical text-white text-sm px-2 py-1 rounded-full">
                {data.alerts.length}
              </span>
            )}
          </h2>
          {data?.alerts && data.alerts.length > 0 ? (
            <div className="space-y-2">
              {data.alerts.map((alert, idx) => (
                <div
                  key={idx}
                  className={`p-3 rounded-lg text-sm border-l-4 ${
                    alert.severity === 'high'
                      ? 'bg-red-900/30 border-red-500'
                      : alert.severity === 'medium'
                      ? 'bg-yellow-900/30 border-yellow-500'
                      : 'bg-blue-900/30 border-blue-500'
                  }`}
                >
                  <p className="font-bold">{alert.type}</p>
                  <p className="text-gray-300">{alert.facility_id || alert.zone || alert.warehouse}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400">No active alerts</p>
          )}
        </div>
      </div>

      {/* Metrics Grid */}
      {data && <BentoGrid data={data} />}
    </div>
  )
}