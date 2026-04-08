import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const fetchStatus = async () => {
  try {
    const response = await axios.get(`${API_URL}/status`)
    return response.data
  } catch (error) {
    console.error('Failed to fetch status:', error)
    return null
  }
}

export const triggerScenario = async (scenario: string) => {
  try {
    const response = await axios.post(`${API_URL}/trigger`, { scenario })
    return response.data
  } catch (error) {
    console.error('Failed to trigger scenario:', error)
    throw error
  }
}

export const setupWebSocket = (onMessage: (message: any) => void) => {
  try {
    const wsUrl = API_URL.replace('http', 'ws') + '/ws'
    const ws = new WebSocket(wsUrl)

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        onMessage(message)
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    return ws
  } catch (error) {
    console.error('Failed to setup WebSocket:', error)
    return null
  }
}