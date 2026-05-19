import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (key: string) => key }) }))
vi.mock('@/models/chart/chart-senior', () => ({}))

import BubbleAnimateCfg from '../BubbleAnimateCfg.vue'

const globalStubs = {
  ElForm: {
    props: ['model', 'disabled'],
    template: '<form class="form-stub" :data-disabled="String(disabled)"><slot /></form>'
  },
  ElFormItem: { props: ['label'], template: '<div class="form-item-stub"><slot /></div>' },
  ElRow: { template: '<div class="row-stub"><slot /></div>' },
  ElCol: { props: ['span'], template: '<div class="col-stub"><slot /></div>' },
  ElSlider: { props: ['modelValue'], template: '<div class="slider-stub" />' },
  ElInput: { props: ['modelValue'], template: '<input class="input-stub" />' },
  ElRadioGroup: { props: ['modelValue'], template: '<div class="radio-group-stub"><slot /></div>' },
  ElRadio: { props: ['label'], template: '<label class="radio-stub"><slot /></label>' }
}

const createChart = (bubbleCfg = {}) => ({
  senior: {
    bubbleCfg: {
      enable: true,
      type: 'wave',
      speed: 1,
      rings: 2,
      ...bubbleCfg
    }
  }
})

const mountComponent = (chart = createChart()) =>
  shallowMount(BubbleAnimateCfg, {
    props: {
      chart,
      themes: 'dark'
    },
    global: {
      stubs: globalStubs
    }
  })

describe('BubbleAnimateCfg', () => {
  it('initializes bubbleAnimateForm from chart senior config', () => {
    const wrapper = mountComponent()

    expect((wrapper.vm as any).state.bubbleAnimateForm).toEqual({
      enable: true,
      type: 'wave',
      speed: 1,
      rings: 2
    })
  })

  it('disables the form when bubbleCfg.enable is false', () => {
    const wrapper = mountComponent(createChart({ enable: false }))

    expect(wrapper.get('.form-stub').attributes('data-disabled')).toBe('true')
  })

  it('clamps speed to minimum 0.1 when changeSpeedSize receives invalid input', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    vm.changeSpeedSize('abc')

    expect(vm.state.bubbleAnimateForm.speed).toBe(0.1)
  })

  it('clamps speed to maximum 5 when changeSpeedSize receives a value above 5', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    vm.changeSpeedSize('10')

    expect(vm.state.bubbleAnimateForm.speed).toBe(5)
  })

  it('clamps rings to minimum 0.1 when changeRingsSize receives zero', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    vm.changeRingsSize('0')

    expect(vm.state.bubbleAnimateForm.rings).toBe(0.1)
  })

  it('clamps rings to maximum 5 when changeRingsSize receives a value above 5', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    vm.changeRingsSize('99')

    expect(vm.state.bubbleAnimateForm.rings).toBe(5)
  })

  it('emits onBubbleAnimateChange with the current form state', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    vm.onBubbleAnimateChange()

    expect(wrapper.emitted('onBubbleAnimateChange')).toEqual([[vm.state.bubbleAnimateForm]])
  })
})
