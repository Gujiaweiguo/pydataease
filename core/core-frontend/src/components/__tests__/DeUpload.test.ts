import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mockState = vi.hoisted(() => ({
  recordSnapshotCache: vi.fn(),
  uploadFileResult: vi.fn((file: unknown, cb: (url: string) => void) => {
    void file
    cb('uploaded-url')
  }),
  beforeUploadCheck: vi.fn(() => true),
  error: vi.fn()
}))

vi.mock('@/utils/imgUtils', () => ({
  imgUrlTrans: (url: string) => `preview:${url}`
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: mockState.recordSnapshotCache
  })
}))

vi.mock('@/api/staticResource', () => ({
  beforeUploadCheck: mockState.beforeUploadCheck,
  uploadFileResult: mockState.uploadFileResult
}))

vi.mock('element-plus-secondary', () => ({
  ElMessage: {
    error: mockState.error
  }
}))

import DeUpload from '@/components/visualization/common/DeUpload.vue'

const ElUploadStub = defineComponent({
  name: 'ElUpload',
  props: ['onPreview', 'onRemove', 'httpRequest', 'beforeUpload', 'fileList', 'effect'],
  template:
    '<div class="upload-stub" :data-file-count="String(fileList?.length || 0)"><slot /></div>'
})

const ImgViewDialogStub = defineComponent({
  name: 'ImgViewDialog',
  props: ['modelValue', 'imageUrl'],
  template:
    '<div class="img-view-dialog-stub" :data-visible="String(modelValue)" :data-image-url="imageUrl"></div>'
})

const mountComponent = (props: Record<string, unknown> = {}) =>
  mount(DeUpload, {
    props: {
      themes: 'dark',
      ...props
    },
    global: {
      stubs: {
        ElUpload: ElUploadStub,
        ElIcon: defineComponent({
          name: 'ElIcon',
          template: '<span class="el-icon-stub"><slot /></span>'
        }),
        Plus: defineComponent({ name: 'Plus', template: '<svg class="plus-icon"></svg>' }),
        ImgViewDialog: ImgViewDialogStub
      }
    }
  })

describe('DeUpload', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('initializes the file list from the provided image url', () => {
    const wrapper = mountComponent({ imgUrl: '/avatar.png' })
    const upload = wrapper.getComponent(ElUploadStub)

    expect(upload.props('fileList')).toEqual([{ url: 'preview:/avatar.png' }])
  })

  it('opens the preview dialog when preview is requested', async () => {
    const wrapper = mountComponent({ imgUrl: '/avatar.png' })
    const upload = wrapper.getComponent(ElUploadStub)

    upload.props('onPreview')?.({ url: 'preview:/avatar.png' })
    await wrapper.vm.$nextTick()

    expect(wrapper.getComponent(ImgViewDialogStub).props('modelValue')).toBe(true)
    expect(wrapper.getComponent(ImgViewDialogStub).props('imageUrl')).toBe('preview:/avatar.png')
  })

  it('clears the file list and emits onImgChange when removing a file', async () => {
    const wrapper = mountComponent({ imgUrl: '/avatar.png' })
    const upload = wrapper.getComponent(ElUploadStub)

    upload.props('onRemove')?.()
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('onImgChange')).toEqual([[]])
    expect(wrapper.getComponent(ElUploadStub).props('fileList')).toEqual([])
  })

  it('uploads a file, records a snapshot, and emits the new image url', async () => {
    const wrapper = mountComponent()
    const upload = wrapper.getComponent(ElUploadStub)

    upload.props('httpRequest')?.({ file: { name: 'avatar.png' } })
    await wrapper.vm.$nextTick()

    expect(mockState.uploadFileResult).toHaveBeenCalled()
    expect(mockState.recordSnapshotCache).toHaveBeenCalledWith('deUpload')
    expect(wrapper.emitted('onImgChange')).toEqual([['uploaded-url']])
  })

  it('shows an error when the re-uploaded file is larger than 15MB', async () => {
    const wrapper = mountComponent()
    const input = wrapper.get('input').element as HTMLInputElement

    Object.defineProperty(input, 'files', {
      value: [{ size: 16000000 }],
      configurable: true
    })

    await wrapper.get('input').trigger('change')

    expect(mockState.error).toHaveBeenCalledWith('图片大小不能超过15M')
  })
})
