<!--
  注册页面
  用户注册入口
  (´；ω；`) 注册表单比登录复杂一点
-->
<template>
  <div class="register-view">
    <div class="auth-card">
      <div class="auth-header">
        <h1 class="auth-title">创建账号</h1>
        <p class="auth-subtitle">加入 SynthInk，开始你的创作之旅</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="auth-form"
        @keyup.enter="handleSubmit"
      >
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" size="large" :prefix-icon="User" />
        </el-form-item>

        <el-form-item prop="email">
          <el-input v-model="form.email" placeholder="邮箱" size="large" :prefix-icon="Message" />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="确认密码"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="submit-btn"
            :loading="authStore.loading"
            @click="handleSubmit"
          >
            注册
          </el-button>
        </el-form-item>
      </el-form>

      <div class="auth-footer">
        <p>
          已有账号？
          <router-link to="/auth/login" class="link">立即登录</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      const success = await authStore.register(form.username, form.email, form.password)
      if (success) {
        ElMessage.success('注册成功')
        router.push('/auth/login')
      } else {
        ElMessage.error('注册失败')
      }
    }
  })
}
</script>

<style scoped>
.register-view {
  width: 100%;
}

.auth-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: var(--space-2xl);
  backdrop-filter: blur(20px);
}

.auth-header {
  text-align: center;
  margin-bottom: var(--space-xl);
}

.auth-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--space-sm);
}

.auth-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
}

.auth-form :deep(.el-input__wrapper) {
  background: var(--bg-glass);
  box-shadow: none;
  border: 1px solid var(--border-color);
}

.auth-form :deep(.el-input__wrapper:hover) {
  border-color: var(--border-color-hover);
}

.auth-form :deep(.el-input__wrapper.is-focus) {
  border-color: var(--accent-primary);
}

.auth-form :deep(.el-input__inner) {
  color: var(--text-primary);
}

.auth-form :deep(.el-input__inner::placeholder) {
  color: var(--text-muted);
}

.submit-btn {
  width: 100%;
  background: var(--gradient-border);
  border: none;
  font-weight: 600;
  font-size: 16px;
}

.submit-btn:hover {
  box-shadow: var(--shadow-glow);
}

.auth-footer {
  text-align: center;
  margin-top: var(--space-lg);
  color: var(--text-secondary);
  font-size: 14px;
}

.link {
  color: var(--accent-primary);
  text-decoration: none;
  font-weight: 500;
}

.link:hover {
  text-decoration: underline;
}
</style>
