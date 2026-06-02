<template>
  <div class="appearance-settings" v-loading="loading">
    <el-form class="appearance-form" :model="form" label-width="140px" label-position="right">
      <el-form-item :label="t('system.site_name')">
        <el-input v-model="form['basic.siteName']" />
      </el-form-item>

      <el-form-item :label="t('system.navigate_logo')">
        <div class="appearance-upload-field">
          <div class="appearance-upload-actions">
            <el-upload
              action=""
              :show-file-list="false"
              :accept="uploadAccept"
              :before-upload="createImageBeforeUpload('ui.navigate')"
            >
              <el-button>{{
                form['ui.navigate'] ? t('system.replace_image') : t('common.add')
              }}</el-button>
            </el-upload>
            <el-button
              v-if="form['ui.navigate']"
              link
              type="danger"
              @click="clearImage('ui.navigate')"
            >
              {{ t('common.delete') }}
            </el-button>
          </div>
          <img
            v-if="form['ui.navigate']"
            class="appearance-upload-preview"
            :src="getImageSrc('ui.navigate')"
            :alt="t('system.navigate_logo')"
          />
        </div>
      </el-form-item>

      <el-form-item :label="t('system.login_logo')">
        <div class="appearance-upload-field">
          <div class="appearance-upload-actions">
            <el-upload
              action=""
              :show-file-list="false"
              :accept="uploadAccept"
              :before-upload="createImageBeforeUpload('ui.login')"
            >
              <el-button>{{
                form['ui.login'] ? t('system.replace_image') : t('common.add')
              }}</el-button>
            </el-upload>
            <el-button v-if="form['ui.login']" link type="danger" @click="clearImage('ui.login')">
              {{ t('common.delete') }}
            </el-button>
          </div>
          <img
            v-if="form['ui.login']"
            class="appearance-upload-preview"
            :src="getImageSrc('ui.login')"
            :alt="t('system.login_logo')"
          />
        </div>
      </el-form-item>

      <el-form-item :label="t('system.theme_color')">
        <div class="appearance-color-field">
          <div class="appearance-color-options">
            <button
              type="button"
              class="appearance-color-option"
              :class="{ active: themePreset === 'default' }"
              @click="selectThemePreset('default')"
            >
              <span class="appearance-color-swatch appearance-color-swatch--default" />
              <span>{{ t('system.default_blue') }}</span>
            </button>

            <button
              type="button"
              class="appearance-color-option"
              :class="{ active: themePreset === 'custom' }"
              @click="selectThemePreset('custom')"
            >
              <span
                class="appearance-color-swatch"
                :style="{ backgroundColor: customThemeColor }"
              />
              <span>{{ t('system.custom_color_value') }}</span>
            </button>
          </div>

          <div v-if="themePreset === 'custom'" class="appearance-custom-picker">
            <el-color-picker
              v-model="customThemeColor"
              :predefine="predefineColors"
              @change="handleCustomColorChange"
            />
            <span class="appearance-custom-value">{{ customThemeColor }}</span>
          </div>
        </div>
      </el-form-item>

      <el-form-item :label="t('system.navigation_bar_style')">
        <el-select v-model="form['ui.navigationBarStyle']">
          <el-option
            v-for="option in navigationBarStyleOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item :label="t('system.login_title')">
        <el-input v-model="form['ui.loginTitle']" />
      </el-form-item>

      <el-form-item :label="t('system.login_subtitle')">
        <el-input v-model="form['ui.loginSubtitle']" />
      </el-form-item>

      <el-form-item :label="t('system.footer_text')">
        <el-input v-model="form['ui.footerText']" />
      </el-form-item>

      <el-form-item :label="t('system.footer_link')">
        <el-input v-model="form['ui.footerLink']" />
      </el-form-item>

      <el-form-item :label="t('system.help_link')">
        <el-input v-model="form['ui.helpLink']" />
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
import { COLOR_PANEL } from '@/views/chart/components/editor/util/chart'

const { t } = useI18n()

const DEFAULT_THEME_COLOR = '#3370FF'
const basePath = import.meta.env.VITE_API_BASEPATH
const uploadAccept = '.png,.jpg,.jpeg,.svg,.gif'
const APPEARANCE_FORM_KEYS = [
  'basic.siteName',
  'ui.navigate',
  'ui.login',
  'ui.themeColor',
  'ui.navigationBarStyle',
  'ui.loginTitle',
  'ui.loginSubtitle',
  'ui.footerText',
  'ui.footerLink',
  'ui.helpLink'
]
type ThemePreset = 'default' | 'custom'

const loading = ref(false)
const saving = ref(false)
const themePreset = ref<ThemePreset>('default')
const customThemeColor = ref(DEFAULT_THEME_COLOR)
const predefineColors = COLOR_PANEL

const navigationBarStyleOptions = [
  { label: t('chart.default'), value: 'default' },
  { label: t('system.dark_color'), value: 'dark' },
  { label: t('system.light_color'), value: 'light' }
] as const

const form = reactive<Record<string, string>>({
  'basic.siteName': '',
  'ui.navigate': '',
  'ui.login': '',
  'ui.themeColor': '',
  'ui.navigationBarStyle': 'default',
  'ui.loginTitle': '',
  'ui.loginSubtitle': '',
  'ui.footerText': '',
  'ui.footerLink': '',
  'ui.helpLink': ''
})

const applyThemeColor = () => {
  form['ui.themeColor'] = themePreset.value === 'custom' ? customThemeColor.value : ''
}

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
  APPEARANCE_FORM_KEYS.forEach(key => {
    form[key] = typeof data[key] === 'string' ? data[key] : ''
  })
  form['ui.navigationBarStyle'] = form['ui.navigationBarStyle'] || 'default'

  if (form['ui.themeColor']) {
    themePreset.value = 'custom'
    customThemeColor.value = form['ui.themeColor']
  } else {
    themePreset.value = 'default'
    customThemeColor.value = DEFAULT_THEME_COLOR
  }

  applyThemeColor()
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

const selectThemePreset = (preset: ThemePreset) => {
  themePreset.value = preset
  applyThemeColor()
}

const handleCustomColorChange = (color: string | null) => {
  customThemeColor.value = color || DEFAULT_THEME_COLOR
  applyThemeColor()
}

const handleSave = async () => {
  saving.value = true
  try {
    applyThemeColor()
    await request.post({
      url: '/sysParameter/appearance/save',
      data: APPEARANCE_FORM_KEYS.map(key => ({ pkey: key, pval: form[key] || '' }))
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
  :deep(.ed-input) {
    width: 100%;
  }
}

.appearance-color-field {
  display: flex;
  flex-direction: column;
  gap: var(--appearance-space-3);
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

.appearance-color-options {
  display: flex;
  flex-wrap: wrap;
  gap: var(--appearance-space-3);
}

.appearance-color-option {
  display: inline-flex;
  align-items: center;
  gap: var(--appearance-space-2);
  min-width: 140px;
  padding: var(--appearance-space-2) var(--appearance-space-3);
  border: 1px solid var(--ed-border-color-light, #dee0e3);
  border-radius: var(--ed-border-radius-base, 6px);
  background: var(--ContentBG, #ffffff);
  color: var(--ed-text-color-primary, #1f2329);
  cursor: pointer;
  transition: border-color 0.2s ease, background-color 0.2s ease, box-shadow 0.2s ease;

  &.active {
    border-color: var(--ed-color-primary, #3370ff);
    background: var(--ed-color-primary-1a, rgba(51, 112, 255, 0.1));
    box-shadow: 0 0 0 1px var(--ed-color-primary-1a, rgba(51, 112, 255, 0.1));
  }
}

.appearance-color-swatch {
  width: var(--appearance-space-4);
  height: var(--appearance-space-4);
  border: 1px solid var(--ed-border-color, #d9dcdf);
  border-radius: 999px;
  background: var(--ed-color-primary, #3370ff);
  flex-shrink: 0;
}

.appearance-color-swatch--default {
  background: var(--ed-color-primary, #3370ff);
}

.appearance-custom-picker {
  display: inline-flex;
  align-items: center;
  gap: var(--appearance-space-3);
}

.appearance-custom-value {
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
