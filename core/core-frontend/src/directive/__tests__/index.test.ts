import { describe, it, expect, vi } from 'vitest'

const { mockCheckPermission, mockVClickOutside } = vi.hoisted(() => ({
  mockCheckPermission: vi.fn(),
  mockVClickOutside: { beforeMount: vi.fn(), unmounted: vi.fn() }
}))

vi.mock('../Permission', () => ({
  checkPermission: mockCheckPermission
}))

vi.mock('../ClickOutside', () => ({
  vClickOutside: mockVClickOutside
}))

import { installDirective } from '../index'

describe('installDirective', () => {
  it('should register permission and click-outside directives on the app', () => {
    const app = { directive: vi.fn() } as unknown as Parameters<typeof installDirective>[0]

    installDirective(app)

    expect(app.directive).toHaveBeenCalledTimes(2)
    expect(app.directive).toHaveBeenCalledWith('permission', mockCheckPermission)
    expect(app.directive).toHaveBeenCalledWith('click-outside', mockVClickOutside)
  })
})
