(function (global) {
  const admin = global.SquidAdmin || {};

  admin.defaultRoute = 'accounts';
  admin.menus = [
    {
      key: 'accounts',
      label: '账号管理',
      icon: 'el-icon-user',
      hash: '#/accounts',
      component: 'accounts-view',
    },
  ];

  admin.requestJson = async function requestJson(url, options = {}) {
    const response = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      ...options,
    });

    if (response.status === 401) {
      window.location.href = '/login';
      return null;
    }

    if (!response.ok) {
      let detail = '请求失败';
      try {
        const payload = await response.json();
        detail = payload.detail || detail;
      } catch (_) {}
      throw new Error(detail);
    }

    if (response.status === 204) return null;
    return response.json();
  };

  global.SquidAdmin = admin;
})(window);
