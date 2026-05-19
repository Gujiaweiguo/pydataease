import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/utils/imgUtils', () => ({
  imgUrlTrans: (url: string) => url
}))

import DeTemplateItem from '../DeTemplateItem.vue'

const globalStubs = {
  ElCheckbox: { template: '<input type="checkbox" />', props: ['modelValue'] },
  ElTooltip: { template: '<div><slot /></div>', props: ['effect', 'content', 'placement'] },
  ElDropdown: {
    template: '<div><slot /><slot name="dropdown" /></div>',
    props: ['size', 'trigger']
  },
  ElDropdownMenu: { template: '<div><slot /></div>' },
  ElDropdownItem: { template: '<div><slot /></div>', props: ['command'] },
  ElIcon: { template: '<i><slot /></i>', props: ['class'] },
  MoreFilled: { template: '<span>...</span>' },
  EditPen: { template: '<span>Edit</span>' },
  Delete: { template: '<span>Del</span>' }
}

const defaultProps = () => ({
  model: {
    name: 'Test Template',
    snapshot: 'http://example.com/snapshot.png',
    checked: false
  },
  width: 200,
  batchState: false
})

describe('DeTemplateItem', () => {
  it('renders with required props', () => {
    const wrapper = shallowMount(DeTemplateItem, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('computes classBackground based on width prop', () => {
    const wrapper = shallowMount(DeTemplateItem, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.classBackground.width).toBe('200px')
    const expectedBgHeight = 200 * 0.714
    expect(parseFloat(vm.classBackground.height)).toBeCloseTo(expectedBgHeight, 1)
  })

  it('computes classImg based on width prop', () => {
    const wrapper = shallowMount(DeTemplateItem, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.classImg.width).toBe('200px')
    const expectedImgHeight = 200 * 0.576
    expect(parseFloat(vm.classImg.height)).toBeCloseTo(expectedImgHeight, 1)
  })

  it('emits command when handleCommand is called', () => {
    const wrapper = shallowMount(DeTemplateItem, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    vm.handleCommand('delete')
    expect(wrapper.emitted('command')).toBeTruthy()
    expect(wrapper.emitted('command')![0][0]).toBe('delete')
  })

  it('updates classBackground when width prop changes', async () => {
    const wrapper = shallowMount(DeTemplateItem, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    await wrapper.setProps({ width: 300 })
    const vm = wrapper.vm as any
    expect(vm.classBackground.width).toBe('300px')
  })
})
