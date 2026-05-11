(function () {
  function emptyForm() {
    return {
      id: null,
      username: '',
      password: '',
      enabled: true,
      expires_at: null,
    };
  }

  Vue.component('accounts-view', {
    template: `
      <div class="admin-view accounts-view">
        <el-card shadow="never" class="search-card">
          <el-form :inline="true" :model="searchForm" class="search-form" @submit.native.prevent>
            <el-form-item label="用户名">
              <el-input
                v-model.trim="searchForm.username"
                clearable
                placeholder="请输入用户名"
                @keyup.enter.native="queryAccounts">
              </el-input>
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="searchForm.status" clearable placeholder="全部状态">
                <el-option label="启用" value="enabled"></el-option>
                <el-option label="已禁用" value="disabled"></el-option>
                <el-option label="已过期" value="expired"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item class="search-actions">
              <el-button type="primary" icon="el-icon-search" @click="queryAccounts">查询</el-button>
              <el-button icon="el-icon-refresh-left" @click="resetSearch">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card shadow="never" class="table-card">
          <div class="table-toolbar">
            <div>
              <div class="table-title">账号列表</div>
            </div>
            <div class="toolbar-actions">
              <el-button type="primary" icon="el-icon-plus" @click="openCreateDialog">新增账号</el-button>
              <el-button type="success" icon="el-icon-document-checked" @click="syncPasswd">同步passwd</el-button>
            </div>
          </div>
          <div ref="tableArea" class="table-scroll">
            <el-table
              ref="accountTable"
              :data="items"
              :height="tableHeight"
              stripe
              border
              v-loading="loading"
              class="account-table">
              <el-table-column prop="username" label="用户名" min-width="150"></el-table-column>
              <el-table-column label="密码" min-width="220">
                <template slot-scope="scope">
                  <span class="password-mask">{{ visiblePasswords[scope.row.id] ? scope.row.password : '••••••••' }}</span>
                  <el-button type="text" size="mini" @click="togglePassword(scope.row)">
                    {{ visiblePasswords[scope.row.id] ? '隐藏' : '查看' }}
                  </el-button>
                </template>
              </el-table-column>
              <el-table-column label="状态" width="110">
                <template slot-scope="scope">
                  <el-tag :type="statusType(scope.row.status)" size="small">{{ statusText(scope.row.status) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="过期时间" min-width="170">
                <template slot-scope="scope">{{ formatDate(scope.row.expires_at, '不过期') }}</template>
              </el-table-column>
              <el-table-column label="更新时间" min-width="170">
                <template slot-scope="scope">{{ formatDate(scope.row.updated_at, '-') }}</template>
              </el-table-column>
              <el-table-column label="操作" width="250" fixed="right">
                <template slot-scope="scope">
                  <el-button size="mini" @click="openEditDialog(scope.row)">编辑</el-button>
                  <el-button size="mini" :type="scope.row.enabled ? 'warning' : 'success'" @click="setEnabled(scope.row)">
                    {{ scope.row.enabled ? '禁用' : '启用' }}
                  </el-button>
                  <el-button size="mini" type="danger" @click="deleteAccount(scope.row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div class="pagination-row">
            <el-pagination
              background
              layout="total, sizes, prev, pager, next"
              :current-page.sync="page"
              :page-size.sync="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="total"
              @current-change="loadAccounts"
              @size-change="handleSizeChange">
            </el-pagination>
          </div>
        </el-card>

        <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="520px" :close-on-click-modal="false">
          <el-form :model="form" :rules="rules" ref="accountForm" label-width="96px">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="form.username" placeholder="字母、数字、点、下划线或中划线"></el-input>
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input v-model="form.password" show-password placeholder="页面可查看密码"></el-input>
            </el-form-item>
            <el-form-item label="过期时间">
              <el-date-picker
                v-model="form.expires_at"
                type="datetime"
                value-format="yyyy-MM-ddTHH:mm:ss"
                placeholder="不选择表示不过期"
                style="width: 100%;">
              </el-date-picker>
            </el-form-item>
            <el-form-item label="启用状态">
              <el-switch v-model="form.enabled" active-text="启用" inactive-text="禁用"></el-switch>
            </el-form-item>
          </el-form>
          <span slot="footer" class="dialog-footer">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" :loading="saving" @click="saveAccount">保存</el-button>
          </span>
        </el-dialog>
      </div>
    `,
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
        form: emptyForm(),
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
      emptyForm,
      requestJson(url, options = {}) {
        return window.SquidAdmin.requestJson(url, options);
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
        this.form = emptyForm();
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
          if (!result) return;
          this.$message.success(`已同步 ${result.active_accounts} 个启用账号`);
        } catch (error) {
          this.$message.error(error.message);
        }
      },
    },
  });
})();
