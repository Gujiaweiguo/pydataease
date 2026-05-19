import { defineComponent, h, reactive } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import CollapseSwitchItem from '../collapse-switch-item/src/CollapseSwitchItem.vue'

const emitSwitchClick = async (wrapper: ReturnType<typeof mount>, nextValue: boolean) => {
  const switchComponent = wrapper.getComponent(ElSwitchStub)

  switchComponent.vm.$emit('update:modelValue', nextValue)
  switchComponent.vm.$emit('click', new MouseEvent('click'))
  await wrapper.vm.$nextTick()
}

const ElSwitchStub = defineComponent({
  name: 'ElSwitch',
  props: {
    modelValue: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'click'],
  setup(props, { attrs, emit }) {
    return () =>
      h(
        'button',
        {
          class: 'switch-stub',
          style: attrs.style as string | undefined,
          onClick: () => {
            emit('update:modelValue', !props.modelValue)
            emit('click', new MouseEvent('click'))
          }
        },
        'switch'
      )
  }
})

const createMountOptions = () => {
  const collapseItemApi = reactive({
    isActive: false,
    handleHeaderClick: vi.fn(() => {
      collapseItemApi.isActive = !collapseItemApi.isActive
    })
  })

  const ElCollapseItemStub = defineComponent({
    name: 'ElCollapseItem',
    setup(_, { attrs, expose, slots }) {
      expose(collapseItemApi)

      return () =>
        h('div', { class: 'collapse-item-stub', ...attrs }, [
          h('div', { class: 'title-slot' }, slots.title?.()),
          h('div', { class: 'content-slot' }, slots.default?.())
        ])
    }
  })

  return {
    collapseItemApi,
    global: {
      stubs: {
        ElCollapseItem: ElCollapseItemStub,
        ElSwitch: ElSwitchStub
      }
    }
  }
}

describe('CollapseSwitchItem', () => {
  it('renders the title and slot content', () => {
    const mountOptions = createMountOptions()
    const wrapper = mount(CollapseSwitchItem, {
      props: {
        title: 'Advanced settings'
      },
      slots: {
        default: '<div class="panel-body">Body content</div>'
      },
      global: mountOptions.global
    })

    expect(wrapper.find('.title-slot').text()).toContain('Advanced settings')
    expect(wrapper.find('.panel-body').exists()).toBe(true)
  })

  it('hides the switch control when showSwitch is false', () => {
    const mountOptions = createMountOptions()
    const wrapper = mount(CollapseSwitchItem, {
      props: {
        showSwitch: false
      },
      global: mountOptions.global
    })

    expect(wrapper.get('.switch-stub').attributes('style')).toContain('display: none')
  })

  it('emits model update and modelChange when the switch is clicked', async () => {
    const changeModel = { id: 9 }
    const mountOptions = createMountOptions()
    const wrapper = mount(CollapseSwitchItem, {
      props: {
        modelValue: false,
        changeModel
      },
      global: mountOptions.global
    })

    await emitSwitchClick(wrapper, true)

    expect(wrapper.emitted('update:modelValue')).toEqual([[true]])
    expect(wrapper.emitted('modelChange')).toEqual([[changeModel]])
  })

  it('opens the collapse item when enabling an inactive panel', async () => {
    const mountOptions = createMountOptions()
    const wrapper = mount(CollapseSwitchItem, {
      props: {
        modelValue: false
      },
      global: mountOptions.global
    })

    await emitSwitchClick(wrapper, true)

    expect(mountOptions.collapseItemApi.handleHeaderClick).toHaveBeenCalledTimes(1)
    expect(mountOptions.collapseItemApi.isActive).toBe(true)
  })

  it('closes the collapse item when disabling an active panel', async () => {
    const mountOptions = createMountOptions()
    const wrapper = mount(CollapseSwitchItem, {
      props: {
        modelValue: true
      },
      global: mountOptions.global
    })

    mountOptions.collapseItemApi.isActive = true

    await emitSwitchClick(wrapper, false)

    expect(mountOptions.collapseItemApi.handleHeaderClick).toHaveBeenCalledTimes(1)
    expect(mountOptions.collapseItemApi.isActive).toBe(false)
  })
})
