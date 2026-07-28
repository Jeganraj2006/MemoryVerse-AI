/**
 * TypeBadge — colored pill badge for document types
 */

const BADGE_CONFIG = {
  Certification: 'certification',
  Project:       'project',
  Internship:    'internship',
  Achievement:   'achievement',
  Academic:      'academic',
  Skill:         'skill',
}

export default function TypeBadge({ type, size = 'default' }) {
  const cls = BADGE_CONFIG[type] ?? 'achievement'
  return (
    <span className={`type-badge ${cls}`} style={size === 'sm' ? { fontSize: '0.65rem' } : {}}>
      {type}
    </span>
  )
}
