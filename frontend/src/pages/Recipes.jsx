import { useState, useEffect } from 'react'
import { inventoryApi } from '../api/inventory.js'
import { recipesApi } from '../api/recipes.js'
import RecipeCard from '../components/RecipeCard.jsx'
import toast from 'react-hot-toast'

export default function Recipes() {
  const [inventory, setInventory] = useState([])
  const [recipes, setRecipes] = useState([])
  const [generated, setGenerated] = useState(null)
  const [source, setSource] = useState('faiss')
  const [loading, setLoading] = useState(false)
  const [browsing, setBrowsing] = useState(false)
  const [filters, setFilters] = useState({
    filter_vegetarian: false,
    filter_vegan: false,
    filter_high_protein: false,
    max_cooking_time: '',
    use_expiring_first: true,
    top_k: 6,
  })
  const [search, setSearch] = useState('')
  const [browseResults, setBrowseResults] = useState([])
  const [activeTab, setActiveTab] = useState('recommend')

  useEffect(() => {
    inventoryApi.list({ include_consumed: false }).then(setInventory).catch(() => {})
  }, [])

  const handleRecommend = async () => {
    setLoading(true)
    setGenerated(null)
    try {
      const ingredients = inventory.map(i => i.name)
      const data = await recipesApi.recommend({
        available_ingredients: ingredients,
        ...filters,
        max_cooking_time: filters.max_cooking_time ? Number(filters.max_cooking_time) : undefined,
      })
      setRecipes(data.recipes)
      setGenerated(data.generated_recipe)
      setSource(data.source)
      if (data.recipes.length === 0) toast('No recipes found with current filters', { icon: '🍽️' })
    } catch {
      toast.error('Failed to get recommendations')
    } finally {
      setLoading(false)
    }
  }

  const handleBrowse = async () => {
    setBrowsing(true)
    try {
      const params = {}
      if (search) params.search = search
      if (filters.filter_vegetarian) params.vegetarian = true
      if (filters.filter_vegan) params.vegan = true
      setBrowseResults(await recipesApi.list(params))
    } catch {
      toast.error('Failed to browse recipes')
    } finally {
      setBrowsing(false)
    }
  }

  const toggle = (key) => setFilters(f => ({ ...f, [key]: !f[key] }))

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Recipes</h1>
        <p className="text-sm text-gray-500 mt-1">AI-powered recommendations from your inventory</p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200">
        {['recommend', 'browse'].map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)}
            className={`px-5 py-2.5 text-sm font-medium border-b-2 transition-colors capitalize ${
              activeTab === tab ? 'border-primary-600 text-primary-700' : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}>
            {tab === 'recommend' ? '✨ Smart Recommend' : '📚 Browse All'}
          </button>
        ))}
      </div>

      {activeTab === 'recommend' && (
        <>
          {/* Filters */}
          <div className="card">
            <h2 className="font-medium text-gray-700 mb-3 text-sm">Filters</h2>
            <div className="flex flex-wrap gap-3">
              {[
                ['filter_vegetarian', '🥗 Vegetarian'],
                ['filter_vegan', '🌱 Vegan'],
                ['filter_high_protein', '💪 High Protein'],
                ['use_expiring_first', '⏰ Use expiring first'],
              ].map(([key, label]) => (
                <button key={key} onClick={() => toggle(key)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                    filters[key]
                      ? 'bg-primary-100 border-primary-400 text-primary-700'
                      : 'bg-white border-gray-300 text-gray-600 hover:border-gray-400'
                  }`}>
                  {label}
                </button>
              ))}
              <div className="flex items-center gap-2">
                <label className="text-xs text-gray-600">Max time:</label>
                <input type="number" min="5" step="5" className="input-field py-1 text-xs w-20"
                  placeholder="mins" value={filters.max_cooking_time}
                  onChange={e => setFilters(f => ({ ...f, max_cooking_time: e.target.value }))} />
              </div>
            </div>

            <div className="mt-3 flex items-center gap-2">
              <label className="text-xs text-gray-600">Using {inventory.length} inventory items</label>
            </div>
          </div>

          <button onClick={handleRecommend} disabled={loading || inventory.length === 0} className="btn-primary w-full py-3">
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Finding recipes...
              </span>
            ) : '✨ Get AI Recommendations'}
          </button>

          {/* LLM generated recipe */}
          {generated && (
            <div className="card bg-gradient-to-br from-primary-50 to-green-50 border-primary-200">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-lg">🤖</span>
                <h2 className="font-semibold text-primary-800">AI Generated Recipe</h2>
                <span className="text-xs bg-primary-100 text-primary-600 px-2 py-0.5 rounded-full">Ollama</span>
              </div>
              <p className="text-sm text-gray-700 whitespace-pre-line">{generated}</p>
            </div>
          )}

          {/* Recipe cards */}
          {recipes.length > 0 && (
            <div>
              <p className="text-sm text-gray-500 mb-3">
                {recipes.length} recipes found {source === 'faiss' ? '(FAISS similarity)' : ''}
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {recipes.map(r => <RecipeCard key={r.id} recipe={r} />)}
              </div>
            </div>
          )}
        </>
      )}

      {activeTab === 'browse' && (
        <>
          <div className="flex gap-3">
            <input className="input-field flex-1" placeholder="Search recipes..."
              value={search} onChange={e => setSearch(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleBrowse()} />
            <button onClick={handleBrowse} disabled={browsing} className="btn-primary shrink-0">
              {browsing ? '...' : 'Search'}
            </button>
          </div>
          <div className="flex gap-2">
            {[['filter_vegetarian', 'Vegetarian'], ['filter_vegan', 'Vegan']].map(([key, label]) => (
              <button key={key} onClick={() => toggle(key)}
                className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
                  filters[key] ? 'bg-primary-100 border-primary-400 text-primary-700' : 'bg-white border-gray-300 text-gray-600'
                }`}>
                {label}
              </button>
            ))}
          </div>
          {browseResults.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {browseResults.map(r => <RecipeCard key={r.id} recipe={r} />)}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <p className="text-3xl mb-3">📚</p>
              <p>Search for recipes or click the button to browse all</p>
              <button onClick={handleBrowse} className="btn-secondary mt-3 text-sm">Browse all recipes</button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
