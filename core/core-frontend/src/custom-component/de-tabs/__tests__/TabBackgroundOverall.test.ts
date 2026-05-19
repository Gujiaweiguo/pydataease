import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: (store: Record<string, unknown>) => store
}))
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: vi.fn() })
}))
vi.mock('@/components/visualization/component-background/BackgroundOverallCommon.vue', () => ({
  default: {
    template: '<div class="bg-overall-common" />',
    props: ['themes', 'editPosition', 'commonBackgroundPop', 'componentPosition']
  }
}))

import TabBackgroundOverall from '../TabBackgroundOverall.vue'

const globalStubs = {
  'el-tabs': {
    template: '<div class="el-tabs"><slot /></div>',
    props: ['modelValue', 'effect', 'stretch']
  },
  'el-tab-pane': {
    template: '<div class="el-tab-pane"><slot /></div>',
    props: ['effect', 'label', 'name']
  },
  'el-checkbox': {
    template: '<input type="checkbox" class="el-checkbox" />',
    props: ['modelValue', 'effect', 'size']
  },
  'el-form-item': {
    template: '<div class="form-item"><slot /></div>',
    props: ['class']
  }
}

const createElement = () => ({
  titleBackground: {
    active: { color: '#fff' },
    inActive: { color: '#000' },
    multiply: false
  }
})

describe('de-tabs/TabBackgroundOverall.vue', () => {
  it('renders the component', () => {
    const wrapper = shallowMount(TabBackgroundOverall, {
      props: { element: createElement() },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders with dark themes class when themes is dark', () => {
    const wrapper = shallowMount(TabBackgroundOverall, {
      props: { element: createElement(), themes: 'dark' },
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.background-tabs-dark').exists()).toBe(true)
  })

  it('does not have dark class when themes is light', () => {
    const wrapper = shallowMount(TabBackgroundOverall, {
      props: { element: createElement(), themes: 'light' },
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.background-tabs-dark').exists()).toBe(false)
  })

  it('renders el-tabs component', () => {
    const wrapper = shallowMount(TabBackgroundOverall, {
      props: { element: createElement() },
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.el-tabs').exists()).toBe(true)
  })

  it('renders two el-tab-pane components', () => {
    const wrapper = shallowMount(TabBackgroundOverall, {
      props: { element: createElement() },
      global: { stubs: globalStubs }
    })
    expect(wrapper.findAll('.el-tab-pane').length).toBe(2)
  })

  it('has element prop with titleBackground', async () => {
    const el = createElement()
    shallowMount(TabBackgroundOverall, {
      props: { element: el },
      global: { stubs: globalStubs }
    })
    expect(el.titleBackground).toBeDefined()
  })
})
