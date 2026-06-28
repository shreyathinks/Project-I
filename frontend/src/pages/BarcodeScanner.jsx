import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { inventoryApi } from '../api/inventory.js'
import toast from 'react-hot-toast'

export default function BarcodeScanner() {
  const navigate = useNavigate()
  const videoRef = useRef(null)
  const [scanning, setScanning] = useState(false)
  const [product, setProduct] = useState(null)
  const [manualBarcode, setManualBarcode] = useState('')
  const [looking, setLooking] = useState(false)
  const [form, setForm] = useState(null)

  useEffect(() => {
    return () => { stopCamera() }
  }, [])

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
      if (videoRef.current) videoRef.current.srcObject = stream
      setScanning(true)
      startQuagga()
    } catch {
      toast.error('Camera access denied. Try entering the barcode manually.')
    }
  }

  const stopCamera = () => {
    if (videoRef.current?.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(t => t.stop())
    }
    setScanning(false)
    if (window.Quagga) window.Quagga.stop()
  }

  const startQuagga = () => {
    if (!window.Quagga) return

    window.Quagga.init({
      inputStream: { type: 'LiveStream', target: videoRef.current },
      decoder: { readers: ['ean_reader', 'upc_reader', 'code_128_reader', 'code_39_reader'] },
    }, (err) => {
      if (!err) {
        window.Quagga.start()
        window.Quagga.onDetected(async (data) => {
          const code = data.codeResult.code
          stopCamera()
          await lookupBarcode(code)
        })
      }
    })
  }

  const lookupBarcode = async (barcode) => {
    setLooking(true)
    try {
      const p = await inventoryApi.lookupBarcode(barcode)
      setProduct(p)
      setForm({
        name: p.name, brand: p.brand || '', quantity: 1, unit: p.unit || 'units',
        purchase_date: new Date().toISOString().split('T')[0],
        storage_location: 'pantry', barcode,
      })
      toast.success('Product found!')
    } catch {
      toast.error('Product not found. Please fill in the details manually.')
      setProduct(null)
      setForm({
        name: '', brand: '', quantity: 1, unit: 'units',
        purchase_date: new Date().toISOString().split('T')[0],
        storage_location: 'pantry', barcode,
      })
    } finally {
      setLooking(false)
    }
  }

  const handleManualLookup = async () => {
    if (!manualBarcode.trim()) return
    await lookupBarcode(manualBarcode.trim())
  }

  const handleAddToInventory = async () => {
    try {
      await inventoryApi.create({ ...form, quantity: Number(form.quantity) })
      toast.success(`${form.name} added to inventory!`)
      navigate('/inventory')
    } catch {
      toast.error('Failed to add item')
    }
  }

  return (
    <div className="max-w-lg mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Barcode Scanner</h1>
        <p className="text-sm text-gray-500 mt-1">Scan a barcode or enter it manually to look up a product</p>
      </div>

      {/* Camera viewfinder */}
      <div className="card overflow-hidden">
        <div className="relative bg-black rounded-lg overflow-hidden" style={{ aspectRatio: '4/3' }}>
          <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
          {!scanning && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-900/80">
              <div className="text-center text-white">
                <p className="text-4xl mb-3">📲</p>
                <p className="text-sm font-medium">Camera not active</p>
                <button onClick={startCamera} className="btn-primary mt-3 text-sm">
                  Start Camera
                </button>
              </div>
            </div>
          )}
          {scanning && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="border-2 border-primary-400 w-48 h-32 rounded-lg" />
              <p className="absolute bottom-4 text-white text-xs bg-black/50 px-3 py-1 rounded-full">
                Point camera at barcode
              </p>
            </div>
          )}
        </div>
        {scanning && (
          <button onClick={stopCamera} className="btn-secondary w-full mt-3 text-sm">
            Stop Camera
          </button>
        )}
      </div>

      {/* Manual entry */}
      <div className="card">
        <p className="text-sm font-medium text-gray-700 mb-3">Enter barcode manually</p>
        <div className="flex gap-2">
          <input
            className="input-field flex-1"
            placeholder="e.g. 5000112637922"
            value={manualBarcode}
            onChange={e => setManualBarcode(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleManualLookup()}
          />
          <button onClick={handleManualLookup} disabled={looking} className="btn-primary shrink-0">
            {looking ? '...' : 'Lookup'}
          </button>
        </div>
      </div>

      {/* Product result form */}
      {form && (
        <div className="card space-y-4">
          <h2 className="font-semibold text-gray-800">
            {product ? '✅ Product Found' : '➕ Enter Details'}
          </h2>
          {product && (
            <div className="bg-primary-50 rounded-lg p-3 text-sm">
              <p className="font-medium text-primary-800">{product.name}</p>
              {product.brand && <p className="text-primary-600 text-xs">{product.brand}</p>}
              <p className="text-xs text-gray-500 mt-1">Source: {product.source}</p>
            </div>
          )}
          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2">
              <label className="label">Name</label>
              <input className="input-field" value={form.name}
                onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
            </div>
            <div>
              <label className="label">Quantity</label>
              <input type="number" min="0.01" step="0.01" className="input-field"
                value={form.quantity} onChange={e => setForm(f => ({ ...f, quantity: e.target.value }))} />
            </div>
            <div>
              <label className="label">Unit</label>
              <select className="input-field" value={form.unit}
                onChange={e => setForm(f => ({ ...f, unit: e.target.value }))}>
                {['units', 'g', 'kg', 'ml', 'L', 'pack', 'can', 'bottle'].map(u => (
                  <option key={u} value={u}>{u}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">Storage</label>
              <select className="input-field" value={form.storage_location}
                onChange={e => setForm(f => ({ ...f, storage_location: e.target.value }))}>
                <option value="refrigerator">🧊 Refrigerator</option>
                <option value="pantry">🏠 Pantry</option>
                <option value="freezer">❄️ Freezer</option>
              </select>
            </div>
            <div>
              <label className="label">Purchase Date</label>
              <input type="date" className="input-field" value={form.purchase_date}
                onChange={e => setForm(f => ({ ...f, purchase_date: e.target.value }))} />
            </div>
          </div>
          <button onClick={handleAddToInventory} className="btn-primary w-full">
            Add to Inventory
          </button>
        </div>
      )}
    </div>
  )
}
