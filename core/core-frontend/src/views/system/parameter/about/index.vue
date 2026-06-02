<template>
  <div class="appearance-settings" v-loading="loading">
    <el-form class="appearance-form" :model="form" label-width="140px" label-position="right">
      <el-form-item :label="t('system.about_bg')">
        <div class="appearance-upload-field">
          <div class="appearance-upload-actions">
            <el-upload
              action=""
              :show-file-list="false"
              :accept="uploadAccept"
              :before-upload="createImageBeforeUpload('ui.aboutBg')"
            >
              <el-button>{{
                form['ui.aboutBg'] ? t('system.replace_image') : t('common.add')
              }}</el-button>
            </el-upload>
            <el-button
              v-if="form['ui.aboutBg']"
              link
              type="danger"
              @click="clearImage('ui.aboutBg')"
            >
              {{ t('common.delete') }}
            </el-button>
          </div>
          <img
            v-if="form['ui.aboutBg']"
            class="appearance-upload-preview appearance-upload-preview--wide"
            :src="getImageSrc('ui.aboutBg')"
            :alt="t('system.about_bg')"
          />
        </div>
      </el-form-item>

      <el-form-item :label="t('system.about_logo')">
        <div class="appearance-upload-field">
          <div class="appearance-upload-actions">
            <el-upload
              action=""
              :show-file-list="false"
              :accept="uploadAccept"
              :before-upload="createImageBeforeUpload('ui.aboutLogo')"
            >
              <el-button>{{
                form['ui.aboutLogo'] ? t('system.replace_image') : t('common.add')
              }}</el-button>
            </el-upload>
            <el-button
              v-if="form['ui.aboutLogo']"
              link
              type="danger"
              @click="clearImage('ui.aboutLogo')"
            >
              {{ t('common.delete') }}
            </el-button>
          </div>
          <img
            v-if="form['ui.aboutLogo']"
            class="appearance-upload-preview"
            :src="getImageSrc('ui.aboutLogo')"
            :alt="t('system.about_logo')"
          />
          <div class="appearance-upload-tip">{{ t('system.about_logo_fallback_tip') }}</div>
        </div>
      </el-form-item>

      <el-divider />

      <el-form-item :label="t('system.about_edition')">
        <el-input v-model="form['about.edition']" />
      </el-form-item>

      <el-form-item :label="t('system.about_version')">
        <el-input v-model="form['about.version']" />
      </el-form-item>

      <el-form-item :label="t('system.about_corporation')">
        <el-input v-model="form['about.corporation']" />
      </el-form-item>

      <el-form-item :label="t('system.about_expired')">
        <el-input v-model="form['about.expired']" />
      </el-form-item>

      <el-form-item :label="t('system.about_count')">
        <el-input v-model="form['about.count']" type="number" />
      </el-form-item>

      <el-form-item :label="t('system.about_serial_no')">
        <el-input v-model="form['about.serialNo']" />
      </el-form-item>

      <el-form-item :label="t('system.about_remark')">
        <el-input v-model="form['about.remark']" />
      </el-form-item>

      <el-divider />

      <el-form-item :label="t('system.about_content')">
        <el-input v-model="form['ui.aboutContent']" type="textarea" :rows="4" />
      </el-form-item>
    </el-form>

    <div class="appearance-footer">
      <el-button type="primary" :loading="saving" @click="handleSave">{{
        t('common.sure')
      }}</el-button>
      <el-button @click="handleReset">{{ t('common.cancel') }}</el-button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus-secondary'
import request from '@/config/axios'
import { useI18n } from '@/hooks/web/useI18n'
import { beforeUploadCheck } from '@/api/staticResource'

const { t } = useI18n()

const basePath = import.meta.env.VITE_API_BASEPATH
const uploadAccept = '.png,.jpg,.jpeg,.svg,.gif'
const ABOUT_FORM_KEYS = [
  'ui.aboutBg',
  'ui.aboutContent',
  'ui.aboutLogo',
  'about.corporation',
  'about.expired',
  'about.count',
  'about.edition',
  'about.version',
  'about.serialNo',
  'about.remark'
]

const loading = ref(false)
const saving = ref(false)

const form = reactive<Record<string, string>>({
  'ui.aboutBg': '',
  'ui.aboutContent': '',
  'ui.aboutLogo': '',
  'about.corporation': '',
  'about.expired': '',
  'about.count': '',
  'about.edition': '',
  'about.version': '',
  'about.serialNo': '',
  'about.remark': ''
})

const readFileAsDataUrl = (file: File) =>
  new Promise<string>((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = event => {
      const result = event.target?.result
      if (typeof result === 'string') {
        resolve(result)
        return
      }
      reject(new Error('invalid image content'))
    }
    reader.onerror = () => {
      reject(reader.error || new Error('failed to read image'))
    }
    reader.readAsDataURL(file)
  })

const uploadImage = async (key: string, file: File) => {
  const content = await readFileAsDataUrl(file)
  const fileId = Date.now().toString()
  const res = await request.post({
    url: `/staticResource/upload/${fileId}`,
    data: { content }
  })
  form[key] = res.data?.id || fileId
}

const createImageBeforeUpload = (key: string) => async (file: File) => {
  if (!beforeUploadCheck(file)) {
    return false
  }

  try {
    await uploadImage(key, file)
  } catch (error) {
    console.error(error)
    ElMessage.error(t('system.contact_the_administrator'))
  }

  return false
}

const getImageSrc = (key: string) => {
  return form[key] ? `${basePath}/appearance/image/${form[key]}` : ''
}

const clearImage = (key: string) => {
  form[key] = ''
}

const syncForm = (data: Record<string, string>) => {
  ABOUT_FORM_KEYS.forEach(key => {
    form[key] = typeof data[key] === 'string' ? data[key] : ''
  })
}

const loadSettings = async () => {
  loading.value = true
  try {
    const res = await request.get({ url: '/sysParameter/appearance' })
    syncForm(res.data || {})
  } finally {
    loading.value = false
  }
}

const handleSave = async () => {
  saving.value = true
  try {
    await request.post({
      url: '/sysParameter/appearance/save',
      data: ABOUT_FORM_KEYS.map(key => ({ pkey: key, pval: form[key] || '' }))
    })
    ElMessage.success(t('common.save_success'))
    await loadSettings()
  } finally {
    saving.value = false
  }
}

const handleReset = async () => {
  await loadSettings()
}

onMounted(() => {
  loadSettings()
})
</script>

<style lang="less" scoped>
.appearance-settings {
  --appearance-space-1: 4px;
  --appearance-space-2: 8px;
  --appearance-space-3: 12px;
  --appearance-space-4: 16px;
  --appearance-space-5: 24px;
  display: flex;
  flex-direction: column;
  min-height: 100%;
  padding: var(--appearance-space-5);
  background: var(--ContentBG, #ffffff);
  border-radius: 12px;
}

.appearance-form {
  max-width: 720px;

  :deep(.ed-form-item:last-child) {
    margin-bottom: 0;
  }

  :deep(.ed-select),
  :deep(.ed-input),
  :deep(.ed-textarea) {
    width: 100%;
  }
}

.appearance-upload-field {
  display: flex;
  flex-direction: column;
  gap: var(--appearance-space-3);
}

.appearance-upload-actions {
  display: flex;
  align-items: center;
  gap: var(--appearance-space-3);
}

.appearance-upload-preview {
  width: 160px;
  max-width: 100%;
  height: 80px;
  border: 1px solid var(--ed-border-color-light, #dee0e3);
  border-radius: var(--ed-border-radius-base, 6px);
  object-fit: contain;
  background: var(--ContentBG, #ffffff);
}

.appearance-upload-preview--wide {
  width: 240px;
  object-fit: cover;
}

.appearance-upload-tip {
  color: var(--ed-text-color-secondary, #646a73);
  line-height: 20px;
}

.appearance-footer {
  display: flex;
  gap: var(--appearance-space-3);
  margin-top: auto;
  padding-top: var(--appearance-space-5);
}
</style>
