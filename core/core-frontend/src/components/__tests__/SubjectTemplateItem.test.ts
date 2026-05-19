import { defineComponent, nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mockState = vi.hoisted(() => ({
  setCanvasStyle: vi.fn(),
  recordSnapshotCache: vi.fn(),
  emitterEmit: vi.fn(),
  adaptCurThemeCommonStyleAll: vi.fn(),
  confirm: vi.fn(() => Promise.resolve())
}))

const dvMainRefs = vi.hoisted(() => ({
  canvasStyleData: null as any
}))

vi.mock('@/assets/svg/dv-no-img.svg', () => ({
  default: defineComponent({
    name: 'DvNoImg',
    template: '<svg class="no-img"></svg>'
  })
}))

vi.mock('@/utils/imgUtils', () => ({
  imgUrlTrans: (url: string) => `transformed:${url}`
}))

vi.mock('@/utils/canvasStyle', () => ({
  adaptCurThemeCommonStyleAll: mockState.adaptCurThemeCommonStyleAll
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({ emitter: { emit: mockState.emitterEmit } })
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => key })
}))

vi.mock('pinia', () => ({
  storeToRefs: (store: Record<string, unknown>) => store
}))

vi.mock('@/store/modules/data-visualization/dvMain', async () => {
  const { ref } = await import('vue')
  const canvasStyleData = ref({ themeId: 'theme-a' })
  dvMainRefs.canvasStyleData = canvasStyleData

  return {
    dvMainStoreWithOut: () => ({
      canvasStyleData,
      setCanvasStyle: mockState.setCanvasStyle
    })
  }
})

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: mockState.recordSnapshotCache
  })
}))

vi.mock('element-plus-secondary', () => ({
  ElMessageBox: {
    confirm: mockState.confirm
  },
  ElTooltip: defineComponent({
    name: 'ElTooltip',
    template: '<div class="tooltip-stub"><slot /></div>'
  })
}))

import SubjectTemplateItem from '@/components/dashboard/subject-setting/pre-subject/SubjectTemplateItem.vue'

const mountComponent = (subjectItem: Record<string, unknown>) =>
  mount(SubjectTemplateItem, {
    props: { subjectItem },
    global: {
      mocks: {
        $t: (key: string) => key
      },
      stubs: {
        Icon: defineComponent({
          name: 'Icon',
          template: '<span class="icon-stub"><slot /></span>'
        }),
        ElButton: defineComponent({
          name: 'ElButton',
          emits: ['click'],
          template: '<button class="el-button-stub" @click="$emit(\'click\')"><slot /></button>'
        }),
        ElIcon: defineComponent({
          name: 'ElIcon',
          template: '<span class="el-icon-stub"><slot /></span>'
        }),
        Delete: defineComponent({ name: 'Delete', template: '<svg class="delete-icon"></svg>' }),
        EditPen: defineComponent({ name: 'EditPen', template: '<svg class="edit-icon"></svg>' })
      }
    }
  })

describe('SubjectTemplateItem', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    dvMainRefs.canvasStyleData.value = { themeId: 'theme-a' }
  })

  it('renders the transformed cover image when coverUrl exists', () => {
    const wrapper = mountComponent({
      id: '1',
      name: 'theme-name',
      coverUrl: '/cover.png',
      details: JSON.stringify({ themeId: 'theme-b', dashboard: {} }),
      type: 'public'
    })

    expect(wrapper.get('img').attributes('src')).toBe('transformed:/cover.png')
  })

  it('renders fallback artwork and selected styling for the active theme', () => {
    const wrapper = mountComponent({
      id: '1',
      name: 'theme-name',
      details: JSON.stringify({ themeId: 'theme-a', dashboard: {} }),
      type: 'public'
    })

    return nextTick().then(() => {
      expect(wrapper.find('.no-img').exists()).toBe(true)
      expect(wrapper.classes()).toContain('background-selected')
    })
  })

  it('applies a subject change when the template is not already selected', async () => {
    const wrapper = mountComponent({
      id: '1',
      name: 'theme-name',
      details: JSON.stringify({ themeId: 'theme-b', dashboard: {} }),
      type: 'public'
    })

    await wrapper.get('.vertical-layout').trigger('click')

    expect(mockState.setCanvasStyle).toHaveBeenCalledWith({
      themeId: 'theme-b',
      dashboard: { showGrid: false }
    })
    expect(mockState.recordSnapshotCache).toHaveBeenCalledWith('renderChart')
    expect(mockState.adaptCurThemeCommonStyleAll).toHaveBeenCalled()
    expect(mockState.emitterEmit).toHaveBeenCalledWith('onSubjectChange')
  })

  it('emits delete after the confirmation resolves', async () => {
    const wrapper = mountComponent({
      id: '9',
      name: 'self-theme',
      details: JSON.stringify({ themeId: 'theme-b', dashboard: {} }),
      type: 'self'
    })

    await wrapper.findAll('.el-button-stub')[0].trigger('click')
    await Promise.resolve()

    expect(wrapper.emitted('subjectDelete')).toEqual([['9']])
  })

  it('emits subjectEdit when the edit action is clicked', async () => {
    const wrapper = mountComponent({
      id: '9',
      name: 'self-theme',
      details: JSON.stringify({ themeId: 'theme-b', dashboard: {} }),
      type: 'self'
    })

    await wrapper.findAll('.el-button-stub')[1].trigger('click')

    expect(wrapper.emitted('subjectEdit')).toEqual([[]])
  })
})
