<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router_2'
import { authProviderCallback } from '@/api/auth-provider'
import { useUserStoreWithOut } from '@/store/modules/user'
import { usePermissionStoreWithOut } from '@/store/modules/permission'
import { useI18n } from '@/hooks/web/useI18n'
import { ElMessage } from 'element-plus-secondary'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const userStore = useUserStoreWithOut()
const loading = ref(true)
const errorMsg = ref('')

onMounted(async () => {
  const providerId = Number(route.params.providerId)
  const code = (route.query.code as string) || ''
  const state = (route.query.state as string) || ''

  if (!providerId || !code) {
    errorMsg.value = t('login.invalid_callback_params')
    loading.value = false
    return
  }

  const redirectUri = `${window.location.origin}/#/auth/callback/${providerId}`

  try {
    const res = await authProviderCallback(providerId, {
      code,
      state,
      redirect_uri: redirectUri
    })

    const { token, exp } = res.data
    userStore.setToken(token)
    userStore.setExp(exp)
    userStore.setTime(Date.now())

    const permissionStore = usePermissionStoreWithOut()
    permissionStore.clear()

    router.push({ path: '/workbranch/index' })
  } catch (err: any) {
    errorMsg.value = err?.response?.data?.detail || err?.message || t('login.auth_failed')
    loading.value = false
    ElMessage.error(errorMsg.value)
  }
})
</script>

<template>
  <div class="callback-container" v-loading="loading" :element-loading-text="t('login.logging_in')">
    <div v-if="errorMsg" class="callback-error">
      <p>{{ errorMsg }}</p>
      <el-button type="primary" @click="router.push('/login')">{{
        t('login.back_to_login')
      }}</el-button>
    </div>
  </div>
</template>

<style lang="less" scoped>
.callback-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f6f7;
}

.callback-error {
  text-align: center;
  color: #f56c6c;
  p {
    margin-bottom: 16px;
    font-size: 16px;
  }
}
</style>
