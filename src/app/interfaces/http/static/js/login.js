const REMEMBER_CREDENTIALS_KEY = 'squidManagerRememberedCredentials';
const loginForm = document.getElementById('loginForm');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const rememberPasswordInput = document.getElementById('rememberPassword');
const togglePasswordButton = document.getElementById('togglePassword');
const eyeIcon = document.getElementById('eyeIcon');
const loginButton = document.getElementById('loginButton');
const errorMessage = document.getElementById('errorMessage');
const captchaInput = document.getElementById('captcha');
const captchaImage = document.getElementById('captchaImage');
const refreshCaptchaButton = document.getElementById('refreshCaptcha');

function setError(message) {
  errorMessage.textContent = message;
  errorMessage.classList.add('show');
}

function clearError() {
  errorMessage.textContent = '';
  errorMessage.classList.remove('show');
}

function setPasswordVisible(visible) {
  passwordInput.type = visible ? 'text' : 'password';
  togglePasswordButton.classList.toggle('active', visible);
  togglePasswordButton.setAttribute('aria-pressed', String(visible));
  togglePasswordButton.setAttribute('aria-label', visible ? '隐藏密码' : '显示密码');
  eyeIcon.innerHTML = visible
    ? '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"></path><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"></path><path d="M14.12 14.12a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line>'
    : '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>';
}

function refreshCaptcha() {
  captchaImage.src = `/api/auth/captcha?t=${Date.now()}`;
  captchaInput.value = '';
}

function loadRememberedCredentials() {
  try {
    const saved = JSON.parse(localStorage.getItem(REMEMBER_CREDENTIALS_KEY) || 'null');
    if (!saved || typeof saved.username !== 'string' || typeof saved.password !== 'string') {
      return;
    }

    usernameInput.value = saved.username;
    passwordInput.value = saved.password;
    rememberPasswordInput.checked = true;
  } catch (_) {
    try {
      localStorage.removeItem(REMEMBER_CREDENTIALS_KEY);
    } catch (_) {}
  }
}

function saveRememberedCredentials(username, password) {
  try {
    if (!rememberPasswordInput.checked) {
      localStorage.removeItem(REMEMBER_CREDENTIALS_KEY);
      return;
    }

    localStorage.setItem(REMEMBER_CREDENTIALS_KEY, JSON.stringify({ username, password }));
  } catch (_) {
    // 本地存储不可用时不影响登录成功后的跳转。
  }
}

togglePasswordButton.addEventListener('click', () => {
  setPasswordVisible(passwordInput.type === 'password');
});

refreshCaptchaButton.addEventListener('click', () => {
  refreshCaptcha();
  captchaInput.focus();
});

loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  clearError();

  loginButton.disabled = true;
  loginButton.textContent = '登录中...';

  try {
    const username = usernameInput.value.trim();
    const password = passwordInput.value;
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    formData.append('captcha', captchaInput.value.trim());

    const response = await fetch('/api/auth/login', {
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      saveRememberedCredentials(username, password);
      window.location.href = '/admin#/accounts';
      return;
    }

    if (response.status === 400) {
      setError('验证码错误或已过期，请重新输入');
    } else {
      setError(response.status === 401 ? '账号或密码错误' : '登录失败，请稍后重试');
    }
    refreshCaptcha();
  } catch (_) {
    setError('网络异常，请稍后重试');
    refreshCaptcha();
  } finally {
    loginButton.disabled = false;
    loginButton.textContent = '登录';
  }
});

loadRememberedCredentials();
refreshCaptcha();
