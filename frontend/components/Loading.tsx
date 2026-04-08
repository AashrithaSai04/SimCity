export default function Loading() {
  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin mb-4">
          <div className="text-6xl">🏙️</div>
        </div>
        <p className="text-gray-400">Loading SimCity Dashboard...</p>
      </div>
    </div>
  )
}