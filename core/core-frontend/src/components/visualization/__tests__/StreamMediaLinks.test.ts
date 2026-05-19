import { defineComponent, nextTick, ref } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  curComponent: null as any,
  curActiveTabInner: null as any,
  recordSnapshotCache: vi.fn(),
  checkAddHttp: vi.fn((value: string) => (value.startsWith('http') ? value : `http://${value}`)),
  emitEvent: vi.fn()
}))

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: (store: Record<string, unknown>) => store
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => key })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    curComponent: mocks.curComponent,
    curActiveTabInner: mocks.curActiveTabInner
  })
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: mocks.recordSnapshotCache })
}))

vi.mock('@/utils/utils', () => ({
  checkAddHttp: mocks.checkAddHttp,
  deepCopy: (value: unknown) => JSON.parse(JSON.stringify(value))
}))

vi.mock('@/utils/eventBus', () => ({
  default: { emit: mocks.emitEvent }
}))

import StreamMediaLinks from '../StreamMediaLinks.vue'

const ElPopoverStub = defineComponent({
  name: 'ElPopover',
  data() {
    return { showPopper: true }
  },
  template:
    '<div class="popover-stub"><slot /><div class="reference"><slot name="reference" /></div></div>'
})

const stubs = {
  ElPopover: ElPopoverStub,
  ElRow: defineComponent({ name: 'ElRow', template: '<div><slot /></div>' }),
  ElForm: defineComponent({ name: 'ElForm', template: '<form><slot /></form>' }),
  ElFormItem: defineComponent({ name: 'ElFormItem', template: '<div><slot /></div>' }),
  ElRadioGroup: defineComponent({ name: 'ElRadioGroup', template: '<div><slot /></div>' }),
  ElRadio: defineComponent({
    name: 'ElRadio',
    props: ['label'],
    template: '<label><slot /></label>'
  }),
  ElInput: defineComponent({
    name: 'ElInput',
    props: ['modelValue'],
    emits: ['update:modelValue'],
    template:
      '<input class="input-stub" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />'
  }),
  ElButton: defineComponent({
    name: 'ElButton',
    emits: ['click'],
    template: '<button class="button-stub" @click="$emit(\'click\')"><slot /></button>'
  })
}

const baseLinkInfo = {
  videoType: 'flv',
  flv: { isLive: false, loop: true, url: 'media.example.com' }
}

const mountComponent = (props: Record<string, unknown> = {}) =>
  shallowMount(StreamMediaLinks, {
    props: {
      linkInfo: JSON.parse(JSON.stringify(baseLinkInfo)),
      ...props
    },
    global: { stubs }
  })

describe('StreamMediaLinks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.curComponent = ref({ id: 'view-1', streamMediaLinks: null })
    mocks.curActiveTabInner = ref({ streamMediaLinks: null })
  })

  it('renders playback loop controls for non-live flv streams', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('visualization.play_once')
    expect(wrapper.text()).toContain('visualization.play_circle')
    expect(wrapper.find('.input-stub').exists()).toBe(true)
  })

  it('hides playback frequency options for live streams', async () => {
    const wrapper = mountComponent({
      linkInfo: {
        videoType: 'flv',
        flv: { isLive: true, loop: false, url: 'live.example.com' }
      }
    })

    await nextTick()

    expect(wrapper.text()).not.toContain('visualization.play_once')
    expect(wrapper.text()).not.toContain('visualization.play_circle')
  })

  it('updates current component links, records snapshot and closes popover on submit', async () => {
    const wrapper = mountComponent()

    await wrapper.get('.input-stub').setValue('stream.dataease.cn/live.flv')
    await wrapper.findAll('.button-stub')[0].trigger('click')

    expect(mocks.checkAddHttp).toHaveBeenCalledWith('stream.dataease.cn/live.flv')
    expect(mocks.curComponent.value.streamMediaLinks.flv.url).toBe(
      'http://stream.dataease.cn/live.flv'
    )
    expect(mocks.recordSnapshotCache).toHaveBeenCalledWith('onSubmit')
    expect(mocks.emitEvent).toHaveBeenCalledWith('streamMediaLinksChange-view-1')
    expect(wrapper.getComponent(ElPopoverStub).vm.showPopper).toBe(false)
  })

  it('writes to active tab inner state and emits close on cancel', async () => {
    const wrapper = mountComponent({ attrPosition: 'tabInner' })

    await wrapper.get('.input-stub').setValue('tab.media.flv')
    await wrapper.findAll('.button-stub')[0].trigger('click')
    await wrapper.findAll('.button-stub')[1].trigger('click')

    expect(mocks.curActiveTabInner.value.streamMediaLinks.flv.url).toBe('http://tab.media.flv')
    expect(wrapper.emitted('close')).toEqual([[]])
    expect(wrapper.getComponent(ElPopoverStub).vm.showPopper).toBe(false)
  })
})
