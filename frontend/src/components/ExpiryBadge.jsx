export default function ExpiryBadge({ status, daysUntil }) {
  if (status === 'expired') {
    return (
      <span className="badge-danger">
        🗑️ Expired
      </span>
    )
  }
  if (status === 'expiring_soon') {
    return (
      <span className="badge-warning">
        ⚠️ {daysUntil === 0 ? 'Today' : `${daysUntil}d`}
      </span>
    )
  }
  return (
    <span className="badge-fresh">
      ✅ Fresh
    </span>
  )
}
