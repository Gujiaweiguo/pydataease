import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (k: string) => k
  })
}))

import TimeSetDialog from '../index.vue'

const globalConfig = {
  global: {
    stubs: {
      'el-dialog': {
        template: '<div class="el-dialog-stub"><slot /><slot name="footer" /></div>',
        props: ['beforeClose', 'modelValue', 'title', 'width', 'appendToBody']
      },
      'el-form': { template: '<div><slot /></div>', props: ['labelPosition'] },
      'el-form-item': { template: '<div><slot /></div>', props: ['label'] },
      'el-select': { template: '<div />', props: ['placeholder', 'modelValue'] },
      'el-option': { template: '<div />', props: ['key', 'label', 'value'] },
      'el-date-picker': { template: '<div />', props: ['style', 'modelValue', 'type'] },
      'el-button': { template: '<button><slot /></button>', props: ['type'] }
    },
    mocks: { $t: (k: string) => k }
  }
}

describe('TimeSetDialog', () => {
  it('should render without errors', () => {
    const wrapper = shallowMount(TimeSetDialog, globalConfig)
    expect(wrapper.find('.el-dialog-stub').exists()).toBe(true)
  })

  it('should expose init method', () => {
    const wrapper = shallowMount(TimeSetDialog, globalConfig)
    expect(typeof (wrapper.vm as any).init).toBe('function')
  })
})
