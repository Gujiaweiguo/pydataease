<script lang="ts" setup>
import { computed, ref, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus-secondary'
import { useI18n } from '@/hooks/web/useI18n'

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
  defaultValue: string | number | boolean | string[]
  options: FormBuilderOption[]
}

interface FormBuilderSchema {
  fields: FormBuilderField[]
}

const props = defineProps<{
  modelValue: boolean
  schema?: Record<string, unknown>
}>()

const emit = defineEmits<{
  (event: 'update:modelValue', value: boolean): void
}>()

const { t } = useI18n()
const formRef = ref<FormInstance>()
const previewModel = ref<Record<string, unknown>>({})

const dialogVisible = computed({
  get: () => props.modelValue,
  set: value => emit('update:modelValue', value)
})

const normalizeSchema = (value?: Record<string, unknown>): FormBuilderSchema => {
  const fields = Array.isArray(value?.fields) ? value.fields : []
  return {
    fields: fields.map(field => field as FormBuilderField)
  }
}

const fields = computed(() => normalizeSchema(props.schema).fields)

const columnSpan = (width: FieldWidth) => {
  const widthMap: Record<FieldWidth, number> = {
    '25%': 6,
    '50%': 12,
    '75%': 18,
    '100%': 24
  }
  return widthMap[width] || 24
}

const rules = computed<FormRules>(() => {
  const nextRules: FormRules = {}
  fields.value.forEach(field => {
    const fieldRules = []
    if (field.required) {
      fieldRules.push({
        required: true,
        message: `${field.label}${t('data_filing.form_builder.required')}`,
        trigger: ['blur', 'change']
      })
    }
    if (field.type === 'email') {
      fieldRules.push({ type: 'email', message: 'Email format is invalid', trigger: 'blur' })
    }
    if (field.type === 'phone') {
      fieldRules.push({
        pattern: /^[0-9+\-()\s]{6,20}$/,
        message: 'Phone format is invalid',
        trigger: 'blur'
      })
    }
    if (fieldRules.length) {
      nextRules[field.fieldKey] = fieldRules
    }
  })
  return nextRules
})

watch(
  fields,
  value => {
    const nextModel: Record<string, unknown> = {}
    value.forEach(field => {
      if (field.type === 'checkbox') {
        nextModel[field.fieldKey] = Array.isArray(field.defaultValue) ? field.defaultValue : []
        return
      }
      nextModel[field.fieldKey] = field.defaultValue
    })
    previewModel.value = nextModel
  },
  { deep: true, immediate: true }
)

const submitPreview = async () => {
  await formRef.value?.validate().catch(() => undefined)
}
</script>

<template>
  <el-dialog
    v-model="dialogVisible"
    :title="t('data_filing.form_builder.preview')"
    width="720px"
    append-to-body
  >
    <div class="form-preview">
      <el-scrollbar max-height="560px">
        <el-form ref="formRef" :model="previewModel" :rules="rules" label-position="top">
          <el-row :gutter="16">
            <el-col v-for="field in fields" :key="field.id" :span="columnSpan(field.width)">
              <el-form-item :label="field.label" :prop="field.fieldKey" :required="field.required">
                <el-input
                  v-if="field.type === 'input' || field.type === 'email' || field.type === 'phone'"
                  v-model="previewModel[field.fieldKey]"
                  :maxlength="field.maxLength"
                  :placeholder="field.placeholder"
                />
                <el-input
                  v-else-if="field.type === 'textarea'"
                  v-model="previewModel[field.fieldKey]"
                  :maxlength="field.maxLength"
                  :placeholder="field.placeholder"
                  :rows="4"
                  type="textarea"
                />
                <el-input-number
                  v-else-if="field.type === 'number'"
                  v-model="previewModel[field.fieldKey]"
                  :min="field.min"
                  :max="field.max"
                  controls-position="right"
                  style="width: 100%"
                />
                <el-select
                  v-else-if="field.type === 'select'"
                  v-model="previewModel[field.fieldKey]"
                  :placeholder="field.placeholder"
                  clearable
                  style="width: 100%"
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
                  v-model="previewModel[field.fieldKey]"
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
                  v-model="previewModel[field.fieldKey]"
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
                  v-model="previewModel[field.fieldKey]"
                  type="date"
                  value-format="YYYY-MM-DD"
                  :placeholder="field.placeholder"
                  style="width: 100%"
                />
                <el-date-picker
                  v-else-if="field.type === 'datetime'"
                  v-model="previewModel[field.fieldKey]"
                  type="datetime"
                  value-format="YYYY-MM-DD HH:mm:ss"
                  :placeholder="field.placeholder"
                  style="width: 100%"
                />
                <el-switch
                  v-else-if="field.type === 'switch'"
                  v-model="previewModel[field.fieldKey]"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </el-scrollbar>
    </div>
    <template #footer>
      <el-button @click="dialogVisible = false">{{
        t('data_filing.form_builder.cancel')
      }}</el-button>
      <el-button type="primary" @click="submitPreview">
        {{ t('data_filing.form_builder.save') }}
      </el-button>
    </template>
  </el-dialog>
</template>

<style lang="less" scoped>
.form-preview {
  --preview-space-1: 4px;
  --preview-space-2: 8px;
  --preview-space-3: 12px;
  --preview-space-4: 16px;
  --preview-space-5: 20px;
  padding: var(--preview-space-1) 0;
  font-family: var(--de-custom_font, 'PingFang');
}

:deep(.ed-form-item) {
  margin-bottom: var(--preview-space-4);
}

:deep(.ed-checkbox-group),
:deep(.ed-radio-group) {
  display: flex;
  flex-wrap: wrap;
  gap: var(--preview-space-3);
}
</style>
