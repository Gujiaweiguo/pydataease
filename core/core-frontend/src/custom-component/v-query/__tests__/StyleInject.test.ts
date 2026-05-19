import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({ dvInfo: { type: 'dashboard' }, mobileInPc: false })
}))
vi.mock('@/api/dataset', () => ({
  enumValueObj: () => Promise.resolve([]),
  getEnumValue: () => Promise.resolve([]),
  getFieldTree: () => Promise.resolve([])
}))
vi.mock('@/utils/eventBus', () => ({ default: { on: vi.fn(), off: vi.fn(), emit: vi.fn() } }))
vi.mock('@/hooks/web/useEmitt', () => ({ useEmitt: () => ({ emitter: { emit: vi.fn(), on: vi.fn() } }) }))
vi.mock('@/utils/color', () => ({ colorStringToHex: (c: string) => c }))
vi.mock('@/utils/utils', () => ({ isMobile: () => false }))
vi.mock('./shortcuts', () => ({ useShortcuts: () => ({ shortcuts: [] }) }))
vi.mock('vant/es/popup', () => ({ default: { template: '<div />' } }))
vi.mock('vant/es/popup/style', () => ({}))
vi.mock('vant/es/date-picker', () => ({ default: { template: '<div />' } }))
vi.mock('vant/es/date-picker/style', () => ({}))
vi.mock('vant/es/time-picker', () => ({ default: { template: '<div />' } }))
vi.mock('vant/es/time-picker/style', () => ({}))
vi.mock('vant/es/picker-group', () => ({ default: { template: '<div />' } }))
vi.mock('vant/es/picker-group/style', () => ({}))

import StyleInject from '../StyleInject.vue'

const stubs = {
  Select: { template: '<div class="select-stub" />', props: ['config', 'isConfig'] },
  Time: { template: '<div class="time-stub" />', props: ['config', 'isConfig'] },
  TextSearch: { template: '<div class="text-search-stub" />', props: ['config', 'isConfig'] },
  NumberInput: { template: '<div class="number-input-stub" />', props: ['config', 'isConfig'] },
  Tree: { template: '<div class="tree-stub" />', props: ['config', 'isConfig'] }
}

const defaultProvide = {
  'unmount-select': { value: [] },
  placeholder: { value: { placeholderShow: true } },
  'release-unmount-select': () => undefined,
  'query-data-for-id': () => undefined,
  'is-confirm-search': () => undefined,
  'com-width': () => 227,
  'cascade-list': () => undefined,
  'set-cascade-default': () => undefined,
  '$custom-style-filter': { background: '#fff', border: '#ccc' }
}

const baseConfig = {
  selectValue: '', defaultValue: '', displayType: '0', defaultValueCheck: false,
  optionValueSource: 0, multiple: false, checkedFieldsMap: {}, id: 'test-style',
  field: { id: 'f1' }, checkedFields: [], valueSource: [], displayFormat: 0, name: 'Test'
}

const mountStyleInject = (displayType = '0') =>
  shallowMount(StyleInject, {
    props: { config: { ...baseConfig, displayType }, customStyle: { border: '', background: '', text: '' } },
    global: { stubs, provide: defaultProvide, directives: { loading: () => undefined } }
  })

describe('StyleInject', () => {
  it('renders successfully', () => { expect(mountStyleInject().exists()).toBe(true) })
  it('renders Select for displayType 0', () => { expect(mountStyleInject('0').find('.select-stub').exists()).toBe(true) })
  it('renders Time for displayType 1', () => { expect(mountStyleInject('1').find('.time-stub').exists()).toBe(true) })
  it('renders TextSearch for displayType 8', () => { expect(mountStyleInject('8').find('.text-search-stub').exists()).toBe(true) })
  it('renders NumberInput for displayType 22', () => { expect(mountStyleInject('22').find('.number-input-stub').exists()).toBe(true) })
})
