import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/store/modules/appearance', () => ({
  useAppearanceStoreWithOut: () => ({ fontList: [] })
}))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    batchOptStatus: false,
    mobileInPc: false,
    canvasStyleData: {}
  })
}))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#000', '#fff'],
  CHART_FONT_FAMILY: [],
  CHART_FONT_LETTER_SPACE: [],
  DEFAULT_TITLE_STYLE: {
    show: true,
    fontSize: 16,
    color: '#000',
    hPosition: 'left',
    vPosition: 'top',
    isItalic: false,
    isBolder: true,
    fontFamily: '',
    letterSpacing: 0,
    fontShadow: false,
    remarkShow: false,
    remark: '',
    letterSpace: 0
  }
}))
vi.mock('lodash-es', () => ({
  cloneDeep: (v: any) => JSON.parse(JSON.stringify(v)),
  defaultsDeep: (target: any, ...sources: any[]) => Object.assign({}, ...sources, target)
}))
vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: (store: any) => ({
    batchOptStatus: { value: false },
    mobileInPc: { value: false }
  })
}))
vi.mock('@/components/icon-custom/src/Icon.vue', () => ({
  default: { template: '<span><slot /></span>' }
}))
vi.mock('@/assets/svg/icon_letter-spacing_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_bold_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_italic_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_left-alignment_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_center-alignment_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_right-alignment_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_edit_outlined.svg', () => ({ default: 'icon' }))

import TitleSelector from '../components/TitleSelector.vue'

const globalStubs = {
  ElForm: {
    template: '<form><slot /></form>',
    props: ['model', 'disabled', 'labelPosition', 'size']
  },
  ElFormItem: { template: '<div><slot /></div>', props: ['label', 'class'] },
  ElInput: {
    template: '<input />',
    props: ['modelValue', 'effect', 'maxlength', 'placeholder', 'clearable', 'type', 'autosize']
  },
  ElSelect: {
    template: '<select><slot /></select>',
    props: ['modelValue', 'effect', 'placeholder', 'size']
  },
  ElOption: { template: '<option><slot /></option>', props: ['key', 'label', 'value'] },
  ElColorPicker: { template: '<div />', props: ['modelValue', 'effect', 'predefine'] },
  ElCheckbox: {
    template: '<input type="checkbox" />',
    props: ['modelValue', 'effect', 'size', 'label']
  },
  ElRadioGroup: { template: '<div><slot /></div>', props: ['modelValue', 'effect'] },
  ElRadio: { template: '<label><slot /></label>', props: ['effect', 'label', 'value'] },
  ElSpace: { template: '<div><slot /></div>' },
  ElTooltip: {
    template: '<div><slot /><slot name="content" /></div>',
    props: ['content', 'effect', 'placement']
  },
  ElIcon: { template: '<i><slot /></i>', props: ['size'] },
  ElButton: { template: '<button><slot /></button>', props: ['text', 'effect', 'type'] },
  ElDialog: {
    template: '<div><slot /><slot name="footer" /></div>',
    props: ['title', 'visible', 'modelValue', 'width', 'closeOnClickModal']
  },
  Icon: { template: '<span><slot /></span>', props: ['name'] }
}

const defaultChart = () => ({
  title: 'My Chart',
  customStyle: {
    text: {
      show: true,
      fontSize: 16,
      color: '#000',
      hPosition: 'left',
      vPosition: 'top',
      isItalic: false,
      isBolder: true,
      fontFamily: '',
      letterSpace: 0,
      fontShadow: false,
      remarkShow: false,
      remark: ''
    }
  }
})

describe('TitleSelector', () => {
  it('renders with required props', () => {
    const wrapper = shallowMount(TitleSelector, {
      props: { chart: defaultChart(), themes: 'dark' },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('initializes titleForm from chart customStyle', () => {
    const wrapper = shallowMount(TitleSelector, {
      props: { chart: defaultChart(), themes: 'dark' },
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.state.titleForm.show).toBe(true)
    expect(vm.state.titleForm.fontSize).toBe(16)
  })

  it('computes toolTip as inverted theme', () => {
    const wrapper = shallowMount(TitleSelector, {
      props: { chart: defaultChart(), themes: 'dark' },
      global: { stubs: globalStubs }
    })
    expect((wrapper.vm as any).toolTip).toBe('light')
  })

  it('computes toolTip as dark for light theme', () => {
    const wrapper = shallowMount(TitleSelector, {
      props: { chart: defaultChart(), themes: 'light' },
      global: { stubs: globalStubs }
    })
    expect((wrapper.vm as any).toolTip).toBe('dark')
  })

  it('emits onTextChange when changeTitleStyle is called', () => {
    const wrapper = shallowMount(TitleSelector, {
      props: { chart: defaultChart(), themes: 'dark' },
      global: { stubs: globalStubs }
    })
    ;(wrapper.vm as any).changeTitleStyle('fontSize')
    expect(wrapper.emitted('onTextChange')).toBeTruthy()
  })

  it('fontSizeList contains expected range', () => {
    const wrapper = shallowMount(TitleSelector, {
      props: { chart: defaultChart(), themes: 'dark' },
      global: { stubs: globalStubs }
    })
    const list = (wrapper.vm as any).fontSizeList
    expect(list.length).toBeGreaterThan(0)
    expect(list[0].value).toBe(10)
  })
})
