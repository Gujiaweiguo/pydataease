import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

vi.mock('@/views/data-visualization/PreviewShow.vue', () => ({
  default: { template: '<div class="preview-show-stub" />' }
}))

describe('ScreenIndex', () => {
  it('renders PreviewShow component', async () => {
    const ScreenIndex = (await import('../index.vue')).default
    const wrapper = shallowMount(ScreenIndex, {
      global: {
        stubs: {
          'preview-show': { template: '<div class="preview-show-stub" />' }
        }
      }
    })
    expect(wrapper.find('.preview-show-stub').exists()).toBe(true)
  })
})
