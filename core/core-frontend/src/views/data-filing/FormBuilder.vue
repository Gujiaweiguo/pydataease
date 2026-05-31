<script lang="ts" setup>
import {
  Check,
  CircleCheck,
  Clock,
  Delete,
  EditPen,
  List,
  Rank,
  Select,
  SetUp,
  Tickets
} from '@element-plus/icons-vue'
import { computed, ref, watch, type Component } from 'vue'
import draggable from 'vuedraggable'
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

interface PaletteItem {
  type: BuilderFieldType
  icon: Component
  label: string
}

const WIDTH_OPTIONS: FieldWidth[] = ['25%', '50%', '75%', '100%']
const OPTION_FIELD_TYPES: BuilderFieldType[] = ['select', 'radio', 'checkbox']
const TEXT_FIELD_TYPES: BuilderFieldType[] = ['input', 'textarea', 'email', 'phone']

const props = defineProps<{ modelValue?: Record<string, unknown> }>()

const emit = defineEmits<{
  (event: 'update:modelValue', value: FormBuilderSchema): void
}>()

const { t } = useI18n()

const activeSections = ref<string[]>(['basic', 'validation', 'options', 'appearance'])
const selectedFieldId = ref('')
const editingLabelId = ref('')
const draggingFieldType = ref<BuilderFieldType | ''>('')
const syncingFromProps = ref(false)
const schema = ref<FormBuilderSchema>({ fields: [] })

const fieldPalette = computed<PaletteItem[]>(() => [
  { type: 'input', icon: EditPen, label: t('data_filing.form_builder.fields.input') },
  { type: 'textarea', icon: Tickets, label: t('data_filing.form_builder.fields.textarea') },
  { type: 'number', icon: SetUp, label: t('data_filing.form_builder.fields.number') },
  { type: 'select', icon: Select, label: t('data_filing.form_builder.fields.select') },
  { type: 'radio', icon: CircleCheck, label: t('data_filing.form_builder.fields.radio') },
  { type: 'checkbox', icon: Check, label: t('data_filing.form_builder.fields.checkbox') },
  { type: 'date', icon: List, label: t('data_filing.form_builder.fields.date') },
  { type: 'datetime', icon: Clock, label: t('data_filing.form_builder.fields.datetime') },
  { type: 'email', icon: EditPen, label: t('data_filing.form_builder.fields.email') },
  { type: 'phone', icon: EditPen, label: t('data_filing.form_builder.fields.phone') },
  { type: 'switch', icon: SetUp, label: t('data_filing.form_builder.fields.switch') }
])

const widthOptions = computed(() => WIDTH_OPTIONS.map(value => ({ label: value, value })))

const selectedField = computed(() => {
  return schema.value.fields.find(field => field.id === selectedFieldId.value) || null
})

const getPaletteItem = (type: BuilderFieldType) => {
  return fieldPalette.value.find(item => item.type === type)
}

const getFieldIcon = (type: BuilderFieldType) => {
  return getPaletteItem(type)?.icon || EditPen
}

const getFieldLabel = (type: BuilderFieldType) => {
  return getPaletteItem(type)?.label || type
}

const cloneSchema = (value: FormBuilderSchema) => {
  return JSON.parse(JSON.stringify(value)) as FormBuilderSchema
}

const normalizeFieldKey = (value: string) => {
  return value
    .trim()
    .replace(/[^a-zA-Z0-9_]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .toLowerCase()
}

const buildOptionDefaults = () => [
  {
    label: `${t('data_filing.form_builder.default_option')} 1`,
    value: 'option_1'
  }
]

const buildDefaultPlaceholder = (type: BuilderFieldType) => {
  if (['select', 'radio', 'checkbox', 'date', 'datetime'].includes(type)) {
    return t('common.please_select')
  }
  if (type === 'switch') {
    return ''
  }
  return t('common.please_input')
}

const buildDefaultValue = (type: BuilderFieldType) => {
  if (type === 'number') {
    return 0
  }
  if (type === 'checkbox') {
    return []
  }
  if (type === 'switch') {
    return false
  }
  return ''
}

const buildUniqueFieldKey = (seed: string, currentId = '') => {
  const normalizedSeed = normalizeFieldKey(seed) || 'field'
  const takenKeys = new Set(
    schema.value.fields
      .filter(field => field.id !== currentId)
      .map(field => field.fieldKey)
      .filter(Boolean)
  )
  let nextKey = normalizedSeed
  let suffix = 1
  while (takenKeys.has(nextKey)) {
    suffix += 1
    nextKey = `${normalizedSeed}_${suffix}`
  }
  return nextKey
}

const normalizeField = (field: Partial<FormBuilderField>, index: number): FormBuilderField => {
  const rawType = field.type || 'input'
  const type = fieldPalette.value.some(item => item.type === rawType) ? rawType : 'input'
  const label = field.label?.trim() || `${getFieldLabel(type)} ${index + 1}`
  const fieldKey =
    typeof field.fieldKey === 'string' && field.fieldKey.trim()
      ? field.fieldKey.trim()
      : buildUniqueFieldKey(type)
  const width = WIDTH_OPTIONS.includes(field.width as FieldWidth)
    ? (field.width as FieldWidth)
    : '100%'
  const options = OPTION_FIELD_TYPES.includes(type)
    ? Array.isArray(field.options) && field.options.length
      ? field.options.map((option, optionIndex) => ({
          label:
            typeof option?.label === 'string' && option.label.trim()
              ? option.label
              : `${t('data_filing.form_builder.default_option')} ${optionIndex + 1}`,
          value:
            typeof option?.value === 'string' && option.value.trim()
              ? option.value
              : `option_${optionIndex + 1}`
        }))
      : buildOptionDefaults()
    : []

  return {
    id: typeof field.id === 'string' && field.id.trim() ? field.id : `field_${Date.now()}_${index}`,
    type,
    label,
    fieldKey,
    placeholder:
      typeof field.placeholder === 'string' ? field.placeholder : buildDefaultPlaceholder(type),
    required: Boolean(field.required),
    maxLength: typeof field.maxLength === 'number' ? field.maxLength : undefined,
    min: typeof field.min === 'number' ? field.min : undefined,
    max: typeof field.max === 'number' ? field.max : undefined,
    width,
    defaultValue: field.defaultValue !== undefined ? field.defaultValue : buildDefaultValue(type),
    options
  }
}

const normalizeSchema = (value?: Record<string, unknown>) => {
  const fields = Array.isArray(value?.fields) ? value.fields : []
  return {
    fields: fields.map((field, index) => normalizeField(field as Partial<FormBuilderField>, index))
  }
}

const selectField = (fieldId: string) => {
  selectedFieldId.value = fieldId
}

const syncSelection = () => {
  const hasSelected = schema.value.fields.some(field => field.id === selectedFieldId.value)
  if (!schema.value.fields.length) {
    selectedFieldId.value = ''
    editingLabelId.value = ''
    return
  }
  if (!hasSelected) {
    selectedFieldId.value = schema.value.fields[0].id
  }
}

const addField = (type: BuilderFieldType) => {
  const fieldIndex = schema.value.fields.length + 1
  const field: FormBuilderField = {
    id: `field_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
    type,
    label: `${getFieldLabel(type)} ${fieldIndex}`,
    fieldKey: buildUniqueFieldKey(type),
    placeholder: buildDefaultPlaceholder(type),
    required: false,
    width: '100%',
    defaultValue: buildDefaultValue(type),
    options: OPTION_FIELD_TYPES.includes(type) ? buildOptionDefaults() : []
  }
  schema.value.fields.push(field)
  selectField(field.id)
}

const removeField = (index: number) => {
  schema.value.fields.splice(index, 1)
  syncSelection()
}

const startLabelEdit = (fieldId: string) => {
  editingLabelId.value = fieldId
  selectField(fieldId)
}

const finishLabelEdit = (field: FormBuilderField) => {
  field.label = field.label.trim() || getFieldLabel(field.type)
  editingLabelId.value = ''
}

const addOption = () => {
  if (!selectedField.value) {
    return
  }
  const optionIndex = selectedField.value.options.length + 1
  selectedField.value.options.push({
    label: `${t('data_filing.form_builder.default_option')} ${optionIndex}`,
    value: `option_${optionIndex}`
  })
}

const removeOption = (index: number) => {
  if (!selectedField.value) {
    return
  }
  selectedField.value.options.splice(index, 1)
}

const updateFieldKey = (field: FormBuilderField) => {
  field.fieldKey = buildUniqueFieldKey(field.fieldKey || field.type, field.id)
}

const handlePaletteDragStart = (type: BuilderFieldType, event: DragEvent) => {
  draggingFieldType.value = type
  event.dataTransfer?.setData('text/plain', type)
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'copy'
  }
}

const handleCanvasDrop = (event: DragEvent) => {
  const fieldType = (event.dataTransfer?.getData('text/plain') || draggingFieldType.value) as
    | BuilderFieldType
    | ''
  if (!fieldType || !fieldPalette.value.some(item => item.type === fieldType)) {
    return
  }
  addField(fieldType)
  draggingFieldType.value = ''
}

const isOptionField = (type: BuilderFieldType) => OPTION_FIELD_TYPES.includes(type)
const isTextField = (type: BuilderFieldType) => TEXT_FIELD_TYPES.includes(type)
const isNumberField = (type: BuilderFieldType) => type === 'number'

watch(
  () => props.modelValue,
  value => {
    const nextSchema = normalizeSchema(value)
    if (JSON.stringify(nextSchema) === JSON.stringify(schema.value)) {
      syncSelection()
      return
    }
    syncingFromProps.value = true
    schema.value = nextSchema
    syncSelection()
    syncingFromProps.value = false
  },
  { deep: true, immediate: true }
)

watch(
  schema,
  value => {
    syncSelection()
    if (syncingFromProps.value) {
      return
    }
    emit('update:modelValue', cloneSchema(value))
  },
  { deep: true }
)
</script>

<template>
  <div class="form-builder">
    <section class="builder-panel palette-panel">
      <header class="panel-header">
        <span class="panel-title">{{ t('data_filing.form_builder.field_palette') }}</span>
      </header>
      <el-scrollbar class="panel-scrollbar">
        <div class="palette-list">
          <button
            v-for="item in fieldPalette"
            :key="item.type"
            class="palette-card"
            draggable="true"
            type="button"
            @click="addField(item.type)"
            @dragstart="handlePaletteDragStart(item.type, $event)"
          >
            <el-icon class="palette-card__icon">
              <component :is="item.icon" />
            </el-icon>
            <span class="palette-card__label">{{ item.label }}</span>
          </button>
        </div>
      </el-scrollbar>
    </section>

    <section
      class="builder-panel canvas-panel"
      @dragover.prevent
      @drop.prevent="handleCanvasDrop($event)"
    >
      <header class="panel-header">
        <span class="panel-title">{{ t('data_filing.form_builder.form_canvas') }}</span>
        <span class="panel-description">{{ schema.fields.length }}</span>
      </header>
      <el-scrollbar class="panel-scrollbar canvas-scrollbar">
        <div v-if="!schema.fields.length" class="canvas-empty">
          {{ t('data_filing.form_builder.empty_canvas_tip') }}
        </div>
        <draggable
          v-else
          v-model="schema.fields"
          item-key="id"
          handle=".field-card__handle"
          ghost-class="field-card--ghost"
          class="field-list"
        >
          <template #item="{ element, index }">
            <div
              class="field-card"
              :class="{ 'is-selected': selectedFieldId === element.id }"
              @click="selectField(element.id)"
            >
              <div class="field-card__handle">
                <el-icon>
                  <Rank />
                </el-icon>
              </div>
              <div class="field-card__body">
                <div class="field-card__title-row">
                  <el-icon class="field-card__type-icon">
                    <component :is="getFieldIcon(element.type)" />
                  </el-icon>
                  <el-input
                    v-if="editingLabelId === element.id"
                    v-model="element.label"
                    class="field-card__title-input"
                    size="small"
                    @blur="finishLabelEdit(element)"
                    @click.stop
                    @keyup.enter="finishLabelEdit(element)"
                  />
                  <button
                    v-else
                    class="field-card__title"
                    type="button"
                    @dblclick.stop="startLabelEdit(element.id)"
                  >
                    <span>{{ element.label }}</span>
                  </button>
                  <span v-if="element.required" class="field-card__required">*</span>
                </div>
                <div class="field-card__meta">{{ element.fieldKey }}</div>
              </div>
              <el-button
                class="field-card__delete"
                link
                type="danger"
                @click.stop="removeField(index)"
              >
                <el-icon>
                  <Delete />
                </el-icon>
              </el-button>
            </div>
          </template>
        </draggable>
      </el-scrollbar>
    </section>

    <section class="builder-panel config-panel">
      <header class="panel-header">
        <span class="panel-title">{{ t('data_filing.form_builder.field_config') }}</span>
      </header>
      <el-scrollbar class="panel-scrollbar">
        <div v-if="selectedField" class="config-content">
          <el-form :model="selectedField" label-position="top" size="small">
            <el-collapse v-model="activeSections" class="config-collapse">
              <el-collapse-item :title="t('data_filing.form_builder.basic')" name="basic">
                <el-form-item :label="t('data_filing.form_builder.label')">
                  <el-input v-model="selectedField.label" />
                </el-form-item>
                <el-form-item :label="t('data_filing.form_builder.field_key')">
                  <el-input
                    v-model="selectedField.fieldKey"
                    @blur="updateFieldKey(selectedField)"
                  />
                </el-form-item>
                <el-form-item
                  v-if="selectedField.type !== 'switch'"
                  :label="t('data_filing.form_builder.placeholder')"
                >
                  <el-input v-model="selectedField.placeholder" />
                </el-form-item>
                <el-form-item :label="t('data_filing.form_builder.default_value')">
                  <el-switch
                    v-if="selectedField.type === 'switch'"
                    v-model="selectedField.defaultValue"
                  />
                  <el-input-number
                    v-else-if="selectedField.type === 'number'"
                    v-model="selectedField.defaultValue"
                    controls-position="right"
                    style="width: 100%"
                  />
                  <el-select
                    v-else-if="selectedField.type === 'select' || selectedField.type === 'radio'"
                    v-model="selectedField.defaultValue"
                    clearable
                    style="width: 100%"
                  >
                    <el-option
                      v-for="option in selectedField.options"
                      :key="option.value"
                      :label="option.label"
                      :value="option.value"
                    />
                  </el-select>
                  <el-select
                    v-else-if="selectedField.type === 'checkbox'"
                    v-model="selectedField.defaultValue"
                    clearable
                    multiple
                    style="width: 100%"
                  >
                    <el-option
                      v-for="option in selectedField.options"
                      :key="option.value"
                      :label="option.label"
                      :value="option.value"
                    />
                  </el-select>
                  <el-input v-else v-model="selectedField.defaultValue" />
                </el-form-item>
              </el-collapse-item>

              <el-collapse-item :title="t('data_filing.form_builder.validation')" name="validation">
                <el-form-item :label="t('data_filing.form_builder.required')">
                  <el-switch v-model="selectedField.required" />
                </el-form-item>
                <el-form-item
                  v-if="isTextField(selectedField.type)"
                  :label="t('data_filing.form_builder.max_length')"
                >
                  <el-input-number
                    v-model="selectedField.maxLength"
                    :min="1"
                    controls-position="right"
                    style="width: 100%"
                  />
                </el-form-item>
                <el-form-item
                  v-if="isNumberField(selectedField.type)"
                  :label="t('data_filing.form_builder.min_value')"
                >
                  <el-input-number
                    v-model="selectedField.min"
                    controls-position="right"
                    style="width: 100%"
                  />
                </el-form-item>
                <el-form-item
                  v-if="isNumberField(selectedField.type)"
                  :label="t('data_filing.form_builder.max_value')"
                >
                  <el-input-number
                    v-model="selectedField.max"
                    controls-position="right"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-collapse-item>

              <el-collapse-item
                v-if="isOptionField(selectedField.type)"
                :title="t('data_filing.form_builder.options')"
                name="options"
              >
                <div class="option-list">
                  <div
                    v-for="(option, optionIndex) in selectedField.options"
                    :key="`${selectedField.id}_${optionIndex}`"
                    class="option-item"
                  >
                    <el-form-item :label="t('data_filing.form_builder.option_label')">
                      <el-input v-model="option.label" />
                    </el-form-item>
                    <el-form-item :label="t('data_filing.form_builder.option_value')">
                      <div class="option-item__value-row">
                        <el-input v-model="option.value" />
                        <el-button secondary @click="removeOption(optionIndex)">
                          {{ t('data_filing.form_builder.remove_option') }}
                        </el-button>
                      </div>
                    </el-form-item>
                  </div>
                </div>
                <el-button secondary class="option-add-button" @click="addOption">
                  {{ t('data_filing.form_builder.add_option') }}
                </el-button>
              </el-collapse-item>

              <el-collapse-item :title="t('data_filing.form_builder.appearance')" name="appearance">
                <el-form-item :label="t('data_filing.form_builder.width')">
                  <el-select v-model="selectedField.width" style="width: 100%">
                    <el-option
                      v-for="item in widthOptions"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value"
                    />
                  </el-select>
                </el-form-item>
              </el-collapse-item>
            </el-collapse>
          </el-form>
        </div>
        <div v-else class="canvas-empty">
          {{ t('data_filing.form_builder.empty_canvas_tip') }}
        </div>
      </el-scrollbar>
    </section>
  </div>
</template>

<style lang="less" scoped>
.form-builder {
  --builder-space-1: 4px;
  --builder-space-2: 8px;
  --builder-space-3: 12px;
  --builder-space-4: 16px;
  --builder-space-5: 20px;
  --builder-space-6: 24px;
  --builder-radius-sm: 8px;
  --builder-radius-md: 12px;
  --builder-panel-bg: var(--ed-bg-color, #ffffff);
  --builder-page-bg: var(--ed-fill-color-light, #f5f7fa);
  --builder-border: var(--ed-border-color-light, #dee0e3);
  --builder-border-strong: var(--ed-border-color, #d4d7de);
  --builder-text-primary: var(--ed-text-color-primary, #1f2329);
  --builder-text-regular: var(--ed-text-color-regular, #646a73);
  --builder-text-secondary: var(--ed-text-color-secondary, #8f959e);
  --builder-primary: var(--ed-color-primary, #3370ff);
  --builder-primary-light: var(--ed-color-primary-light-9, #eef4ff);
  --builder-danger: var(--ed-color-danger, #f56c6c);
  display: flex;
  gap: var(--builder-space-4);
  height: 560px;
  font-family: var(--de-custom_font, 'PingFang');
}

.builder-panel {
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: var(--builder-panel-bg);
  border: 1px solid var(--builder-border);
  border-radius: var(--builder-radius-md);
  box-shadow: 0 var(--builder-space-1) var(--builder-space-3) rgba(31, 35, 41, 0.04);
}

.palette-panel {
  width: 208px;
  flex: 0 0 208px;
}

.canvas-panel {
  flex: 1;
}

.config-panel {
  width: 288px;
  flex: 0 0 288px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--builder-space-4) var(--builder-space-4) var(--builder-space-3);
  border-bottom: 1px solid var(--builder-border);
}

.panel-title {
  color: var(--builder-text-primary);
  font-size: 14px;
  font-weight: 500;
  line-height: 22px;
}

.panel-description {
  color: var(--builder-text-secondary);
  font-size: 12px;
  line-height: 20px;
}

.panel-scrollbar {
  flex: 1;
  min-height: 0;
}

.palette-list,
.field-list,
.config-content {
  padding: var(--builder-space-4);
}

.palette-list {
  display: grid;
  gap: var(--builder-space-3);
}

.palette-card {
  display: flex;
  align-items: center;
  gap: var(--builder-space-3);
  width: 100%;
  padding: var(--builder-space-3);
  background: var(--builder-page-bg);
  border: 1px solid transparent;
  border-radius: var(--builder-radius-sm);
  color: var(--builder-text-primary);
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}

.palette-card:hover {
  border-color: var(--builder-primary);
  box-shadow: 0 var(--builder-space-2) var(--builder-space-4) rgba(51, 112, 255, 0.12);
  transform: translateY(calc(var(--builder-space-1) * -1));
}

.palette-card__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: calc(var(--builder-space-6) + var(--builder-space-2));
  height: calc(var(--builder-space-6) + var(--builder-space-2));
  border-radius: var(--builder-radius-sm);
  background: var(--builder-panel-bg);
  color: var(--builder-primary);
}

.palette-card__label {
  font-size: 14px;
  line-height: 22px;
}

.canvas-scrollbar {
  background: linear-gradient(180deg, rgba(255, 255, 255, 1) 0%, rgba(248, 250, 252, 1) 100%);
}

.canvas-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 160px;
  padding: var(--builder-space-6);
  color: var(--builder-text-secondary);
  font-size: 14px;
  line-height: 22px;
}

.field-list {
  display: grid;
  gap: var(--builder-space-3);
}

.field-card {
  display: flex;
  align-items: center;
  gap: var(--builder-space-3);
  padding: var(--builder-space-3) var(--builder-space-4);
  background: var(--builder-panel-bg);
  border: 1px solid var(--builder-border);
  border-left: var(--builder-space-1) solid transparent;
  border-radius: var(--builder-radius-sm);
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.field-card:hover {
  border-color: var(--builder-border-strong);
  box-shadow: 0 var(--builder-space-2) var(--builder-space-4) rgba(31, 35, 41, 0.06);
}

.field-card.is-selected {
  border-left-color: var(--builder-primary);
  background: var(--builder-primary-light);
}

.field-card--ghost {
  opacity: 0.6;
}

.field-card__handle,
.field-card__delete {
  color: var(--builder-text-secondary);
}

.field-card__handle {
  display: flex;
  align-items: center;
  cursor: grab;
}

.field-card__body {
  flex: 1;
  min-width: 0;
}

.field-card__title-row {
  display: flex;
  align-items: center;
  gap: var(--builder-space-2);
}

.field-card__type-icon {
  color: var(--builder-primary);
}

.field-card__title,
.field-card__title-input {
  flex: 1;
  min-width: 0;
}

.field-card__title {
  padding: 0;
  border: none;
  background: transparent;
  color: var(--builder-text-primary);
  font-size: 14px;
  font-weight: 500;
  line-height: 22px;
  text-align: left;
  cursor: text;
}

.field-card__title span {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.field-card__required {
  color: var(--builder-danger);
  font-size: 14px;
  line-height: 22px;
}

.field-card__meta {
  margin-top: var(--builder-space-1);
  color: var(--builder-text-secondary);
  font-size: 12px;
  line-height: 20px;
}

.config-collapse {
  border-top: none;
  border-bottom: none;
}

.option-list {
  display: grid;
  gap: var(--builder-space-3);
}

.option-item {
  padding: var(--builder-space-3);
  background: var(--builder-page-bg);
  border: 1px solid var(--builder-border);
  border-radius: var(--builder-radius-sm);
}

.option-item__value-row {
  display: flex;
  align-items: center;
  gap: var(--builder-space-2);
}

.option-add-button {
  width: 100%;
}

:deep(.ed-form-item) {
  margin-bottom: var(--builder-space-4);
}

:deep(.ed-collapse-item__wrap) {
  border-bottom: none;
}

:deep(.ed-collapse-item__header) {
  color: var(--builder-text-primary);
  font-size: 14px;
  font-weight: 500;
}
</style>
