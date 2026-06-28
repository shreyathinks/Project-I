import { TrashIcon, PencilIcon } from '@heroicons/react/24/outline'
import ExpiryBadge from './ExpiryBadge.jsx'

const LOCATION_ICONS = { refrigerator: '🧊', pantry: '🏠', freezer: '❄️' }

export default function InventoryCard({ item, onDelete, onConsume, onEdit }) {
  return (
    <div className="card hover:shadow-md transition-shadow duration-200 group">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 truncate">{item.name}</h3>
          {item.brand && <p className="text-xs text-gray-400 mt-0.5">{item.brand}</p>}
        </div>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity ml-2">
          {onEdit && (
            <button onClick={() => onEdit(item)} className="p-1.5 rounded hover:bg-gray-100 text-gray-400 hover:text-gray-700">
              <PencilIcon className="w-4 h-4" />
            </button>
          )}
          {onDelete && (
            <button onClick={() => onDelete(item.id)} className="p-1.5 rounded hover:bg-red-50 text-gray-400 hover:text-red-600">
              <TrashIcon className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2 mb-3">
        <ExpiryBadge status={item.expiry_status} daysUntil={item.days_until_expiry} />
        <span className="text-xs text-gray-500">
          {LOCATION_ICONS[item.storage_location]} {item.storage_location}
        </span>
      </div>

      <div className="flex items-center justify-between text-sm text-gray-600">
        <span className="font-medium">{item.quantity} {item.unit}</span>
        {item.expiry_date && (
          <span className="text-xs text-gray-400">
            Exp: {new Date(item.expiry_date).toLocaleDateString()}
          </span>
        )}
      </div>

      {item.category_obj && (
        <p className="text-xs text-gray-400 mt-2">{item.category_obj.icon} {item.category_obj.name}</p>
      )}

      {onConsume && (
        <button
          onClick={() => onConsume(item)}
          className="mt-3 w-full text-xs btn-secondary py-1.5"
        >
          Mark as Consumed
        </button>
      )}
    </div>
  )
}
