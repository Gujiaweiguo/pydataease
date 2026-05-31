<script lang="ts" setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus-secondary'
import type { FormInstance, FormItemRule, FormRules } from 'element-plus-secondary'
import { useI18n } from '@/hooks/web/useI18n'
import {
  filingConfigList,
  filingSubmissionRetry,
  filingSubmissions,
  filingSubmit
} from '@/api/data-filing'
import type { FilingConfig, FilingSubmission, SubmissionStatus } from '@/api/data-filing'
import EmptyBackground from '@/components/empty-background/src/EmptyBackground.vue'

type BuilderFieldType =
  | 'input'
  | 'textarea'
  | 'number'
  | 'select'
  | 'radio'
  | 'checkbox'
  | 'date'
  | 'datetime'
  | 'email'
  | 'phone'
  | 'switch'

type FieldWidth = '25%' | '50%' | '75%' | '100%'
type FormFieldValue = string | number | boolean | string[] | null | undefined

interface FormBuilderOption {
  label: string
  value: string
}

interface FormBuilderField {
  id: string
  type: BuilderFieldType
  label: string
  fieldKey: string
  placeholder: string
  required: boolean
  maxLength?: number
  min?: number
  max?: number
  width: FieldWidth
  defaultValue: FormFieldValue
  options: FormBuilderOption[]
}

interface FormBuilderSchema {
  fields: FormBuilderField[]
}

interface FilingConfigWithStats extends FilingConfig {
  submitCount?: number | null
  submissionCount?: number | null
}

const { t } = useI18n()

const activeTab = ref<'forms' | 'submissions'>('forms')
const loading = ref(false)
const submissionsLoading = ref(false)
const submitting = ref(false)
const drawerVisible = ref(false)
const configs = ref<FilingConfigWithStats[]>([])
const submissions = ref<FilingSubmission[]>([])
const selectedConfig = ref<FilingConfigWithStats | null>(null)
const formRef = ref<FormInstance>()
const formModel = ref<Record<string, FormFieldValue>>({})

const phonePattern = /^[0-9+\-()\s]{6,20}$/

const fieldTypeSet = new Set<BuilderFieldType>([
  'input',
  'textarea',
  'number',
  'select',
  'radio',
  'checkbox',
  'date',
  'datetime',
  'email',
  'phone',
  'switch'
])

const widthSet = new Set<FieldWidth>(['25%', '50%', '75%', '100%'])

const readString = (value: unknown, fallback = '') => {
  return typeof value === 'string' ? value : fallback
}

const readNumber = (value: unknown) => {
  return typeof value === 'number' && Number.isFinite(value) ? value : undefined
}

const readBoolean = (value: unknown, fallback = false) => {
  return typeof value === 'boolean' ? value : fallback
}

const readFieldType = (value: unknown): BuilderFieldType => {
  return typeof value === 'string' && fieldTypeSet.has(value as BuilderFieldType)
    ? (value as BuilderFieldType)
    : 'input'
}

const readWidth = (value: unknown): FieldWidth => {
  return typeof value === 'string' && widthSet.has(value as FieldWidth)
    ? (value as FieldWidth)
    : '100%'
}

const readOptions = (value: unknown): FormBuilderOption[] => {
  if (!Array.isArray(value)) {
    return []
  }
  return value.map(option => {
    const normalized = option as Record<string, unknown>
    return {
      label: readString(normalized?.label),
      value: readString(normalized?.value)
    }
  })
}

const normalizeDefaultValue = (field: {
  type: BuilderFieldType
  defaultValue: unknown
}): FormFieldValue => {
  if (field.type === 'checkbox') {
    return Array.isArray(field.defaultValue)
      ? field.defaultValue.filter((item): item is string => typeof item === 'string')
      : []
  }
  if (field.type === 'switch') {
    return readBoolean(field.defaultValue)
  }
  if (field.type === 'number') {
    return readNumber(field.defaultValue)
  }
  if (typeof field.defaultValue === 'string') {
    return field.defaultValue
  }
  return field.type === 'date' || field.type === 'datetime' ? '' : ''
}

const normalizeSchema = (value?: Record<string, unknown> | null): FormBuilderSchema => {
  const rawFields = Array.isArray(value?.fields) ? value.fields : []
  return {
    fields: rawFields.map((field, index) => {
      const normalized = field as Record<string, unknown>
      const type = readFieldType(normalized?.type)
      return {
        id: readString(normalized?.id, `field_${index}`),
        type,
        label: readString(normalized?.label),
        fieldKey: readString(normalized?.fieldKey, `field_${index}`),
        placeholder: readString(normalized?.placeholder),
        required: readBoolean(normalized?.required),
        maxLength: readNumber(normalized?.maxLength),
        min: readNumber(normalized?.min),
        max: readNumber(normalized?.max),
        width: readWidth(normalized?.width),
        defaultValue: normalizeDefaultValue({
          type,
          defaultValue: normalized?.defaultValue
        }),
        options: readOptions(normalized?.options)
      }
    })
  }
}

const fields = computed(() => normalizeSchema(selectedConfig.value?.formSchema).fields)

const currentConfigName = computed(() => selectedConfig.value?.name || '-')

const columnSpan = (width: FieldWidth) => {
  const widthMap: Record<FieldWidth, number> = {
    '25%': 6,
    '50%': 12,
    '75%': 18,
    '100%': 24
  }
  return widthMap[width] || 24
}

const buildInitialModel = (schemaFields: FormBuilderField[]) => {
  const nextModel: Record<string, FormFieldValue> = {}
  schemaFields.forEach(field => {
    if (field.type === 'checkbox') {
      nextModel[field.fieldKey] = Array.isArray(field.defaultValue) ? [...field.defaultValue] : []
      return
    }
    nextModel[field.fieldKey] = field.defaultValue
  })
  return nextModel
}

const formRules = computed<FormRules>(() => {
  const nextRules: FormRules = {}
  fields.value.forEach(field => {
    const fieldRules: FormItemRule[] = []

    if (field.required && field.type !== 'switch') {
      fieldRules.push({
        required: true,
        type: field.type === 'checkbox' ? 'array' : 'string',
        message: `${field.label}${t('data_filing.form_builder.required')}`,
        trigger:
          field.type === 'select' || field.type === 'radio' || field.type === 'checkbox'
            ? 'change'
            : 'blur'
      })
    }

    if (field.maxLength !== undefined) {
      const maxLength = field.maxLength
      fieldRules.push({
        trigger: 'blur',
        validator: (_rule, value, callback) => {
          if (
            typeof value === 'string' &&
            typeof maxLength === 'number' &&
            value.length > maxLength
          ) {
            callback(new Error(t('data_filing.my_filing.max_length', [field.label, maxLength])))
            return
          }
          callback()
        }
      })
    }

    if (field.type === 'number' && (field.min !== undefined || field.max !== undefined)) {
      fieldRules.push({
        trigger: 'change',
        validator: (_rule, value, callback) => {
          if (value === null || value === undefined || value === '') {
            callback()
            return
          }
          if (typeof value !== 'number' || Number.isNaN(value)) {
            callback()
            return
          }
          if (field.min !== undefined && value < field.min) {
            callback(new Error(t('data_filing.my_filing.min_value', [field.label, field.min])))
            return
          }
          if (field.max !== undefined && value > field.max) {
            callback(new Error(t('data_filing.my_filing.max_value', [field.label, field.max])))
            return
          }
          callback()
        }
      })
    }

    if (field.type === 'email') {
      fieldRules.push({
        type: 'email',
        message: t('data_filing.my_filing.invalid_email'),
        trigger: 'blur'
      })
    }

    if (field.type === 'phone') {
      fieldRules.push({
        pattern: phonePattern,
        message: t('data_filing.my_filing.invalid_phone'),
        trigger: 'blur'
      })
    }

    if (fieldRules.length > 0) {
      nextRules[field.fieldKey] = fieldRules
    }
  })
  return nextRules
})

const statusTagType = (status: SubmissionStatus) => {
  const map: Record<SubmissionStatus, string> = {
    pending: 'warning',
    success: 'success',
    failed: 'danger',
    retrying: 'warning'
  }
  return map[status] || 'info'
}

const statusLabel = (status: SubmissionStatus) => {
  const map: Record<SubmissionStatus, string> = {
    pending: t('data_filing.submission_pending'),
    success: t('data_filing.submission_success'),
    failed: t('data_filing.submission_failed'),
    retrying: t('data_filing.submission_retrying')
  }
  return map[status] || status
}

const getSubmissionCount = (config: FilingConfigWithStats) => {
  if (typeof config.submitCount === 'number') {
    return String(config.submitCount)
  }
  if (typeof config.submissionCount === 'number') {
    return String(config.submissionCount)
  }
  return t('data_filing.my_filing.submit_count_unknown')
}

const loadConfigs = async () => {
  loading.value = true
  try {
    const res = await filingConfigList('published')
    const list = (res.data || []) as FilingConfigWithStats[]
    configs.value = list
    if (selectedConfig.value) {
      const nextSelected = list.find(item => item.id === selectedConfig.value?.id) || null
      selectedConfig.value = nextSelected
      if (!nextSelected) {
        submissions.value = []
      }
    }
  } finally {
    loading.value = false
  }
}

const loadSubmissions = async (filingId?: number) => {
  if (!filingId) {
    submissions.value = []
    return
  }
  submissionsLoading.value = true
  try {
    const res = await filingSubmissions(filingId)
    submissions.value = res.data || []
  } finally {
    submissionsLoading.value = false
  }
}

const selectConfig = async (config: FilingConfigWithStats) => {
  selectedConfig.value = config
  await loadSubmissions(config.id)
}

const openDrawer = async (config: FilingConfigWithStats) => {
  await selectConfig(config)
  drawerVisible.value = true
  await nextTick()
  formRef.value?.clearValidate()
}

const openHistory = async (config: FilingConfigWithStats) => {
  await selectConfig(config)
  activeTab.value = 'submissions'
}

const submitForm = async () => {
  if (!selectedConfig.value || !formRef.value) {
    return
  }
  await formRef.value.validate()
  submitting.value = true
  try {
    await filingSubmit(selectedConfig.value.id, formModel.value)
    ElMessage.success(t('data_filing.my_filing.submit_success'))
    drawerVisible.value = false
    activeTab.value = 'submissions'
    await loadSubmissions(selectedConfig.value.id)
    await loadConfigs()
  } catch (error) {
    ElMessage.error(t('data_filing.my_filing.submit_failed'))
  } finally {
    submitting.value = false
  }
}

const handleRetry = async (row: FilingSubmission) => {
  await filingSubmissionRetry(row.id)
  ElMessage.success(t('data_filing.retry_success'))
  await loadSubmissions(selectedConfig.value?.id)
}

watch(
  fields,
  value => {
    formModel.value = buildInitialModel(value)
  },
  { deep: true, immediate: true }
)

watch(drawerVisible, value => {
  if (!value) {
    formModel.value = buildInitialModel(fields.value)
    void nextTick(() => formRef.value?.clearValidate())
  }
})

onMounted(() => {
  void loadConfigs()
})
</script>

<template>
  <div class="my-filing-page">
    <div class="page-header">
      <p class="router-title">{{ t('data_filing.my_filing.title') }}</p>
    </div>

    <div class="page-shell">
      <el-tabs v-model="activeTab" class="page-tabs">
        <el-tab-pane :label="t('data_filing.my_filing.available_forms')" name="forms">
          <section class="panel-card forms-panel" v-loading="loading">
            <template v-if="configs.length > 0">
              <el-row :gutter="16">
                <el-col
                  v-for="config in configs"
                  :key="config.id"
                  :xs="24"
                  :sm="12"
                  :xl="8"
                  class="filing-card-col"
                >
                  <article class="filing-card">
                    <div class="filing-card__meta">
                      <span class="filing-card__eyebrow">
                        {{ t('data_filing.my_filing.filling_config') }}
                      </span>
                      <h3 class="filing-card__title">{{ config.name }}</h3>
                      <p class="filing-card__subtitle">
                        {{ t('data_filing.my_filing.target_table') }}：{{
                          config.targetTable || '-'
                        }}
                      </p>
                    </div>

                    <div class="filing-card__stats">
                      <div class="stat-item">
                        <span class="stat-item__label">
                          {{ t('data_filing.my_filing.submit_count') }}
                        </span>
                        <span class="stat-item__value">{{ getSubmissionCount(config) }}</span>
                      </div>
                      <div class="stat-item">
                        <span class="stat-item__label">ID</span>
                        <span class="stat-item__value">{{ config.id }}</span>
                      </div>
                    </div>

                    <div class="filing-card__actions">
                      <el-button secondary @click="openHistory(config)">
                        {{ t('data_filing.my_filing.view_history') }}
                      </el-button>
                      <el-button type="primary" @click="openDrawer(config)">
                        {{ t('data_filing.my_filing.fill') }}
                      </el-button>
                    </div>
                  </article>
                </el-col>
              </el-row>
            </template>
            <div v-else class="empty-wrap">
              <EmptyBackground
                img-type="noneWhite"
                :description="t('data_filing.my_filing.no_forms')"
              />
            </div>
          </section>
        </el-tab-pane>

        <el-tab-pane :label="t('data_filing.my_filing.my_submissions')" name="submissions">
          <section class="panel-card submissions-panel">
            <div class="submissions-header">
              <div>
                <p class="submissions-header__label">
                  {{ t('data_filing.my_filing.current_filing') }}
                </p>
                <h3 class="submissions-header__title">{{ currentConfigName }}</h3>
              </div>
            </div>

            <template v-if="selectedConfig">
              <el-table :data="submissions" border v-loading="submissionsLoading">
                <el-table-column prop="id" label="ID" min-width="140" />
                <el-table-column :label="t('data_filing.submission_status')" width="120">
                  <template #default="{ row }">
                    <el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column
                  prop="createTime"
                  :label="t('data_filing.my_filing.submit_time')"
                  min-width="180"
                />
                <el-table-column
                  prop="errorMessage"
                  :label="t('data_filing.my_filing.error')"
                  min-width="220"
                  show-overflow-tooltip
                />
                <el-table-column :label="t('common.operate')" width="120" fixed="right">
                  <template #default="{ row }">
                    <el-button
                      v-if="row.status === 'failed'"
                      link
                      type="primary"
                      @click="handleRetry(row)"
                    >
                      {{ t('data_filing.retry') }}
                    </el-button>
                  </template>
                </el-table-column>
                <template #empty>
                  <EmptyBackground
                    img-type="noneWhite"
                    :description="t('data_filing.my_filing.no_submissions')"
                  />
                </template>
              </el-table>
            </template>
            <div v-else class="empty-wrap empty-wrap--compact">
              <EmptyBackground
                img-type="noneWhite"
                :description="t('data_filing.my_filing.select_filing')"
              />
            </div>
          </section>
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-drawer
      v-model="drawerVisible"
      :title="selectedConfig?.name || t('data_filing.my_filing.filling_config')"
      size="680px"
      direction="rtl"
      append-to-body
    >
      <div class="drawer-content">
        <div class="drawer-intro">
          <p class="drawer-intro__label">{{ t('data_filing.my_filing.filling_config') }}</p>
          <h3 class="drawer-intro__title">{{ selectedConfig?.name }}</h3>
          <p class="drawer-intro__desc">
            {{ t('data_filing.my_filing.target_table') }}：{{ selectedConfig?.targetTable || '-' }}
          </p>
        </div>

        <el-scrollbar max-height="calc(100vh - 220px)">
          <el-form ref="formRef" :model="formModel" :rules="formRules" label-position="top">
            <el-row :gutter="16">
              <el-col v-for="field in fields" :key="field.id" :span="columnSpan(field.width)">
                <el-form-item
                  :label="field.label"
                  :prop="field.fieldKey"
                  :required="field.required"
                >
                  <el-input
                    v-if="
                      field.type === 'input' || field.type === 'email' || field.type === 'phone'
                    "
                    v-model="formModel[field.fieldKey]"
                    :maxlength="field.maxLength"
                    :placeholder="field.placeholder || t('common.please_input')"
                    show-word-limit
                  />
                  <el-input
                    v-else-if="field.type === 'textarea'"
                    v-model="formModel[field.fieldKey]"
                    :maxlength="field.maxLength"
                    :placeholder="field.placeholder || t('common.please_input')"
                    :rows="4"
                    type="textarea"
                    show-word-limit
                  />
                  <el-input-number
                    v-else-if="field.type === 'number'"
                    v-model="formModel[field.fieldKey]"
                    :min="field.min"
                    :max="field.max"
                    controls-position="right"
                    class="field-number"
                  />
                  <el-select
                    v-else-if="field.type === 'select'"
                    v-model="formModel[field.fieldKey]"
                    :placeholder="field.placeholder || t('common.please_select')"
                    clearable
                    class="field-full"
                  >
                    <el-option
                      v-for="option in field.options"
                      :key="option.value"
                      :label="option.label"
                      :value="option.value"
                    />
                  </el-select>
                  <el-radio-group
                    v-else-if="field.type === 'radio'"
                    v-model="formModel[field.fieldKey]"
                  >
                    <el-radio
                      v-for="option in field.options"
                      :key="option.value"
                      :label="option.value"
                    >
                      {{ option.label }}
                    </el-radio>
                  </el-radio-group>
                  <el-checkbox-group
                    v-else-if="field.type === 'checkbox'"
                    v-model="formModel[field.fieldKey]"
                  >
                    <el-checkbox
                      v-for="option in field.options"
                      :key="option.value"
                      :label="option.value"
                    >
                      {{ option.label }}
                    </el-checkbox>
                  </el-checkbox-group>
                  <el-date-picker
                    v-else-if="field.type === 'date'"
                    v-model="formModel[field.fieldKey]"
                    type="date"
                    value-format="YYYY-MM-DD"
                    :placeholder="field.placeholder || t('common.please_select')"
                    class="field-full"
                  />
                  <el-date-picker
                    v-else-if="field.type === 'datetime'"
                    v-model="formModel[field.fieldKey]"
                    type="datetime"
                    value-format="YYYY-MM-DD HH:mm:ss"
                    :placeholder="field.placeholder || t('common.please_select')"
                    class="field-full"
                  />
                  <el-switch
                    v-else-if="field.type === 'switch'"
                    v-model="formModel[field.fieldKey]"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-scrollbar>
      </div>

      <template #footer>
        <el-button secondary @click="drawerVisible = false">
          {{ t('data_filing.my_filing.form_closed') }}
        </el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">
          {{ t('data_filing.my_filing.submit') }}
        </el-button>
      </template>
    </el-drawer>
  </div>
</template>

<style lang="less" scoped>
.my-filing-page {
  --my-filing-space-1: 4px;
  --my-filing-space-2: 8px;
  --my-filing-space-3: 12px;
  --my-filing-space-4: 16px;
  --my-filing-space-5: 20px;
  --my-filing-space-6: 24px;
  --my-filing-space-7: 32px;
  --my-filing-radius-lg: 16px;
  --my-filing-radius-md: 12px;
  padding: var(--my-filing-space-4) var(--my-filing-space-6);
  font-family: var(--de-custom_font, 'PingFang');
}

.page-header {
  margin-bottom: var(--my-filing-space-4);
}

.router-title {
  margin: 0;
  color: var(--ed-text-color-primary, #1f2329);
  font-size: 24px;
  font-weight: 500;
  line-height: 32px;
}

.page-shell {
  display: flex;
  flex-direction: column;
  gap: var(--my-filing-space-4);
}

.panel-card {
  min-height: 320px;
  padding: var(--my-filing-space-5);
  border: 1px solid var(--ed-border-color-light, #dcdfe6);
  border-radius: var(--my-filing-radius-lg);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.88) 0%, rgba(248, 249, 252, 0.96) 100%),
    var(--ed-bg-color, #ffffff);
  box-shadow: 0 16px 40px rgba(31, 35, 41, 0.06);
}

.filing-card-col {
  margin-bottom: var(--my-filing-space-4);
}

.filing-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 220px;
  height: 100%;
  padding: var(--my-filing-space-5);
  border: 1px solid var(--ed-border-color-lighter, #ebeef5);
  border-radius: var(--my-filing-radius-md);
  background: radial-gradient(circle at top right, rgba(64, 158, 255, 0.12), transparent 36%),
    var(--ed-bg-color, #ffffff);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    border-color: var(--ed-color-primary-light-5, #79bbff);
    box-shadow: 0 20px 36px rgba(64, 158, 255, 0.12);
  }
}

.filing-card__meta {
  margin-bottom: var(--my-filing-space-5);
}

.filing-card__eyebrow,
.drawer-intro__label,
.submissions-header__label,
.stat-item__label {
  color: var(--ed-text-color-secondary, #8f959e);
  font-size: 12px;
  line-height: 20px;
}

.filing-card__title,
.drawer-intro__title,
.submissions-header__title {
  margin: var(--my-filing-space-2) 0 0;
  color: var(--ed-text-color-primary, #1f2329);
  font-size: 18px;
  font-weight: 500;
  line-height: 26px;
}

.filing-card__subtitle,
.drawer-intro__desc {
  margin: var(--my-filing-space-2) 0 0;
  color: var(--ed-text-color-regular, #606266);
  font-size: 14px;
  line-height: 22px;
}

.filing-card__stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--my-filing-space-3);
  margin-bottom: var(--my-filing-space-5);
}

.stat-item {
  padding: var(--my-filing-space-3);
  border-radius: var(--my-filing-radius-md);
  background: var(--ed-fill-color-lighter, #f5f7fa);
}

.stat-item__value {
  display: block;
  margin-top: var(--my-filing-space-1);
  color: var(--ed-text-color-primary, #1f2329);
  font-size: 16px;
  font-weight: 500;
  line-height: 24px;
}

.filing-card__actions,
.submissions-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--my-filing-space-3);
}

.drawer-content {
  display: flex;
  flex-direction: column;
  gap: var(--my-filing-space-5);
}

.drawer-intro {
  padding: var(--my-filing-space-4);
  border-radius: var(--my-filing-radius-md);
  background: var(--ed-fill-color-lighter, #f5f7fa);
}

.field-full,
.field-number {
  width: 100%;
}

.empty-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 320px;
}

.empty-wrap--compact {
  min-height: 240px;
}

:deep(.ed-checkbox-group),
:deep(.ed-radio-group) {
  display: flex;
  flex-wrap: wrap;
  gap: var(--my-filing-space-3);
}

:deep(.ed-table .ed-empty) {
  padding: var(--my-filing-space-6) 0;
}
</style>
