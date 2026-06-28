import { useState } from 'react'
import { ClockIcon, UserGroupIcon } from '@heroicons/react/24/outline'

export default function RecipeCard({ recipe }) {
  const [expanded, setExpanded] = useState(false)

  let ingredients = []
  try {
    ingredients = JSON.parse(recipe.ingredients)
  } catch {
    ingredients = [recipe.ingredients]
  }

  return (
    <div className="card hover:shadow-md transition-shadow duration-200">
      {/* Header */}
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-semibold text-gray-900 flex-1">{recipe.title}</h3>
        {recipe.is_vegan && (
          <span className="ml-2 text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">Vegan</span>
        )}
        {!recipe.is_vegan && recipe.is_vegetarian && (
          <span className="ml-2 text-xs bg-lime-100 text-lime-700 px-2 py-0.5 rounded-full font-medium">Veggie</span>
        )}
      </div>

      {recipe.description && (
        <p className="text-sm text-gray-500 mb-3 line-clamp-2">{recipe.description}</p>
      )}

      {/* Stats row */}
      <div className="flex items-center gap-4 text-xs text-gray-500 mb-3">
        {recipe.cooking_time_minutes && (
          <span className="flex items-center gap-1">
            <ClockIcon className="w-3.5 h-3.5" />
            {recipe.cooking_time_minutes} min
          </span>
        )}
        <span className="flex items-center gap-1">
          <UserGroupIcon className="w-3.5 h-3.5" />
          {recipe.servings} servings
        </span>
        {recipe.calories && (
          <span>🔥 {Math.round(recipe.calories)} cal</span>
        )}
        {recipe.cuisine && (
          <span className="bg-gray-100 px-2 py-0.5 rounded text-gray-600">{recipe.cuisine}</span>
        )}
      </div>

      {/* Dietary badges */}
      <div className="flex flex-wrap gap-1 mb-3">
        {recipe.is_high_protein && <span className="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">High Protein</span>}
        {recipe.is_gluten_free && <span className="text-xs bg-purple-50 text-purple-600 px-2 py-0.5 rounded-full">Gluten Free</span>}
      </div>

      {/* Ingredients preview */}
      <p className="text-xs text-gray-500 mb-1 font-medium">Ingredients:</p>
      <p className="text-xs text-gray-600 line-clamp-2">{ingredients.slice(0, 6).join(', ')}</p>

      <button
        onClick={() => setExpanded(v => !v)}
        className="mt-3 text-xs text-primary-600 hover:text-primary-700 font-medium"
      >
        {expanded ? 'Hide instructions ↑' : 'View instructions ↓'}
      </button>

      {expanded && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <p className="text-xs text-gray-500 font-medium mb-1">All Ingredients:</p>
          <ul className="text-xs text-gray-600 list-disc ml-4 mb-3 space-y-0.5">
            {ingredients.map((ing, i) => <li key={i}>{ing}</li>)}
          </ul>
          <p className="text-xs text-gray-500 font-medium mb-1">Instructions:</p>
          <p className="text-xs text-gray-600 whitespace-pre-line">{recipe.instructions}</p>
        </div>
      )}
    </div>
  )
}
