'use client'

import MetricCard from './MetricCard'

interface BentoGridProps {
  data: {
    traffic?: Array<any>
    hospitals?: Array<any>
    supply?: Array<any>
    alerts?: Array<any>
  }
}

export default function BentoGrid({ data }: BentoGridProps) {
  return (
    <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {/* Traffic Metrics */}
      {data.traffic?.map((zone) => (
        <MetricCard
          key={zone._id}
          icon="🚗"
          title={`Traffic - ${zone._id}`}
          value={`${zone.avg_speed?.toFixed(1)} km/h`}
          subValue={`Congestion: ${(zone.avg_congestion * 100).toFixed(0)}%`}
          status={zone.avg_congestion > 0.85 ? 'critical' : zone.avg_congestion > 0.6 ? 'warning' : 'normal'}
        />
      ))}

      {/* Hospital Metrics */}
      {data.hospitals?.map((facility) => (
        <MetricCard
          key={facility._id}
          icon="🏥"
          title={`Hospital - ${facility._id}`}
          value={`${facility.avg_occupancy?.toFixed(1)}%`}
          subValue={`ER Wait: ${facility.avg_er_wait?.toFixed(0)} min`}
          status={facility.avg_occupancy > 90 ? 'critical' : facility.avg_occupancy > 70 ? 'warning' : 'normal'}
        />
      ))}

      {/* Supply Metrics */}
      {data.supply?.map((warehouse) => (
        <MetricCard
          key={warehouse._id}
          icon="📦"
          title={`Supply - ${warehouse._id}`}
          value={`${warehouse.avg_inventory?.toFixed(1)}%`}
          subValue={`ETA: ${warehouse.avg_eta?.toFixed(1)} hours`}
          status={warehouse.avg_inventory < 20 ? 'critical' : warehouse.avg_inventory < 50 ? 'warning' : 'normal'}
        />
      ))}
    </div>
  )
}