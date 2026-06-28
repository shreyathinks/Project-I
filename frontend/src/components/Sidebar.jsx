import { NavLink } from 'react-router-dom'
import {
  HomeIcon, ArchiveBoxIcon, CameraIcon, QrCodeIcon,
  BookOpenIcon, ShoppingCartIcon, ChartBarIcon, UserIcon,
  ArrowUpTrayIcon,
} from '@heroicons/react/24/outline'

const navItems = [
  { to: '/dashboard', icon: HomeIcon, label: 'Dashboard' },
  { to: '/inventory', icon: ArchiveBoxIcon, label: 'Inventory' },
  { to: '/receipt', icon: ArrowUpTrayIcon, label: 'Scan Receipt' },
  { to: '/barcode', icon: QrCodeIcon, label: 'Barcode Scan' },
  { to: '/recipes', icon: BookOpenIcon, label: 'Recipes' },
  { to: '/shopping', icon: ShoppingCartIcon, label: 'Shopping' },
  { to: '/analytics', icon: ChartBarIcon, label: 'Analytics' },
  { to: '/profile', icon: UserIcon, label: 'Profile' },
]

export default function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col shrink-0">
      {/* Logo */}
      <div className="p-6 border-b border-gray-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center text-white text-xl font-bold">
            🍳
          </div>
          <div>
            <p className="font-bold text-gray-900 text-sm leading-tight">Kitchen</p>
            <p className="font-bold text-primary-600 text-sm leading-tight">Intelligence</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`
            }
          >
            <Icon className="w-5 h-5 shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-gray-100">
        <p className="text-xs text-gray-400 text-center">AI Kitchen v1.0</p>
      </div>
    </aside>
  )
}
