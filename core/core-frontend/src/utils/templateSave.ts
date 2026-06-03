import { categoryTemplateNameCheck, nameCheck, save } from '@/api/template'
import { ElMessage, ElMessageBox } from 'element-plus-secondary'
import { buildTemplateExportInfo, toTemplateSavePayload } from '@/utils/imgUtils'

type SaveCanvasTemplateToLibraryParams = {
  canvasDom: HTMLElement
  name: string
  categoryId: string
  t: (key: string) => string
}

export async function saveCanvasTemplateToLibrary({
  canvasDom,
  name,
  categoryId,
  t
}: SaveCanvasTemplateToLibraryParams) {
  const templateInfo = await buildTemplateExportInfo('template', canvasDom, name, null)
  const templatePayload = toTemplateSavePayload(templateInfo, [categoryId])
  const nameCheckRequest = {
    pid: templatePayload.pid,
    name: templatePayload.name,
    categories: templatePayload.categories,
    optType: 'insert'
  }
  const persistTemplate = async (successMessage: string) => {
    await save(templatePayload)
    ElMessage.success(successMessage || t('commons.save_success'))
    return true
  }

  const categoryCheckResponse = await categoryTemplateNameCheck(nameCheckRequest)
  if (String(categoryCheckResponse?.data || '').indexOf('exist') > -1) {
    try {
      await ElMessageBox.confirm(t('template_manage.hint'), {
        tip: t('template_manage.cover_exists_hint'),
        confirmButtonType: 'danger',
        type: 'warning',
        autofocus: false,
        showClose: false
      })
    } catch {
      return false
    }
    return persistTemplate(t('template_manage.cover_success'))
  }

  const globalCheckResponse = await nameCheck(nameCheckRequest)
  if (String(globalCheckResponse?.data || '').indexOf('exist') > -1) {
    ElMessage.warning(t('template_manage.exists_name_hint'))
    return false
  }

  return persistTemplate(t('commons.save_success'))
}
