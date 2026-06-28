import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { ArrowUpTrayIcon, CheckIcon } from '@heroicons/react/24/outline'
import { inventoryApi } from '../api/inventory.js'
import toast from 'react-hot-toast'

export default function ReceiptUpload() {
  const navigate = useNavigate()
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [scanning, setScanning] = useState(false)
  const [result, setResult] = useState(null)
  const [selected, setSelected] = useState([])
  const [saving, setSaving] = useState(false)

  const onDrop = useCallback((accepted) => {
    const f = accepted[0]
    setFile(f)
    setPreview(URL.createObjectURL(f))
    setResult(null)
    setSelected([])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpg', '.jpeg', '.png', '.bmp', '.webp'] },
    maxFiles: 1,
  })

  const handleScan = async () => {
    if (!file) return
    setScanning(true)
    try {
      const data = await inventoryApi.scanReceipt(file)
      setResult(data)
      setSelected(data.items.map((_, i) => i))
      toast.success(`Found ${data.items.length} items on receipt!`)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'OCR scan failed')
    } finally {
      setScanning(false)
    }
  }

  const toggleSelect = (i) => {
    setSelected(prev => prev.includes(i) ? prev.filter(x => x !== i) : [...prev, i])
  }

  const handleAddToInventory = async () => {
    const toAdd = result.items.filter((_, i) => selected.includes(i)).map(item => ({
      ...item,
      purchase_date: result.purchase_date,
      storage_location: 'pantry',
    }))
    if (toAdd.length === 0) { toast.error('Select at least one item'); return }
    setSaving(true)
    try {
      await inventoryApi.bulkCreate(toAdd)
      toast.success(`${toAdd.length} items added to inventory!`)
      navigate('/inventory')
    } catch {
      toast.error('Failed to save items')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Scan Grocery Receipt</h1>
        <p className="text-sm text-gray-500 mt-1">Upload a photo of your receipt to auto-populate inventory</p>
      </div>

      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${
          isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400 bg-gray-50'
        }`}
      >
        <input {...getInputProps()} />
        <ArrowUpTrayIcon className="w-10 h-10 text-gray-400 mx-auto mb-3" />
        {file ? (
          <p className="text-sm font-medium text-gray-700">{file.name}</p>
        ) : (
          <>
            <p className="text-sm font-medium text-gray-700">Drop receipt image here, or click to select</p>
            <p className="text-xs text-gray-400 mt-1">JPG, PNG, WebP up to 10 MB</p>
          </>
        )}
      </div>

      {preview && (
        <div className="card">
          <p className="text-sm font-medium text-gray-600 mb-2">Preview</p>
          <img src={preview} alt="Receipt preview" className="max-h-64 rounded-lg object-contain mx-auto" />
        </div>
      )}

      {file && !result && (
        <button onClick={handleScan} disabled={scanning} className="btn-primary w-full py-3">
          {scanning ? (
            <span className="flex items-center justify-center gap-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Scanning receipt...
            </span>
          ) : '🔍 Scan Receipt with OCR'}
        </button>
      )}

      {result && (
        <div className="card space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-gray-800">Extracted Items ({result.items.length})</h2>
            <p className="text-xs text-gray-500">Purchase date: {result.purchase_date}</p>
          </div>

          <div className="flex gap-2 text-xs">
            <button onClick={() => setSelected(result.items.map((_, i) => i))}
              className="text-primary-600 hover:underline">Select all</button>
            <span className="text-gray-300">|</span>
            <button onClick={() => setSelected([])} className="text-gray-500 hover:underline">Deselect all</button>
          </div>

          <div className="space-y-2 max-h-72 overflow-y-auto">
            {result.items.map((item, i) => (
              <label key={i} className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer border-2 transition-colors ${
                selected.includes(i) ? 'border-primary-300 bg-primary-50' : 'border-transparent bg-gray-50 hover:bg-gray-100'
              }`}>
                <input type="checkbox" checked={selected.includes(i)} onChange={() => toggleSelect(i)}
                  className="w-4 h-4 text-primary-600 rounded" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800 truncate">{item.name}</p>
                </div>
                <span className="text-xs text-gray-500 shrink-0">{item.quantity} {item.unit}</span>
              </label>
            ))}
          </div>

          {result.items.length > 0 && (
            <button
              onClick={handleAddToInventory}
              disabled={saving || selected.length === 0}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              {saving ? 'Saving...' : (
                <><CheckIcon className="w-4 h-4" /> Add {selected.length} items to Inventory</>
              )}
            </button>
          )}
        </div>
      )}
    </div>
  )
}
