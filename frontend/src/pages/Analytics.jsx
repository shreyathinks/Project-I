import { useState, useEffect } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, LineChart, Line,
} from 'recharts'
import { predictionApi } from '../api/recipes.js'
import { inventoryApi } from '../api/inventory.js'
import toast from 'react-hot-toast'

const RISK_COLORS = { low: '#22c55e', medium: '#eab308', high: '#ef4444' }
const PIE_COLORS = ['#22c55e', '#eab308', '#ef4444']

export default function Analytics() {
  const [wasteRisk, setWasteRisk] = useState(null)
  const [forecast, setForecast] = useState(null)
  const [inventory, setInventory] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedItem, setSelectedItem] = useState('')
  const [prediction, setPrediction] = useState(null)
  const [predicting, setPredicting] = useState(false)

  useEffect(() => {
    Promise.all([
      predictionApi.getWasteRisk(),
      predictionApi.getShoppingForecast(),
      inventoryApi.list(),
    ]).then(([waste, fc, inv]) => {
      setWasteRisk(waste)
      setForecast(fc)
      setInventory(inv)
    }).catch(() => toast.error('Failed to load analytics'))
      .finally(() => setLoading(false))
  }, [])

  const handlePredict = async () => {
    if (!selectedItem) return
    setPredicting(true)
    try {
      const data = await predictionApi.getConsumption(selectedItem)
      setPrediction(data)
    } catch {
      toast.error('Failed to get prediction')
    } finally {
      setPredicting(false)
    }
  }

  if (loading) {
    return <div className="flex justify-center py-16"><div className="animate-spin rounded-full h-10 w-10 border-4 border-primary-600 border-t-transparent" /></div>
  }

  const riskSummary = wasteRisk?.summary || { low: 0, medium: 0, high: 0 }
  const pieData = [
    { name: 'Low Risk', value: riskSummary.low },
    { name: 'Medium Risk', value: riskSummary.medium },
    { name: 'High Risk', value: riskSummary.high },
  ].filter(d => d.value > 0)

  const highRiskItems = (wasteRisk?.items || []).filter(i => i.risk_level === 'high').slice(0, 5)
  const forecastItems = forecast?.items_to_restock || []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-sm text-gray-500 mt-1">Consumption insights and waste risk analysis</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Waste risk distribution */}
        <div className="card">
          <h2 className="font-semibold text-gray-800 mb-4">Waste Risk Distribution</h2>
          {pieData.length > 0 ? (
            <div className="h-52">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label>
                    {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i]} />)}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : <p className="text-gray-400 text-sm py-8 text-center">No inventory data</p>}
        </div>

        {/* High risk items */}
        <div className="card">
          <h2 className="font-semibold text-gray-800 mb-4">⚠️ High Waste Risk Items</h2>
          {highRiskItems.length === 0 ? (
            <p className="text-green-600 text-sm py-4 text-center">✅ No high-risk items!</p>
          ) : (
            <div className="space-y-2">
              {highRiskItems.map(item => (
                <div key={item.item_id} className="flex items-center justify-between py-2 border-b border-gray-50">
                  <div>
                    <p className="text-sm font-medium text-gray-800">{item.item_name}</p>
                    <p className="text-xs text-gray-400">
                      {item.days_until_expiry !== null ? `${item.days_until_expiry}d until expiry` : 'No expiry date'}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-20 bg-gray-100 rounded-full h-2">
                      <div className="h-2 bg-red-500 rounded-full" style={{ width: `${item.risk_score * 100}%` }} />
                    </div>
                    <span className="text-xs font-bold text-red-600">{Math.round(item.risk_score * 100)}%</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Shopping forecast */}
      {forecastItems.length > 0 && (
        <div className="card">
          <h2 className="font-semibold text-gray-800 mb-4">🛒 Predicted Restocking Needs (next 7 days)</h2>
          <div className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={forecastItems} margin={{ top: 0, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="item_name" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip formatter={(val, name) => [val, name === 'days_remaining' ? 'Days Left' : name]} />
                <Bar dataKey="days_remaining" fill="#16a34a" radius={[4, 4, 0, 0]} name="Days remaining" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Consumption predictor */}
      <div className="card">
        <h2 className="font-semibold text-gray-800 mb-4">📈 Consumption Predictor</h2>
        <div className="flex gap-3 mb-4">
          <select className="input-field flex-1" value={selectedItem}
            onChange={e => setSelectedItem(e.target.value)}>
            <option value="">Select an item...</option>
            {inventory.map(i => <option key={i.id} value={i.name}>{i.name}</option>)}
          </select>
          <button onClick={handlePredict} disabled={!selectedItem || predicting} className="btn-primary shrink-0">
            {predicting ? 'Predicting...' : 'Predict'}
          </button>
        </div>

        {prediction?.prediction && (
          <div className="bg-primary-50 rounded-xl p-4 grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-primary-700">{prediction.prediction.days_remaining}</p>
              <p className="text-xs text-gray-500 mt-0.5">Days Remaining</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-primary-700">{prediction.prediction.restock_date}</p>
              <p className="text-xs text-gray-500 mt-0.5">Restock By</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-primary-700">{prediction.prediction.avg_daily_consumption}</p>
              <p className="text-xs text-gray-500 mt-0.5">Avg/Day</p>
            </div>
            <div className="text-center">
              <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                prediction.prediction.confidence === 'high' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
              }`}>
                {prediction.prediction.confidence} confidence
              </span>
              <p className="text-xs text-gray-400 mt-1">{prediction.prediction.method}</p>
            </div>
          </div>
        )}
        {prediction && !prediction.prediction && (
          <p className="text-sm text-gray-500 bg-gray-50 rounded-lg p-3">{prediction.message}</p>
        )}
      </div>

      {/* Full waste risk table */}
      {wasteRisk?.items?.length > 0 && (
        <div className="card overflow-hidden">
          <h2 className="font-semibold text-gray-800 mb-4">All Items — Waste Risk Scores</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100 text-gray-500 text-xs uppercase tracking-wide">
                  <th className="text-left py-2 pr-4">Item</th>
                  <th className="text-right py-2 pr-4">Qty</th>
                  <th className="text-right py-2 pr-4">Exp. Days</th>
                  <th className="text-center py-2 pr-4">Risk</th>
                  <th className="text-right py-2">Score</th>
                </tr>
              </thead>
              <tbody>
                {wasteRisk.items.map(item => (
                  <tr key={item.item_id} className="border-b border-gray-50 hover:bg-gray-50">
                    <td className="py-2 pr-4 font-medium text-gray-800">{item.item_name}</td>
                    <td className="py-2 pr-4 text-right text-gray-500">{item.quantity}</td>
                    <td className="py-2 pr-4 text-right text-gray-500">
                      {item.days_until_expiry !== null ? item.days_until_expiry : '—'}
                    </td>
                    <td className="py-2 pr-4 text-center">
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium`}
                        style={{ background: RISK_COLORS[item.risk_level] + '20', color: RISK_COLORS[item.risk_level] }}>
                        {item.risk_level}
                      </span>
                    </td>
                    <td className="py-2 text-right text-gray-600">{Math.round(item.risk_score * 100)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
