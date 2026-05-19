import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({ dvInfo: { type: 'dashboard' }, mobileInPc: false })
}))
vi.mock('pinia', async (importOriginal) => {
  const actual = await importOriginal() as any
  return { ...actual, storeToRefs: () => ({ dvInfo: { value: { type: 'dashboard' } } }) }
})
vi.mock('@/utils/eventBus', () => ({ default: { on: vi.fn(), off: vi.fn(), emit: vi.fn() } }))

import TextSearch from '../TextSearch.vue'

const stubs = {
  'el-select': { template: '<select class="el-select-stub"><slot /></select>', props: ['modelValue', 'effect', 'popperClass'] },
  'el-option': { template: '<option><slot /></option>', props: ['label', 'value', 'key'] },
  'el-input': { template: '<input class="el-input-stub" />', props: ['modelValue', 'placeholder', 'style'] }
}

const defaultProvide = {
  placeholder: { value: { placeholderShow: true } },
  'com-width': () => 227,
  'is-confirm-search': () => undefined,
  '$custom-style-filter': { background: '#fff', border: '#ccc' }
}

const baseConfig = {
  id: 'test-text', conditionType: 0, queryConditionWidth: 0,
  conditionValueOperatorF: 'eq', conditionValueF: '', conditionValueOperatorS: 'like',
  conditionValueS: '', defaultConditionValueOperatorF: 'eq', defaultConditionValueF: '',
  defaultConditionValueOperatorS: 'like', defaultConditionValueS: '',
  hideConditionSwitching: false, placeholder: 'Search...'
}

const mountTextSearch = (configOverrides: Record<string, any> = {}) =>
  shallowMount(TextSearch, {
    props: { config: { ...baseConfig, ...configOverrides }, isConfig: false },
    global: { stubs, provide: defaultProvide }
  })

describe('TextSearch', () => {
  it('renders successfully with default props', () => { expect(mountTextSearch().exists()).toBe(true) })
  it('renders the text-search-select wrapper', () => { expect(mountTextSearch().find('.text-search-select').exists()).toBe(true) })
  it('shows operator select when hideConditionSwitching is false', () => {
    expect(mountTextSearch().findAll('.el-select-stub').length).toBeGreaterThanOrEqual(1)
  })
  it('renders second condition row when conditionType is 1', () => {
    expect(mountTextSearch({ conditionType: 1 }).findAll('.condition-type').length).toBe(2)
  })
  it('does not render second condition when conditionType is 0', () => {
    expect(mountTextSearch().findAll('.condition-type').length).toBe(1)
  })
})
