new Vue({
  el: '#account-app',
  data() {
    return {
      loading: false,
      saving: false,
      page: 1,
      pageSize: 20,
      total: 0,
      items: [],
      tableHeight: 420,
      searchForm: {
        username: '',
        status: '',
      },
      visiblePasswords: {},
      dialogVisible: false,
      form: this.emptyForm(),
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { pattern: /^[A-Za-z0-9._-]{1,128}$/, message: '仅支持字母、数字、点、下划线或中划线', trigger: 'blur' },
        ],
        password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
      },
    };
  },
  computed: {
    dialogTitle() {
      return this.form.id ? `编辑账号：${this.form.username}` : '新增账号';
    },
  },
  mounted() {
    this.loadAccounts();
    this.updateTableHeight();
    window.addEventListener('resize', this.updateTableHeight);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.updateTableHeight);
  },
  methods: {
    emptyForm() {
      return {
        id: null,
        username: '',
        password: '',
        enabled: true,
        expires_at: null,
      };
    },
    async requestJson(url, options = {}) {
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
    },
    async loadAccounts() {
      this.loading = true;
      try {
        const params = new URLSearchParams({
          page: String(this.page),
          page_size: String(this.pageSize),
        });
        if (this.searchForm.username) params.set('username', this.searchForm.username);
        if (this.searchForm.status) params.set('status', this.searchForm.status);
        const payload = await this.requestJson(`/api/proxy-accounts?${params.toString()}`);
        if (!payload) return;
        this.total = payload.total;
        this.items = payload.items;
        this.$nextTick(this.updateTableHeight);
      } catch (error) {
        this.$message.error(error.message);
      } finally {
        this.loading = false;
      }
    },
    handleSizeChange(size) {
      this.pageSize = size;
      this.page = 1;
      this.loadAccounts();
    },
    queryAccounts() {
      this.page = 1;
      this.loadAccounts();
    },
    resetSearch() {
      this.searchForm = { username: '', status: '' };
      this.page = 1;
      this.loadAccounts();
    },
    updateTableHeight() {
      this.$nextTick(() => {
        const tableArea = this.$refs.tableArea;
        if (!tableArea) return;
        this.tableHeight = Math.max(tableArea.clientHeight, 260);
        this.$nextTick(() => {
          if (this.$refs.accountTable) this.$refs.accountTable.doLayout();
        });
      });
    },
    formatDate(value, emptyText) {
      if (!value) return emptyText;
      return value.replace('T', ' ').slice(0, 19);
    },
    statusText(status) {
      if (status === 'enabled') return '启用';
      if (status === 'expired') return '已过期';
      return '已禁用';
    },
    statusType(status) {
      if (status === 'enabled') return 'success';
      if (status === 'expired') return 'danger';
      return 'warning';
    },
    togglePassword(row) {
      this.$set(this.visiblePasswords, row.id, !this.visiblePasswords[row.id]);
    },
    openCreateDialog() {
      this.form = this.emptyForm();
      this.dialogVisible = true;
      this.$nextTick(() => this.$refs.accountForm && this.$refs.accountForm.clearValidate());
    },
    openEditDialog(row) {
      this.form = {
        id: row.id,
        username: row.username,
        password: row.password,
        enabled: row.enabled,
        expires_at: row.expires_at ? row.expires_at.slice(0, 19) : null,
      };
      this.dialogVisible = true;
      this.$nextTick(() => this.$refs.accountForm && this.$refs.accountForm.clearValidate());
    },
    async saveAccount() {
      this.$refs.accountForm.validate(async (valid) => {
        if (!valid) return;
        this.saving = true;
        const payload = {
          username: this.form.username.trim(),
          password: this.form.password,
          enabled: this.form.enabled,
          expires_at: this.form.expires_at || null,
        };
        try {
          await this.requestJson(
            this.form.id ? `/api/proxy-accounts/${this.form.id}` : '/api/proxy-accounts',
            { method: this.form.id ? 'PUT' : 'POST', body: JSON.stringify(payload) },
          );
          this.dialogVisible = false;
          this.$message.success('保存成功');
          await this.loadAccounts();
        } catch (error) {
          this.$message.error(error.message);
        } finally {
          this.saving = false;
        }
      });
    },
    async setEnabled(row) {
      try {
        await this.requestJson(`/api/proxy-accounts/${row.id}/enabled`, {
          method: 'PATCH',
          body: JSON.stringify({ enabled: !row.enabled }),
        });
        this.$message.success(row.enabled ? '账号已禁用' : '账号已启用');
        await this.loadAccounts();
      } catch (error) {
        this.$message.error(error.message);
      }
    },
    async deleteAccount(row) {
      try {
        await this.$confirm(`确认删除账号 ${row.username}？`, '删除确认', {
          confirmButtonText: '删除',
          cancelButtonText: '取消',
          type: 'warning',
        });
        await this.requestJson(`/api/proxy-accounts/${row.id}`, { method: 'DELETE' });
        this.$message.success('删除成功');
        await this.loadAccounts();
      } catch (error) {
        if (error !== 'cancel') this.$message.error(error.message || '删除失败');
      }
    },
    async syncPasswd() {
      try {
        const result = await this.requestJson('/api/proxy-accounts/sync-passwd', { method: 'POST' });
        this.$message.success(`已同步 ${result.active_accounts} 个启用账号`);
      } catch (error) {
        this.$message.error(error.message);
      }
    },
    async logout() {
      await this.requestJson('/api/auth/logout', { method: 'POST' });
      window.location.href = '/login';
    },
  },
});
