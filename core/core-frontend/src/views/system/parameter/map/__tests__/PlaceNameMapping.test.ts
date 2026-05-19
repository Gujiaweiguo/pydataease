import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('lodash-es', () => ({
  debounce: (fn: any) => fn,
  forEach: (obj: any, cb: any) => {
    if (Array.isArray(obj)) obj.forEach(cb)
    else Object.keys(obj).forEach(k => cb(obj[k], k))
  },
  cloneDeep: (v: any) => JSON.parse(JSON.stringify(v))
}))
import PlaceNameMapping from '../PlaceNameMapping.vue'

describe('PlaceNameMapping', () => {
  const stubs = {
    ElDrawer: { template: '<div class="el-drawer"><slot /><slot name="footer" /></div>', props: ['modelValue'] },
    ElButton: { template: '<button><slot /></button>' },
    ElInput: { template: '<input />', props: ['modelValue'] },
    ElTable: { template: '<table><slot /></table>' },
    ElTableColumn: { template: '<col />' },
    ElPagination: { template: '<div />' },
    ElIcon: { template: '<i><slot /></i>' }
  }

  const defaultProps = {
    selectedData: { geoJson: JSON.stringify({ deMapping: { '北京': '北京' }, features: [] }) },
    themes: 'plain'
  }

  it('renders with required props', () => {
    const wrapper = shallowMount(PlaceNameMapping, {
      props: defaultProps,
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('exposes init method', () => {
    const wrapper = shallowMount(PlaceNameMapping, {
      props: defaultProps,
      global: { stubs }
    })
    expect(typeof (wrapper.vm as any).init).toBe('function')
  })

  it('renders drawer element', () => {
    const wrapper = shallowMount(PlaceNameMapping, {
      props: defaultProps,
      global: { stubs }
    })
    expect(wrapper.find('.el-drawer').exists()).toBe(true)
  })
})
