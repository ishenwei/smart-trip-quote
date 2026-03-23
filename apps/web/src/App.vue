<template>
  <div class="layout">
    <!-- 导航栏 -->
    <header class="navbar">
      <div class="navbar-inner">
        <div class="brand">
          <span class="brand-icon">🌿</span>
          <span class="brand-name">Smart<em>Trip</em></span>
          <span class="brand-tag">智能旅行报价</span>
        </div>
        <nav class="nav-links">
          <a href="#">首页</a>
          <a href="#">行程管理</a>
          <a href="#">报价中心</a>
          <a href="#">关于我们</a>
        </nav>
      </div>
    </header>

    <!-- 英雄区 -->
    <section class="hero">
      <div class="hero-inner">
        <div class="hero-badge">
          <el-icon><MagicStick /></el-icon>
          AI 驱动 · 秒级响应
        </div>
        <h1 class="hero-title">
          旅行需求，<br />
          <em>一句话</em>搞定
        </h1>
        <p class="hero-subtitle">
          描述您的旅行计划，AI 自动解析需求、生成结构化数据，无缝对接报价系统
        </p>
        <div class="hero-stats">
          <div class="stat">
            <strong>5000+</strong>
            <span>已处理需求</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat">
            <strong>98%</strong>
            <span>识别准确率</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat">
            <strong>&lt; 5s</strong>
            <span>平均响应</span>
          </div>
        </div>
      </div>
      <div class="hero-decoration">
        <div class="deco-circle c1"></div>
        <div class="deco-circle c2"></div>
        <div class="deco-circle c3"></div>
      </div>
    </section>

    <!-- 主内容 -->
    <main class="main-content">
      <div class="content-wrap">

        <!-- 步骤指引 -->
        <div class="steps-card" v-if="!submissionSuccess">
          <el-steps :active="isSubmitting ? 1 : 0" simple finish-status="success">
            <el-step title="输入需求" icon="EditPen" />
            <el-step title="AI 解析" icon="MagicStick" />
            <el-step title="生成结果" icon="Document" />
          </el-steps>
        </div>

        <!-- 输入表单 -->
        <transition name="slide-fade">
          <section class="form-card" v-if="!submissionSuccess">
            <div class="card-header">
              <div class="card-header-left">
                <el-icon class="header-icon"><EditPen /></el-icon>
                <div>
                  <h2>描述旅行需求</h2>
                  <p>支持自然语言，越详细越准确</p>
                </div>
              </div>
              <el-tag type="success" effect="light" size="small">免费使用</el-tag>
            </div>

            <div class="example-chips">
              <span class="chips-label">快速示例：</span>
              <el-tag
                v-for="ex in examples"
                :key="ex.label"
                class="example-chip"
                @click="fillExample(ex.text)"
                effect="plain"
                type="success"
                size="small"
                style="cursor:pointer"
              >{{ ex.label }}</el-tag>
            </div>

            <el-form @submit.prevent="submitRequirement">
              <el-form-item>
                <el-input
                  v-model="userInput"
                  type="textarea"
                  :rows="8"
                  :maxlength="5000"
                  show-word-limit
                  :disabled="isSubmitting"
                  placeholder="例如：我想和家人从上海出发去云南丽江旅游，2个大人1个小孩，玩5天，总预算2万左右，希望住精品民宿，想体验当地特色美食和文化体验项目"
                  resize="none"
                  class="main-textarea"
                />
              </el-form-item>

              <div class="contact-fields">
                <el-form-item>
                  <el-input
                    v-model="contactName"
                    :disabled="isSubmitting"
                    placeholder="联系人姓名"
                    class="contact-input"
                  >
                    <template #prefix>
                      <el-icon><User /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
                <el-form-item>
                  <el-input
                    v-model="contactPhone"
                    :disabled="isSubmitting"
                    placeholder="联系电话"
                    class="contact-input"
                  >
                    <template #prefix>
                      <el-icon><Phone /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
                <el-form-item>
                  <el-input
                    v-model="contactEmail"
                    :disabled="isSubmitting"
                    placeholder="电子邮件地址"
                    class="contact-input"
                  >
                    <template #prefix>
                      <el-icon><Message /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </div>

              <el-alert
                v-if="errorMessage"
                :title="errorMessage"
                type="error"
                show-icon
                :closable="true"
                @close="errorMessage = ''"
                style="margin-bottom: 16px"
              />

              <div class="form-footer">
                <div class="form-tips">
                  <el-icon><InfoFilled /></el-icon>
                  包含出发地、目的地、日期、人数、预算信息可提升准确率
                </div>
                <div class="form-actions">
                  <el-button
                    @click="resetForm"
                    :disabled="isSubmitting || !userInput"
                    size="large"
                  >重置</el-button>
                  <el-button
                    type="primary"
                    native-type="submit"
                    :loading="isSubmitting"
                    :disabled="!isFormValid"
                    size="large"
                    class="submit-btn"
                    @click="submitRequirement"
                  >
                    <el-icon v-if="!isSubmitting"><Promotion /></el-icon>
                    {{ isSubmitting ? 'AI 解析中...' : '提交需求' }}
                  </el-button>
                </div>
              </div>
            </el-form>
          </section>
        </transition>

        <!-- 成功结果 -->
        <transition name="slide-fade">
          <section class="result-card" v-if="submissionSuccess">
            <div class="result-header">
              <div class="result-icon">
                <el-icon><CircleCheckFilled /></el-icon>
              </div>
              <div>
                <h2>需求已成功解析</h2>
                <p>AI 已完成需求识别，结构化数据已生成</p>
              </div>
            </div>

            <el-divider />

            <div class="result-meta" v-if="submissionResult">
              <div class="meta-grid">
                <div class="meta-item">
                  <label>需求编号</label>
                  <strong class="meta-value id-value">{{ submissionResult.requirement_id }}</strong>
                </div>
                <div class="meta-item" v-if="submissionResult.llm_info">
                  <label>AI 提供商</label>
                  <strong class="meta-value">{{ submissionResult.llm_info.provider }}</strong>
                </div>
                <div class="meta-item" v-if="submissionResult.llm_info">
                  <label>使用模型</label>
                  <strong class="meta-value">{{ submissionResult.llm_info.model }}</strong>
                </div>
              </div>
            </div>

            <div class="pending-message">
              <el-icon class="pending-icon"><MagicStick /></el-icon>
              <p>我们会尽快为您安排合适的行程并通知您！</p>
            </div>

            <div class="result-actions">
              <el-button type="primary" size="large" @click="resetSubmission" class="submit-btn">
                <el-icon><Plus /></el-icon>
                提交新需求
              </el-button>
              <el-button size="large" @click="goAdmin">
                <el-icon><Setting /></el-icon>
                进入管理后台
              </el-button>
            </div>
          </section>
        </transition>

      </div>
    </main>

    <!-- 特性栏 -->
    <section class="features" v-if="!submissionSuccess">
      <div class="content-wrap">
        <div class="features-grid">
          <div class="feature-item" v-for="f in features" :key="f.title">
            <span class="feature-icon">{{ f.icon }}</span>
            <h4>{{ f.title }}</h4>
            <p>{{ f.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-inner">
        <span class="brand-name-sm">🌿 SmartTrip</span>
        <span class="footer-divider">|</span>
        <span>智能旅行报价系统</span>
        <span class="footer-divider">|</span>
        <span>&copy; {{ new Date().getFullYear() }} 保留所有权利</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'

const userInput = ref('')
const contactName = ref('')
const contactPhone = ref('')
const contactEmail = ref('')
const isSubmitting = ref(false)
const submissionSuccess = ref(false)
const submissionResult = ref(null)
const errorMessage = ref('')

const isFormValid = computed(() => userInput.value.trim().length > 0)


const examples = [
  { label: '三亚家庭游', text: '从北京出发去三亚，2大1小，5天4晚，预算2万，住海景酒店，希望有亲子活动' },
  { label: '云南深度游', text: '上海出发去云南丽江大理，4人，7天，预算3万，喜欢文艺风格，住精品民宿' },
  { label: '东南亚蜜月', text: '广州出发去泰国清迈普吉，2人蜜月，10天，预算4万，需要浪漫行程安排' },
]

const features = [
  { icon: '🤖', title: 'AI 智能解析', desc: '多模型支持，精准识别出发地、目的地、预算、人数等关键信息' },
  { icon: '⚡', title: '秒级响应', desc: '平均 3-5 秒完成解析，高效处理大量旅行需求' },
  { icon: '📋', title: '结构化输出', desc: '自动生成标准化 JSON 数据，无缝对接报价和行程规划系统' },
  { icon: '🔒', title: '数据安全', desc: '全程加密传输，需求数据安全存储，符合数据合规要求' },
]

function fillExample(text) {
  userInput.value = text
}

async function submitRequirement() {
  if (!isFormValid.value) {
    errorMessage.value = '请输入旅游需求描述'
    return
  }

  isSubmitting.value = true
  errorMessage.value = ''

  try {
    const response = await axios.post('/api/llm/webhook/requirement/', {
      user_input: userInput.value,
      save_to_db: true,
      contact_name: contactName.value,
      contact_phone: contactPhone.value,
      contact_email: contactEmail.value,
    })

    if (response.data.success) {
      submissionSuccess.value = true
      submissionResult.value = response.data
    } else {
      errorMessage.value = response.data.error || '处理需求时出现错误'
    }
  } catch (error) {
    if (error.response) {
      errorMessage.value = `服务器错误 ${error.response.status}：${error.response.data.error || '处理失败'}`
    } else if (error.request) {
      errorMessage.value = '网络错误：无法连接到服务器，请检查网络连接'
    } else {
      errorMessage.value = '提交失败，请稍后重试'
    }
  } finally {
    isSubmitting.value = false
  }
}

function resetForm() {
  userInput.value = ''
  contactName.value = ''
  contactPhone.value = ''
  contactEmail.value = ''
  errorMessage.value = ''
}

function resetSubmission() {
  submissionSuccess.value = false
  submissionResult.value = null
  resetForm()
}

function goAdmin() {
  window.open('/admin/', '_blank')
}

</script>

<style scoped>
/* Layout */
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Navbar */
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.navbar-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-icon {
  font-size: 22px;
}

.brand-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.3px;
}

.brand-name em {
  font-style: normal;
  color: var(--color-primary);
}

.brand-tag {
  font-size: 11px;
  color: var(--color-text-muted);
  background: var(--color-border);
  padding: 2px 8px;
  border-radius: 20px;
  margin-left: 4px;
}

.nav-links {
  display: flex;
  gap: 28px;
}

.nav-links a {
  font-size: 14px;
  color: var(--color-text-muted);
  font-weight: 500;
  transition: var(--transition);
}

.nav-links a:hover {
  color: var(--color-primary);
}

/* Hero */
.hero {
  background: linear-gradient(135deg, #064e3b 0%, #065f46 50%, #047857 100%);
  color: #fff;
  padding: 72px 24px 80px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.hero-inner {
  max-width: 700px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 20px;
  padding: 6px 16px;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 24px;
  backdrop-filter: blur(4px);
}

.hero-title {
  font-size: clamp(2rem, 5vw, 3.2rem);
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: 20px;
  letter-spacing: -0.5px;
}

.hero-title em {
  font-style: normal;
  color: var(--color-accent-light);
}

.hero-subtitle {
  font-size: 16px;
  opacity: 0.85;
  max-width: 520px;
  margin: 0 auto 36px;
  line-height: 1.7;
}

.hero-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 28px;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat strong {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-accent-light);
}

.stat span {
  font-size: 12px;
  opacity: 0.75;
}

.stat-divider {
  width: 1px;
  height: 36px;
  background: rgba(255, 255, 255, 0.2);
}

/* Hero decorations */
.hero-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.c1 { width: 400px; height: 400px; top: -150px; right: -100px; }
.c2 { width: 250px; height: 250px; bottom: -80px; left: -60px; }
.c3 { width: 160px; height: 160px; top: 30px; left: 10%; }

/* Main content */
.main-content {
  flex: 1;
  padding: 40px 24px 60px;
}

.content-wrap {
  max-width: 780px;
  margin: 0 auto;
}

/* Steps card */
.steps-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  padding: 20px 28px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
}

/* Form card */
.form-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  padding: 32px;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-border);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.card-header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-icon {
  width: 42px;
  height: 42px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
  color: white;
  border-radius: 10px;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-header-left h2 {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 2px;
}

.card-header-left p {
  font-size: 13px;
  color: var(--color-text-muted);
}

/* Example chips */
.example-chips {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
}

.chips-label {
  font-size: 13px;
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.example-chip {
  transition: var(--transition) !important;
}

.example-chip:hover {
  background: var(--color-primary) !important;
  color: white !important;
  border-color: var(--color-primary) !important;
}

/* Textarea */
.main-textarea :deep(.el-textarea__inner) {
  border-color: var(--color-border) !important;
  background: #fafffe !important;
  font-size: 14.5px !important;
  line-height: 1.75 !important;
  padding: 14px 16px !important;
  color: var(--color-text) !important;
}

.main-textarea :deep(.el-textarea__inner::placeholder) {
  color: #aac8b8 !important;
}

.main-textarea :deep(.el-textarea__inner:focus) {
  border-color: var(--color-primary) !important;
  box-shadow: 0 0 0 2px rgba(5, 150, 105, 0.12) !important;
}

/* Form footer */
.form-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.form-tips {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--color-text-muted);
  line-height: 1.4;
  max-width: 360px;
}

.form-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.submit-btn {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark)) !important;
  border: none !important;
  font-weight: 600 !important;
  letter-spacing: 0.3px !important;
  padding: 0 28px !important;
}

.submit-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--color-primary-dark), var(--color-primary)) !important;
  box-shadow: 0 4px 16px rgba(5, 150, 105, 0.35) !important;
  transform: translateY(-1px) !important;
}

/* Result card */
.result-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  padding: 36px;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-border);
}

.result-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.result-icon {
  width: 52px;
  height: 52px;
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  color: var(--color-primary);
  flex-shrink: 0;
}

.result-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 4px;
}

.result-header p {
  font-size: 14px;
  color: var(--color-text-muted);
}

/* Meta grid */
.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.meta-item {
  background: var(--color-bg);
  border-radius: var(--radius-sm);
  padding: 14px 16px;
  border: 1px solid var(--color-border);
}

.meta-item label {
  display: block;
  font-size: 12px;
  color: var(--color-text-muted);
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.meta-value {
  font-size: 14px;
  color: var(--color-text);
  word-break: break-all;
}

.id-value {
  color: var(--color-primary);
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
}

/* Structured result */
.structured-result {
  background: #0d1117;
  border-radius: var(--radius-sm);
  overflow: hidden;
  margin-bottom: 28px;
}

.block-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  font-size: 13px;
  color: #8b949e;
  background: #161b22;
  border-bottom: 1px solid #30363d;
}

.json-block {
  padding: 20px;
  font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', monospace;
  font-size: 13px;
  line-height: 1.7;
  color: #e6edf3;
  overflow-x: auto;
  white-space: pre;
  max-height: 400px;
  overflow-y: auto;
}

.result-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* Contact fields */
.contact-fields {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.contact-fields .el-form-item {
  margin-bottom: 0;
}

.contact-input :deep(.el-input__wrapper) {
  border-color: var(--color-border) !important;
  background: #fafffe !important;
}

.contact-input :deep(.el-input__wrapper:hover) {
  border-color: var(--color-primary) !important;
}

.contact-input :deep(.el-input__wrapper.is-focus) {
  border-color: var(--color-primary) !important;
  box-shadow: 0 0 0 2px rgba(5, 150, 105, 0.12) !important;
}

/* Pending message */
.pending-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
  text-align: center;
  gap: 12px;
  margin-bottom: 28px;
}

.pending-icon {
  font-size: 36px;
  color: var(--color-primary);
}

.pending-message p {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text);
  letter-spacing: 0.3px;
}

/* Features section */
.features {
  background: var(--color-bg-card);
  border-top: 1px solid var(--color-border);
  padding: 48px 24px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 28px;
}

.feature-item {
  text-align: center;
}

.feature-icon {
  font-size: 32px;
  display: block;
  margin-bottom: 12px;
}

.feature-item h4 {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 8px;
}

.feature-item p {
  font-size: 13px;
  color: var(--color-text-muted);
  line-height: 1.6;
}

/* Footer */
.footer {
  background: #064e3b;
  color: rgba(255, 255, 255, 0.75);
  padding: 18px 24px;
}

.footer-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  font-size: 13px;
  flex-wrap: wrap;
}

.brand-name-sm {
  font-weight: 700;
  color: #ffffff;
}

.footer-divider {
  opacity: 0.3;
}

/* Transitions */
.slide-fade-enter-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-leave-active {
  transition: all 0.25s ease;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateY(16px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* Responsive */
@media (max-width: 640px) {
  .hero {
    padding: 48px 20px 56px;
  }

  .hero-title {
    font-size: 2rem;
  }

  .hero-stats {
    gap: 16px;
  }

  .nav-links {
    display: none;
  }

  .form-card, .result-card {
    padding: 20px;
  }

  .form-footer {
    flex-direction: column;
    align-items: stretch;
  }

  .form-actions {
    flex-direction: column;
  }

  .form-tips {
    max-width: 100%;
  }

  .result-actions {
    flex-direction: column;
  }

  .meta-grid {
    grid-template-columns: 1fr;
  }

  .contact-fields {
    grid-template-columns: 1fr;
  }
}
</style>
