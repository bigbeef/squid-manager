(function (global) {
  const admin = global.SquidAdmin;

  new Vue({
    el: '#admin-app',
    data() {
      return {
        menus: admin.menus,
        currentKey: admin.defaultRoute,
      };
    },
    computed: {
      currentMenu() {
        return this.menus.find((item) => item.key === this.currentKey) || this.menus[0];
      },
      currentComponent() {
        return this.currentMenu.component;
      },
    },
    created() {
      this.syncRoute();
      window.addEventListener('hashchange', this.syncRoute);
    },
    beforeDestroy() {
      window.removeEventListener('hashchange', this.syncRoute);
    },
    methods: {
      routeKeyFromHash() {
        const hash = window.location.hash.replace(/^#\/?/, '');
        return hash.split('/')[0] || admin.defaultRoute;
      },
      syncRoute() {
        const key = this.routeKeyFromHash();
        const menu = this.menus.find((item) => item.key === key);
        if (!menu) {
          this.currentKey = admin.defaultRoute;
          window.location.hash = `#/${admin.defaultRoute}`;
          return;
        }

        this.currentKey = menu.key;
        if (!window.location.hash && window.history && window.history.replaceState) {
          window.history.replaceState(null, '', `${window.location.pathname}${window.location.search}${menu.hash}`);
        }
      },
      navigate(key) {
        const menu = this.menus.find((item) => item.key === key);
        if (!menu) return;
        if (window.location.hash !== menu.hash) {
          window.location.hash = menu.hash;
        }
      },
      async logout() {
        try {
          await admin.requestJson('/api/auth/logout', { method: 'POST' });
        } finally {
          window.location.href = '/login';
        }
      },
    },
  });
})(window);
