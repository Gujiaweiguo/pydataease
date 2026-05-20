import { describe, it, expect, vi } from 'vitest'

vi.mock('../../install', () => ({
  withInstall: vi.fn((component: any) => component)
}))

vi.mock('@/views/dashboard/index.vue', () => ({
  default: { name: 'Dashboard', template: '<div>dashboard</div>' }
}))

import { DeDashboard } from '../index'

describe('DeDashboard', () => {
  it('should export DeDashboard', () => {
    expect(DeDashboard).toBeDefined()
  })

  it('should be the result of withInstall', async () => {
    const { withInstall } = await import('../../install')
    expect(withInstall).toHaveBeenCalled()
  })
})
