import { defineComponent } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/components/icon-group/field-list', () => ({
  iconFieldMap: {
    text: 'span',
    time: 'span',
    value: 'span',
    float: 'span',
    location: 'span',
    url: 'span'
  }
}))

const ElCascaderPanelStub = defineComponent({
  name: 'ElCascaderPanel',
  props: {
    modelValue: {
      type: Array,
      default: () => []
    },
    options: {
      type: Array,
      default: () => []
    }
  },
  emits: ['change', 'expand-change', 'update:modelValue'],
  template: `
    <div class="cascader-panel-stub">
      <button
        class="expand-trigger"
        type="button"
        @click="$emit('expand-change', { left: 2 })"
      />
      <button
        class="change-trigger"
        type="button"
        @click="$emit('update:modelValue', ['translateType', 'time', 'yyyy-MM-dd']); $emit('change')"
      />
      <slot :data="options[0] || {}" />
    </div>
  `
})

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => `t:${key}` })
}))

vi.mock('@/utils/attr', () => ({
  fieldType: ['text', 'time', 'value', 'float', 'value', 'location', 'binary', 'url']
}))

import FieldMore from '../form/FieldMore.vue'

const ElPopoverStub = defineComponent({
  name: 'ElPopover',
  props: {
    width: {
      type: Number,
      default: 175
    }
  },
  data() {
    return {
      hidden: false
    }
  },
  methods: {
    hide() {
      this.hidden = true
    }
  },
  template: `
    <div class="popover-stub" :data-width="String(width)" :data-hidden="String(hidden)">
      <slot name="reference" />
      <slot />
    </div>
  `
})

const ElIconStub = defineComponent({
  name: 'ElIcon',
  template: '<i class="icon-stub"><slot /></i>'
})

const IconStub = defineComponent({
  name: 'Icon',
  template: '<span class="custom-icon-stub"><slot /></span>'
})

const mountComponent = (props?: Record<string, unknown>) =>
  shallowMount(FieldMore, {
    props,
    global: {
      stubs: {
        ElCascaderPanel: ElCascaderPanelStub,
        ElIcon: ElIconStub,
        ElPopover: ElPopoverStub,
        Icon: IconStub
      }
    }
  })

describe('FieldMore', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('hides the editor option for non-extended fields', () => {
    const wrapper = mountComponent({ extField: 0, transType: 'Translate' })
    const options = wrapper.findComponent({ name: 'ElCascaderPanel' }).props('options') as Array<
      Record<string, string>
    >

    expect(options.map(option => option.value)).toEqual([
      'translate',
      'translateType',
      'rename',
      'copy',
      'delete'
    ])
  })

  it('reduces options to rename, copy, and delete for copied calculated fields', () => {
    const wrapper = mountComponent({ extField: 3, transType: 'Translate' })
    const options = wrapper.findComponent({ name: 'ElCascaderPanel' }).props('options') as Array<
      Record<string, string>
    >

    expect(options.map(option => option.value)).toEqual(['editor', 'rename', 'copy', 'delete'])
  })

  it('adds time-format children when showTime is enabled', () => {
    const wrapper = mountComponent({ extField: 2, showTime: true, transType: 'Translate' })
    const options = wrapper
      .findComponent({ name: 'ElCascaderPanel' })
      .props('options') as Array<any>
    const timeOption = options[1].children[1]

    expect(timeOption.value).toBe('time')
    expect(timeOption.children).toHaveLength(5)
    expect(timeOption.children[4].value).toBe('custom')
  })

  it('updates popover width and emits the selected command', async () => {
    const wrapper = mountComponent({ extField: 2, showTime: true, transType: 'Translate' })

    expect(wrapper.get('.popover-stub').attributes('data-width')).toBe('175')

    await wrapper.get('.expand-trigger').trigger('click')
    await wrapper.get('.change-trigger').trigger('click')

    expect(wrapper.get('.popover-stub').attributes('data-width')).toBe('525')
    expect(wrapper.get('.popover-stub').attributes('data-hidden')).toBe('true')
    expect(wrapper.emitted('handleCommand')).toEqual([['yyyy-MM-dd']])
  })
})
