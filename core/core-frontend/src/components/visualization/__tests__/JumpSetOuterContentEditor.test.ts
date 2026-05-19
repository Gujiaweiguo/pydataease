import { defineComponent } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  docContent: '',
  selectionFrom: 0,
  dispatch: vi.fn(),
  destroy: vi.fn(),
  mirror: null as any
}))

import JumpSetOuterContentEditor from '../JumpSetOuterContentEditor.vue'

const createMirror = () => {
  mocks.dispatch = vi.fn(payload => {
    if (payload?.changes?.insert !== undefined) {
      mocks.docContent = payload.changes.insert
    }
    if (payload?.selection?.anchor !== undefined) {
      mocks.selectionFrom = payload.selection.anchor
    }
  })
  mocks.destroy = vi.fn()
  mocks.mirror = {
    dispatch: mocks.dispatch,
    destroy: mocks.destroy,
    state: {
      doc: {
        toString: () => mocks.docContent
      }
    },
    viewState: {
      state: {
        doc: {
          get length() {
            return mocks.docContent.length
          }
        },
        selection: {
          ranges: [
            {
              get from() {
                return mocks.selectionFrom
              }
            }
          ]
        }
      }
    }
  }
  return mocks.mirror
}

const CodeMirrorStub = defineComponent({
  name: 'CodeMirror',
  props: ['quotaMap', 'domId'],
  methods: {
    codeComInit() {
      return createMirror()
    }
  },
  template: '<div class="code-mirror-stub" />'
})

const mountComponent = () => {
  const linkJumpInfo = { content: '' }
  const wrapper = shallowMount(JumpSetOuterContentEditor, {
    props: {
      linkJumpInfoArray: [
        { sourceFieldId: 'field_id', sourceFieldName: 'Field Name' },
        { sourceFieldId: 'city_id', sourceFieldName: 'City' }
      ],
      linkJumpInfo
    },
    global: { stubs: { CodeMirror: CodeMirrorStub } }
  })
  return { wrapper, linkJumpInfo }
}

describe('JumpSetOuterContentEditor', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    mocks.docContent = ''
    mocks.selectionFrom = 0
    mocks.mirror = null
  })

  it('passes source field names to code mirror quotaMap', () => {
    const { wrapper } = mountComponent()

    expect(wrapper.getComponent(CodeMirrorStub).props('quotaMap')).toEqual(['Field Name', 'City'])
  })

  it('initializes editor content with field names and syncs ids back on interval', () => {
    const { wrapper, linkJumpInfo } = mountComponent()

    ;(wrapper.vm as any).editorInit('jump to [field_id] and [city_id]')

    expect(mocks.dispatch).toHaveBeenCalledWith({
      changes: {
        from: 0,
        to: 0,
        insert: 'jump to [Field Name] and [City]'
      }
    })

    vi.advanceTimersByTime(1500)

    expect(linkJumpInfo.content).toBe('jump to [field_id] and [city_id]')
  })

  it('inserts content at the current cursor position', () => {
    const { wrapper } = mountComponent()
    ;(wrapper.vm as any).editorInit('')
    mocks.selectionFrom = 4
    ;(wrapper.vm as any).insertFieldToCodeMirror('[Field Name]')

    expect(mocks.dispatch).toHaveBeenLastCalledWith({
      changes: { from: 4, insert: '[Field Name]' },
      selection: { anchor: 4 }
    })
  })

  it('clears timer and destroys mirror on unmount', () => {
    const { wrapper } = mountComponent()
    ;(wrapper.vm as any).editorInit('[field_id]')

    wrapper.unmount()

    expect(mocks.destroy).toHaveBeenCalled()
  })
})
