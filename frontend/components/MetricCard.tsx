'use client'

interface MetricCardProps {
  icon: string
  title: string
  value: string
  subValue: string
  status: 'critical' | 'warning' | 'normal'
}

export default function MetricCard({ icon, title, value, subValue, status }: MetricCardProps) {
  const statusColor = {
    critical: 'border-red-500 bg-red-900/10',
    warning: 'border-yellow-500 bg-yellow-900/10',
    normal: 'border-green-500 bg-green-900/10'
  }

  return (
    <div className={`card border-l-4 ${statusColor[status]}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-gray-400 text-sm">{title}</p>
          <p className="text-3xl font-bold mt-2">{icon} {value}</p>
          <p className="text-gray-400 text-sm mt-2">{subValue}</p>
        </div>
        <div className={`w-3 h-3 rounded-full ${
          status === 'critical' ? 'bg-red-500 animate-pulse' : 
          status === 'warning' ? 'bg-yellow-500' : 
          'bg-green-500'
        }`}></div>
      </div>
    </div>
  )
}