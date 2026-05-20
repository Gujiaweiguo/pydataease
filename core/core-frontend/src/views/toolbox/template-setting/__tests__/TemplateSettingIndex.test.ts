import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

vi.mock('@/views/template/index.vue', () => ({
  default: { template: '<div class="template-manage-stub" />' }
}))

describe('TemplateSettingIndex', () => {
  it('renders TemplateManage component', async () => {
    const TemplateSettingIndex = (await import('../index.vue')).default
    const wrapper = shallowMount(TemplateSettingIndex, {
      global: {
        stubs: {
          'template-manage': { template: '<div class="template-manage-stub" />' }
        }
      }
    })
    expect(wrapper.find('.template-manage-stub').exists()).toBe(true)
  })
})
