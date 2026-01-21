<template>
  <div class="app-container">
    <header class="app-header">
      <div class="container">
        <h1>旅游需求管理系统</h1>
        <p>轻松输入您的旅游需求，我们将为您提供专业的规划服务</p>
      </div>
    </header>
    
    <main class="app-main">
      <div class="container">
        <section class="input-section" v-if="!submissionSuccess">
          <h2>描述您的旅游需求</h2>
          <p class="section-description">请用自然语言详细描述您的旅游计划，包括出发地、目的地、出行时间、人数、预算等信息</p>
          
          <form @submit.prevent="submitRequirement" class="requirement-form">
            <div class="form-group">
              <label for="userInput">旅游需求描述</label>
              <textarea
                id="userInput"
                v-model="userInput"
                placeholder="例如：我想和家人从上海出发去三亚旅游，2个大人1个小孩，住4天，预算15000元左右，希望住海景房，有推荐的景点和美食"
                :maxlength="5000"
                class="input-textarea"
                :disabled="isSubmitting"
                aria-required="true"
              ></textarea>
              <div class="input-meta">
                <span class="char-count" :class="{ 'warning': userInput.length > 4000 }">
                  {{ userInput.length }}/5000
                </span>
                <span class="format-hint">请尽量详细描述您的需求，以获得更准确的规划</span>
              </div>
            </div>
            
            <div class="form-actions">
              <button
                type="submit"
                class="btn-submit"
                :disabled="isSubmitting || !isFormValid"
              >
                <span v-if="!isSubmitting">提交需求</span>
                <span v-else class="loading">
                  <span class="spinner"></span>
                  处理中...
                </span>
              </button>
              <button
                type="button"
                class="btn-reset"
                @click="resetForm"
                :disabled="isSubmitting"
              >
                重置
              </button>
            </div>
          </form>
          
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>
        </section>
        
        <section class="success-section" v-else>
          <div class="success-card">
            <div class="success-icon">✓</div>
            <h2>需求提交成功！</h2>
            <p>您的旅游需求已成功提交，我们将尽快为您处理。</p>
            
            <div class="result-info" v-if="submissionResult">
              <h3>处理结果</h3>
              <div class="result-item">
                <strong>需求ID：</strong>
                <span>{{ submissionResult.requirement_id }}</span>
              </div>
              <div class="result-item" v-if="submissionResult.llm_info">
                <strong>LLM提供商：</strong>
                <span>{{ submissionResult.llm_info.provider }}</span>
              </div>
              <div class="result-item" v-if="submissionResult.llm_info">
                <strong>使用模型：</strong>
                <span>{{ submissionResult.llm_info.model }}</span>
              </div>
            </div>
            
            <div class="structured-data" v-if="submissionResult && submissionResult.structured_data">
              <h3>结构化数据</h3>
              <pre>{{ formattedStructuredData }}</pre>
            </div>
            
            <button @click="resetSubmission" class="btn-primary">
              提交新需求
            </button>
          </div>
        </section>
      </div>
    </main>
    
    <footer class="app-footer">
      <div class="container">
        <p>&copy; {{ new Date().getFullYear() }} 旅游需求管理系统 | 专业、高效、安全</p>
      </div>
    </footer>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'App',
  data() {
    return {
      userInput: '',
      isSubmitting: false,
      submissionSuccess: false,
      submissionResult: null,
      errorMessage: '',
    };
  },
  computed: {
    isFormValid() {
      return this.userInput.trim().length > 0;
    },
    formattedStructuredData() {
      if (this.submissionResult && this.submissionResult.structured_data) {
        return JSON.stringify(this.submissionResult.structured_data, null, 2);
      }
      return '';
    },
  },
  methods: {
    async submitRequirement() {
      if (!this.isFormValid) {
        this.errorMessage = '请输入旅游需求描述';
        return;
      }
      
      this.isSubmitting = true;
      this.errorMessage = '';
      
      try {
        const response = await axios.post('/api/llm/process/', {
          user_input: this.userInput,
          save_to_db: true,
        });
        
        if (response.data.success) {
          this.submissionSuccess = true;
          this.submissionResult = response.data;
        } else {
          this.errorMessage = response.data.error || '处理需求时出现错误';
        }
      } catch (error) {
        console.error('提交需求失败:', error);
        if (error.response) {
          this.errorMessage = `服务器错误: ${error.response.status} - ${error.response.data.error || '处理失败'}`;
        } else if (error.request) {
          this.errorMessage = '网络错误: 无法连接到服务器，请检查网络连接';
        } else {
          this.errorMessage = '提交失败: 请稍后重试';
        }
      } finally {
        this.isSubmitting = false;
      }
    },
    
    resetForm() {
      this.userInput = '';
      this.errorMessage = '';
    },
    
    resetSubmission() {
      this.submissionSuccess = false;
      this.submissionResult = null;
      this.resetForm();
    },
  },
};
</script>

<style>
:root {
  --primary-color: #1e88e5;
  --primary-light: #42a5f5;
  --primary-dark: #1565c0;
  --secondary-color: #f5f5f5;
  --text-color: #333333;
  --text-light: #666666;
  --border-color: #e0e0e0;
  --success-color: #4caf50;
  --error-color: #f44336;
  --warning-color: #ff9800;
  --white: #ffffff;
  --shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  --transition: all 0.3s ease;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: var(--text-color);
  background-color: #f8f9fa;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 20px;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, var(--primary-dark), var(--primary-color));
  color: var(--white);
  padding: 40px 0;
  text-align: center;
  box-shadow: var(--shadow);
}

.app-header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  font-weight: 600;
}

.app-header p {
  font-size: 1.1rem;
  opacity: 0.9;
}

.app-main {
  flex: 1;
  padding: 40px 0;
}

.input-section {
  background-color: var(--white);
  border-radius: 8px;
  padding: 30px;
  box-shadow: var(--shadow);
}

.input-section h2 {
  font-size: 1.8rem;
  margin-bottom: 10px;
  color: var(--primary-dark);
}

.section-description {
  color: var(--text-light);
  margin-bottom: 25px;
  font-size: 1rem;
}

.requirement-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: var(--text-color);
  font-size: 0.95rem;
}

.input-textarea {
  width: 100%;
  min-height: 200px;
  padding: 15px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  transition: var(--transition);
}

.input-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.1);
}

.input-textarea:disabled {
  background-color: var(--secondary-color);
  cursor: not-allowed;
}

.input-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: var(--text-light);
  margin-top: 5px;
}

.char-count {
  font-weight: 500;
}

.char-count.warning {
  color: var(--warning-color);
}

.format-hint {
  font-style: italic;
}



.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 10px;
}

.btn-submit,
.btn-reset,
.btn-primary {
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
}

.btn-submit {
  background-color: var(--primary-color);
  color: var(--white);
  flex: 1;
}

.btn-submit:hover:not(:disabled) {
  background-color: var(--primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(30, 136, 229, 0.3);
}

.btn-submit:disabled {
  background-color: var(--border-color);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-reset {
  background-color: var(--secondary-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.btn-reset:hover:not(:disabled) {
  background-color: #e0e0e0;
}

.btn-primary {
  background-color: var(--primary-color);
  color: var(--white);
  margin-top: 20px;
}

.btn-primary:hover {
  background-color: var(--primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(30, 136, 229, 0.3);
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid var(--white);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background-color: rgba(244, 67, 54, 0.1);
  color: var(--error-color);
  padding: 12px;
  border-radius: 4px;
  margin-top: 15px;
  font-size: 0.95rem;
  border-left: 4px solid var(--error-color);
}

.success-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 500px;
}

.success-card {
  background-color: var(--white);
  border-radius: 8px;
  padding: 40px;
  box-shadow: var(--shadow);
  text-align: center;
  max-width: 600px;
  width: 100%;
}

.success-icon {
  width: 60px;
  height: 60px;
  background-color: var(--success-color);
  color: var(--white);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: bold;
  margin: 0 auto 20px;
}

.success-card h2 {
  font-size: 1.8rem;
  margin-bottom: 15px;
  color: var(--success-color);
}

.success-card p {
  color: var(--text-light);
  margin-bottom: 25px;
  font-size: 1.1rem;
}

.result-info {
  background-color: var(--secondary-color);
  border-radius: 4px;
  padding: 20px;
  margin-bottom: 20px;
  text-align: left;
}

.result-info h3 {
  font-size: 1.2rem;
  margin-bottom: 15px;
  color: var(--primary-dark);
}

.result-item {
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
}

.result-item strong {
  color: var(--text-color);
}

.structured-data {
  background-color: var(--secondary-color);
  border-radius: 4px;
  padding: 20px;
  margin-bottom: 20px;
  text-align: left;
}

.structured-data h3 {
  font-size: 1.2rem;
  margin-bottom: 15px;
  color: var(--primary-dark);
}

.structured-data pre {
  background-color: var(--text-color);
  color: var(--white);
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 0.9rem;
  line-height: 1.4;
}

.app-footer {
  background-color: var(--text-color);
  color: var(--white);
  padding: 20px 0;
  text-align: center;
  margin-top: 40px;
}

.app-footer p {
  font-size: 0.9rem;
  opacity: 0.8;
}

@media (max-width: 768px) {
  .app-header h1 {
    font-size: 2rem;
  }
  
  .app-main {
    padding: 20px 0;
  }
  
  .input-section {
    padding: 20px;
  }
  
  .input-section h2 {
    font-size: 1.5rem;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn-submit,
  .btn-reset {
    width: 100%;
  }
  
  .success-card {
    padding: 30px 20px;
  }
}

@media (max-width: 480px) {
  .app-header {
    padding: 30px 0;
  }
  
  .app-header h1 {
    font-size: 1.8rem;
  }
  
  .input-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .format-hint {
    order: -1;
  }
}
</style>
