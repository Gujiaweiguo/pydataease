import { defineComponent, nextTick } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const { tinymceInitMock, tinymceEditors, useEmittMock } = vi.hoisted(() => ({
  tinymceEditors: {} as Record<string, { insertContent: ReturnType<typeof vi.fn> }>,
  tinymceInitMock: vi.fn(),
  useEmittMock: vi.fn()
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: useEmittMock
}))

vi.mock('@/utils/url', () => ({
  formatDataEaseBi: (value: string) => value
}))

vi.mock('tinymce/tinymce', () => ({
  default: {
    editors: tinymceEditors,
    init: tinymceInitMock
  }
}))

vi.mock('@tinymce/tinymce-vue', () => ({
  default: defineComponent({
    name: 'Editor',
    props: {
      id: {
        type: String,
        default: ''
      },
      init: {
        type: Object,
        default: () => ({})
      },
      modelValue: {
        type: [String, Object],
        default: ''
      }
    },
    emits: ['update:modelValue'],
    template:
      '<div class="editor-stub" :data-editor-id="id" @click="$emit(\'update:modelValue\', \'updated from editor\')">{{ modelValue }}</div>'
  })
}))

vi.mock('tinymce/themes/silver/theme', () => ({}))
vi.mock('tinymce/icons/default', () => ({}))
vi.mock('tinymce/plugins/advlist', () => ({}))
vi.mock('tinymce/plugins/autolink', () => ({}))
vi.mock('tinymce/plugins/link', () => ({}))
vi.mock('tinymce/plugins/image', () => ({}))
vi.mock('tinymce/plugins/lists', () => ({}))
vi.mock('tinymce/plugins/charmap', () => ({}))
vi.mock('tinymce/plugins/media', () => ({}))
vi.mock('tinymce/plugins/wordcount', () => ({}))
vi.mock('tinymce/plugins/table', () => ({}))
vi.mock('tinymce/plugins/contextmenu', () => ({}))
vi.mock('tinymce/plugins/directionality', () => ({}))
vi.mock('tinymce/plugins/nonbreaking', () => ({}))
vi.mock('tinymce/plugins/pagebreak', () => ({}))

import TinymacEditorAlarm from '../TinymacEditorAlarm.vue'

type AlarmField = { deType: number; id: string; name: string; groupType: string }

const mountComponent = (fieldList?: AlarmField[]) =>
  shallowMount(TinymacEditorAlarm, {
    props: {
      modelValue: 'initial value',
      fieldList: fieldList ?? [
        { deType: 0, groupType: 'd', id: '1', name: 'Created At' },
        { deType: 2, groupType: 'q', id: '2', name: 'Amount' }
      ]
    },
    global: {
      stubs: {
        Editor: false
      }
    }
  })

describe('TinymacEditorAlarm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    Object.keys(tinymceEditors).forEach(key => {
      delete tinymceEditors[key]
    })
  })

  afterEach(() => {
    vi.runOnlyPendingTimers()
    vi.useRealTimers()
  })

  it('renders the editor and emits v-model updates from the child editor', async () => {
    const wrapper = mountComponent()
    const editor = wrapper.getComponent({ name: 'Editor' })

    expect(editor.props('id')).toBe('tinymce-view-alarm')

    editor.vm.$emit('update:modelValue', 'updated from editor')
    await nextTick()

    expect(wrapper.emitted('update:modelValue')).toEqual([['updated from editor']])
    expect(wrapper.emitted('change')).toEqual([['updated from editor']])
  })

  it('registers split button choices and inserts the selected field token', () => {
    const wrapper = mountComponent([{ deType: 0, groupType: 'd', id: '1', name: 'Created At' }])
    const init = wrapper.findComponent({ name: 'Editor' }).props('init') as Record<string, any>
    const addIcon = vi.fn()
    const addSplitButton = vi.fn()
    const insertContent = vi.fn()

    tinymceEditors['tinymce-view-alarm'] = { insertContent }

    init.setup({
      insertContent,
      ui: {
        registry: {
          addIcon,
          addSplitButton
        }
      }
    })

    const splitButtonConfig = addSplitButton.mock.calls[0][1]
    const callback = vi.fn()
    splitButtonConfig.fetch(callback)

    expect(addSplitButton).toHaveBeenCalledWith('splitDateButton', expect.any(Object))
    expect(callback).toHaveBeenCalledWith([
      {
        icon: 'icon_text_outlined',
        id: '1',
        text: 'Created At',
        type: 'choiceitem',
        value: 'Created At'
      }
    ])

    splitButtonConfig.onItemAction(null, 'Created At')

    expect(insertContent).toHaveBeenNthCalledWith(
      1,
      expect.stringContaining('background: #3370FF33;color: #2B5FD9')
    )
    expect(insertContent).toHaveBeenNthCalledWith(1, expect.stringContaining('[Created At]'))
    expect(insertContent).toHaveBeenNthCalledWith(2, '<span id="attachValue">&nbsp;</span>')
  })

  it('exposes viewInit and delegates editor bootstrap to tinymce', () => {
    const wrapper = mountComponent()

    ;(wrapper.vm as unknown as { viewInit: () => void }).viewInit()

    expect(tinymceInitMock).toHaveBeenCalledWith({})
  })

  it('registers the more-bar click listener on mount', () => {
    mountComponent()

    expect(useEmittMock).toHaveBeenCalledWith({
      name: 'moreBarElementClick',
      callback: expect.any(Function)
    })
  })
})
