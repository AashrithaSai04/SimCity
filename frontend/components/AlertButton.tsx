'use client'

import { useState } from 'react'
import axios from 'axios'

interface AlertButtonProps {
  scenario: string
  activeScenario: string | null
  setActiveScenario: (scenario: string | null) => void
}

const icons = {
  flood: '🌊',
  earthquake: '🌍',
  fire: '🔥'
}

export default function AlertButton({ scenario, activeScenario, setActiveScenario }: AlertButtonProps) {
  const [loading, setLoading] = useState(false)

  const handleTrigger = async () => {
    setLoading(true)
    try {
      await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/trigger`, {
        scenario: scenario
      })
      setActiveScenario(scenario)
    } catch (error) {
      console.error('Failed to trigger scenario:', error)
    } finally {
      setLoading(false)
    }
  }

  const isActive = activeScenario === scenario

  return (
    <button
      onClick={handleTrigger}
      disabled={loading || isActive}
      className={`px-6 py-2 rounded-lg font-semibold transition ${
        isActive
          ? 'bg-red-600 text-white'
          : 'bg-slate-700 hover:bg-slate-600 text-white'
      }`}
    >
      {icons[scenario as keyof typeof icons]} {scenario.charAt(0).toUpperCase() + scenario.slice(1)}
    </button>
  )
}